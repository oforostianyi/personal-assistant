"""Contacts module commands.

CTX_ROOT       : `contacts` — enter the module (+ global birthdays/search).
CTX_CONTACTS   : list / sort / find / filter / new.
CTX_CONTACT    : show / notes / edit / delete.

`create_contact_from_input` is the shared creation path for `new <name>`
and the entity-enter fallback, so the logic is not duplicated.
"""

from __future__ import annotations

from personal_assistant.contacts.book import _VALID_SORT_FIELDS
from personal_assistant.contacts.fields import Name
from personal_assistant.contacts.record import Record
from personal_assistant.core.decorators import input_error
from personal_assistant.core.registry import (
    CTX_CONTACT,
    CTX_CONTACTS,
    CTX_NOTES,
    CTX_ROOT,
    command,
)
from personal_assistant.ui.views import (
    render_contact_card,
    render_contacts_table,
    render_notes_table,
)


# All interactive `edit` menus read extra input via input() in the handler
# body. The hw-08 rule "I/O only in main.py" is intentionally relaxed here:
# otherwise any two-step edit would need separate commands (edit-name-prompt,
# edit-name-set), which is worse UX.
def _ask(prompt: str) -> str | None:
    """Read a line; return None on EOF/Ctrl-C (== cancel)."""
    try:
        return input(prompt)
    except (EOFError, KeyboardInterrupt):
        print()
        return None


# --- root: enter --------------------------------------------------------------


@command(
    "contacts",
    context=CTX_ROOT,
    help_text="Enter the contacts module.",
)
@input_error
def enter_contacts(_args, state):
    state.enter_module("contacts")
    return ""


# --- shared creation path -----------------------------------------------------


@input_error
def create_contact_from_input(query: str, state) -> str:
    """Create a new contact and enter it.

    Shared path for `new <name>` and the entity-enter fallback. The contact
    card is shown by the dispatcher's auto-show after this returns (the
    state.entity_key changed).
    """
    record = Record(query)
    if state.contacts.find(record.name.value) is not None:
        raise ValueError(f"Contact '{record.name.value}' already exists.")
    state.contacts.add_record(record)
    state.enter_entity(record.name.value)
    return f"Created contact '{record.name.value}'."


# --- contacts: list / sort / find / filter / new -----------------------------


@command(
    "list",
    context=CTX_CONTACTS,
    help_text="List all contacts.",
)
@input_error
def list_contacts(_args, state):
    if not state.contacts.data:
        return "Contacts book is empty."
    field, reverse = state.contacts_sort
    return render_contacts_table(state.contacts.sorted_by(field, reverse))


@command(
    "sort",
    context=CTX_CONTACTS,
    format="<field> [asc|desc]",
    help_text="Set the sort key for `list`.",
)
@input_error
def sort_contacts(args, state):
    if not args:
        raise ValueError(
            f"Usage: sort <field> [asc|desc]. Fields: {', '.join(_VALID_SORT_FIELDS)}."
        )
    field = args[0].lower()
    if field not in _VALID_SORT_FIELDS:
        raise ValueError(
            f"Unknown sort field '{field}'. Try: {', '.join(_VALID_SORT_FIELDS)}."
        )
    direction = args[1].lower() if len(args) > 1 else "asc"
    if direction not in ("asc", "desc"):
        raise ValueError("Direction must be 'asc' or 'desc'.")
    state.contacts_sort = (field, direction == "desc")
    return f"Sort: {field} {direction}"


@command(
    "find",
    context=CTX_CONTACTS,
    format="<query>",
    help_text="Substring search across name, phone, email, address, tags.",
)
@input_error
def find_contacts(args, state):
    if not args:
        raise ValueError("Usage: find <query>")
    query = " ".join(args)
    results = state.contacts.search(query)
    if not results:
        return f"No contacts matching '{query}'."
    return render_contacts_table(results)


@command(
    "filter",
    context=CTX_CONTACTS,
    format="tag <tag>",
    help_text="Filter contacts by tag.",
)
@input_error
def filter_contacts(args, state):
    if not args or args[0].lower() != "tag":
        raise ValueError("Usage: filter tag <tag>")
    if len(args) < 2:
        raise ValueError("Usage: filter tag <tag>")
    tag = args[1]
    results = state.contacts.search_by_tag(tag)
    if not results:
        return f"No contacts tagged '{tag.lstrip('#').lower()}'."
    return render_contacts_table(results)


@command(
    "new",
    context=CTX_CONTACTS,
    format="<name>",
    help_text="Create a new contact and enter it.",
)
@input_error
def new_contact(args, state):
    if not args:
        raise ValueError("Usage: new <name>")
    name = " ".join(args)
    return create_contact_from_input(name, state)


# --- contact entity: show / notes / delete -----------------------------------


@command(
    "show",
    context=CTX_CONTACT,
    help_text="Show details for the current contact.",
)
@input_error
def show_contact(_args, state):
    record = state.contacts.find(state.entity_key)
    if record is None:
        raise KeyError(state.entity_key)
    return render_contact_card(record)


@command(
    "notes",
    context=CTX_CONTACT,
    help_text="List notes linked to this contact.",
)
@input_error
def contact_notes(_args, state):
    record = state.contacts.find(state.entity_key)
    if record is None:
        raise KeyError(state.entity_key)
    finder = getattr(state.notes, "find_by_uuid", None)
    if finder is None or not record.linked_note_ids:
        return "Notes module not ready yet." if finder is None else "No linked notes."
    linked = [finder(uid) for uid in record.linked_note_ids]
    linked = [n for n in linked if n is not None]
    return render_notes_table(linked) if linked else "No linked notes."


# --- edit -------------------------------------------------------------------

_FIELD_LABELS = ("name", "phone", "email", "address", "birthday", "tags")


def _phones_summary(record: Record) -> str:
    if not record.phones:
        return "—"
    first = record.phones[0].value
    if len(record.phones) > 1:
        return f"{first} (+{len(record.phones) - 1} more)"
    return first


def _print_main_menu(record: Record) -> None:
    print("What to edit?")
    print(f"  1) name      {record.name.value}")
    print(f"  2) phone     {_phones_summary(record)}")
    print(f"  3) email     {record.email.value if record.email else '—'}")
    print(f"  4) address   {record.address.value if record.address else '—'}")
    print(f"  5) birthday  {record.birthday if record.birthday else '—'}")
    print(
        f"  6) tags      "
        f"{', '.join(t.value for t in record.tags) if record.tags else '—'}"
    )
    print("  0) cancel")


def _rename_contact(record: Record, new_name: str, state) -> str:
    new_name = new_name.strip()
    if not new_name:
        raise ValueError("Name cannot be empty.")
    if new_name == record.name.value:
        return "(unchanged)"
    if state.contacts.find(new_name) is not None:
        raise ValueError(f"Contact '{new_name}' already exists.")
    old_name = record.name.value
    record.name = Name(new_name)
    # UserDict preserves insertion order; rebuild dict to keep position.
    state.contacts.data = {
        (new_name if k == old_name else k): v for k, v in state.contacts.data.items()
    }
    state.entity_key = new_name
    return f"✓ Renamed: '{old_name}' → '{new_name}'."


def _prompt_name(record: Record, state) -> str:
    new = _ask(f"Name [{record.name.value}]: ")
    if new is None:
        return "Cancelled."
    new = new.strip()
    if not new:
        return "(unchanged)"
    return _rename_contact(record, new, state)


def _single_value_prompt(record: Record, field: str) -> str:
    current = ""
    if field == "email" and record.email:
        current = record.email.value
    elif field == "address" and record.address:
        current = record.address.value
    elif field == "birthday" and record.birthday:
        current = str(record.birthday)
    new = _ask(f"{field.capitalize()} [{current}]: ")
    if new is None:
        return "Cancelled."
    new = new.strip()
    if not new:
        return "(unchanged)"
    if new == "-":
        if field == "email":
            record.clear_email()
        elif field == "address":
            record.clear_address()
        elif field == "birthday":
            record.birthday = None
        return "✓ Cleared."
    if field == "email":
        record.set_email(new)
    elif field == "address":
        record.set_address(new)
    elif field == "birthday":
        record.add_birthday(new)
    return "✓ Updated."


def _phone_submenu(record: Record) -> str:
    for _ in range(4):
        print(f"Phones for {record.name.value}:")
        for i, p in enumerate(record.phones, 1):
            print(f"  {i}) {p.value}")
        print(f"  {len(record.phones) + 1}) + add new")
        print("  0) back")
        choice = _ask("> ")
        if choice is None:
            return "Cancelled."
        choice = choice.strip()
        if choice in ("", "0"):
            return "(done)"
        if not choice.isdigit():
            print(f"Invalid choice '{choice}'. Try again.")
            continue
        n = int(choice)
        if n == len(record.phones) + 1:
            new = _ask("New phone: ")
            if new is None or not new.strip():
                continue
            try:
                record.add_phone(new.strip())
                print("✓ Added.")
            except ValueError as e:
                print(f"Error: {e}")
            continue
        if 1 <= n <= len(record.phones):
            phone = record.phones[n - 1]
            action = _ask(f"({phone.value}) edit/remove/back: ")
            if action is None:
                return "Cancelled."
            action = action.strip().lower()
            if action.startswith("e"):
                new = _ask(f"New value for {phone.value}: ")
                if new is None or not new.strip():
                    continue
                try:
                    record.edit_phone(phone.value, new.strip())
                    print("✓ Updated.")
                except ValueError as e:
                    print(f"Error: {e}")
            elif action.startswith("r"):
                record.remove_phone(phone.value)
                print(f"✓ Removed '{phone.value}'.")
            continue
        print(f"Invalid choice '{choice}'. Try again.")
    return "Too many invalid choices."


def _phone_shortcut(record: Record, args: list[str]) -> str:
    op = args[0].lower()
    rest = args[1:]
    if op == "add":
        if not rest:
            raise ValueError("Usage: edit phone add <number>")
        record.add_phone(rest[0])
        return "✓ Added."
    if op == "remove":
        if not rest:
            raise ValueError("Usage: edit phone remove <number>")
        record.remove_phone(rest[0])
        return f"✓ Removed '{rest[0]}'."
    if op == "edit":
        if len(rest) < 2:
            raise ValueError("Usage: edit phone edit <old> <new>")
        record.edit_phone(rest[0], rest[1])
        return "✓ Updated."
    raise ValueError(f"Unknown phone op '{op}'. Try: add, remove, edit.")


def _tags_submenu(record: Record) -> str:
    for _ in range(4):
        print(f"Tags for {record.name.value}:")
        if record.tags:
            for i, t in enumerate(record.tags, 1):
                print(f"  {i}) {t.value}")
        else:
            print("  (no tags)")
        print("  a) add")
        print("  r) remove (by number)")
        print("  0) back")
        choice = _ask("> ")
        if choice is None:
            return "Cancelled."
        choice = choice.strip().lower()
        if choice in ("", "0"):
            return "(done)"
        if choice == "a":
            new = _ask("New tag: ")
            if new is None or not new.strip():
                continue
            try:
                record.add_tag(new.strip())
                print("✓ Added.")
            except ValueError as e:
                print(f"Error: {e}")
            continue
        if choice == "r":
            if not record.tags:
                print("Nothing to remove.")
                continue
            n_str = _ask("Number to remove: ")
            if n_str is None or not n_str.strip().isdigit():
                continue
            idx = int(n_str.strip())
            if 1 <= idx <= len(record.tags):
                value = record.tags[idx - 1].value
                record.remove_tag(value)
                print(f"✓ Removed '{value}'.")
            else:
                print("Out of range.")
            continue
        print(f"Invalid choice '{choice}'.")
    return "Too many invalid choices."


def _tags_shortcut(record: Record, args: list[str]) -> str:
    op = args[0].lower()
    rest = args[1:]
    if op == "add":
        if not rest:
            raise ValueError("Usage: edit tags add <tag>")
        record.add_tag(rest[0])
        return f"✓ Added '{rest[0].lstrip('#').lower()}'."
    if op == "remove":
        if not rest:
            raise ValueError("Usage: edit tags remove <tag>")
        record.remove_tag(rest[0])
        return f"✓ Removed '{rest[0].lstrip('#').lower()}'."
    raise ValueError(f"Unknown tags op '{op}'. Try: add, remove.")


@command(
    "edit",
    context=CTX_CONTACT,
    format="[<field> [args...]]",
    help_text="Edit contact fields. Without args opens an interactive menu.",
)
@input_error
def edit_contact(args, state):
    record = state.contacts.find(state.entity_key)
    if record is None:
        raise KeyError(state.entity_key)

    if not args:
        for _ in range(4):
            _print_main_menu(record)
            choice = _ask("> ")
            if choice is None:
                return "Cancelled."
            choice = choice.strip()
            if choice in ("", "0"):
                return "Cancelled."
            if choice == "1":
                return _prompt_name(record, state)
            if choice == "2":
                return _phone_submenu(record)
            if choice == "3":
                return _single_value_prompt(record, "email")
            if choice == "4":
                return _single_value_prompt(record, "address")
            if choice == "5":
                return _single_value_prompt(record, "birthday")
            if choice == "6":
                return _tags_submenu(record)
            print(f"Invalid choice '{choice}'. Try again.")
        return "Too many invalid choices."

    field = args[0].lower()
    rest = args[1:]

    if field == "name":
        if rest:
            return _rename_contact(record, " ".join(rest), state)
        return _prompt_name(record, state)
    if field in ("email", "address"):
        if rest:
            value = " ".join(rest)
            if field == "email":
                record.set_email(value)
            else:
                record.set_address(value)
            return "✓ Updated."
        return _single_value_prompt(record, field)
    if field == "birthday":
        if rest:
            record.add_birthday(rest[0])
            return "✓ Updated."
        return _single_value_prompt(record, "birthday")
    if field == "phone":
        if rest:
            return _phone_shortcut(record, rest)
        return _phone_submenu(record)
    if field == "tags":
        if rest:
            return _tags_shortcut(record, rest)
        return _tags_submenu(record)
    raise ValueError(f"Unknown field '{field}'. Try: {', '.join(_FIELD_LABELS)}.")


# --- cross-cutting commands (registered in multiple contexts) ----------------

_WEEKDAYS = (
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
)


def _weekday_name(date_str: str) -> str:
    """`date_str` in DD.MM.YYYY → English weekday name.

    Locale-independent: we don't rely on strftime("%A"), which depends on
    the system locale.
    """
    from datetime import datetime

    return _WEEKDAYS[datetime.strptime(date_str, "%d.%m.%Y").weekday()]


@command(
    "birthdays",
    context=CTX_ROOT,
    format="[days]",
    help_text="Show upcoming birthdays (default: next 7 days).",
)
@command(
    "birthdays",
    context=CTX_CONTACTS,
    format="[days]",
    help_text="Show upcoming birthdays (default: next 7 days).",
)
@input_error
def birthdays_cmd(args, state):
    days = 7
    if args:
        try:
            days = int(args[0])
        except ValueError:
            raise ValueError("Days must be a number.")
        if days < 0:
            raise ValueError("Days must be non-negative.")
    upcoming = state.contacts.get_upcoming_birthdays(days)
    if not upcoming:
        return f"No birthdays in the next {days} days."
    from io import StringIO

    from rich.console import Console
    from rich.table import Table

    table = Table(show_header=True, header_style="bold")
    table.add_column("Name")
    table.add_column("Congratulation date")
    table.add_column("Weekday")
    for item in upcoming:
        table.add_row(
            item["name"],
            item["congratulation_date"],
            _weekday_name(item["congratulation_date"]),
        )
    buf = StringIO()
    Console(file=buf, force_terminal=False, width=120).print(table)
    return buf.getvalue().rstrip("\n")


@command(
    "search",
    context=CTX_ROOT,
    format="<query>",
    help_text="Search both contacts and notes for a query.",
)
@command(
    "search",
    context=CTX_CONTACTS,
    format="<query>",
    help_text="Search both contacts and notes for a query.",
)
@command(
    "search",
    context=CTX_NOTES,
    format="<query>",
    help_text="Search both contacts and notes for a query.",
)
@input_error
def search_cmd(args, state):
    if not args:
        raise ValueError("Usage: search <query>")
    query = " ".join(args)
    contacts_results = state.contacts.search(query)
    notes_results = state.notes.search(query)
    parts: list[str] = []
    parts.append(f"Contacts ({len(contacts_results)}):")
    parts.append(
        render_contacts_table(contacts_results) if contacts_results else "  (none)"
    )
    parts.append("")
    parts.append(f"Notes ({len(notes_results)}):")
    parts.append(render_notes_table(notes_results) if notes_results else "  (none)")
    return "\n".join(parts)


@command(
    "delete",
    context=CTX_CONTACT,
    help_text="Delete this contact (with confirmation).",
)
@input_error
def delete_contact(_args, state):
    name = state.entity_key
    try:
        ans = input(f"Delete '{name}'? (y/N): ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return "Cancelled."
    if ans not in ("y", "yes"):
        return "Cancelled."
    record = state.contacts.find(name)
    if record is None:
        raise KeyError(name)
    # Unlink from any linked notes (no-op if notes module isn't wired yet).
    finder = getattr(state.notes, "find_by_uuid", None)
    if finder is not None:
        for uid in list(record.linked_note_ids):
            note = finder(uid)
            if note is not None:
                note.unlink_contact(name)
    state.contacts.delete(name)
    state.go_up()
    return f"Deleted '{name}'."
