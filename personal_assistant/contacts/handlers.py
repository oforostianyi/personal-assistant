"""Contacts module commands (flat command registry).

All handlers return a single string. Validators in record.py / fields.py raise
ValueError with a human-readable message; @input_error catches that and returns
the message to the user.

Commands registered:
  add-contact <name> <phone>
  edit-contact <name> <field> <value>     # field: phone|email|address|birthday|tag
  delete-contact <name>
  find-contact <query>
  list-contacts
  birthdays [days]

Until ui/tables.py (Card 13) lands, list rendering uses an inline simple text
table. After Card 13 merges, refactor list-contacts and birthdays to call
ui.tables.render_contacts_table / ui.tables.render_birthdays_table.
"""

from __future__ import annotations

from personal_assistant.contacts.book import ContactsBook
from personal_assistant.contacts.record import Record
from personal_assistant.core.decorators import input_error
from personal_assistant.core.registry import command


# --- inline rendering helpers (replaced by ui.tables after Card 13) ----------

def _truncate(s: str, n: int = 60) -> str:
    return s if len(s) <= n else s[: n - 1] + "…"


def _render_contacts_text_table(records) -> str:
    records = list(records)
    if not records:
        return "(no contacts)"
    header = f"{'Name':<20} {'Phone':<14} {'Email':<28} {'Birthday':<11} {'Tags':<20}"
    sep = "-" * len(header)
    lines = [header, sep]
    for r in records:
        phone = r.phones[0].value if r.phones else "—"
        email = r.email.value if r.email else "—"
        birthday = str(r.birthday) if r.birthday else "—"
        tags = ", ".join(t.value for t in r.tags) if r.tags else "—"
        lines.append(
            f"{_truncate(r.name.value, 20):<20} "
            f"{phone:<14} "
            f"{_truncate(email, 28):<28} "
            f"{birthday:<11} "
            f"{_truncate(tags, 20):<20}"
        )
    return "\n".join(lines)


def _render_birthdays_text_table(items: list[dict]) -> str:
    if not items:
        return "(no upcoming birthdays)"
    header = f"{'Name':<20} {'Congratulation date':<22} {'Weekday':<10}"
    sep = "-" * len(header)
    lines = [header, sep]
    from datetime import datetime
    weekdays = ("Monday", "Tuesday", "Wednesday", "Thursday",
                "Friday", "Saturday", "Sunday")
    for item in items:
        dt = datetime.strptime(item["congratulation_date"], "%d.%m.%Y")
        wd = weekdays[dt.weekday()]
        lines.append(
            f"{_truncate(item['name'], 20):<20} "
            f"{item['congratulation_date']:<22} "
            f"{wd:<10}"
        )
    return "\n".join(lines)


# --- commands ---------------------------------------------------------------

@command(
    "add-contact",
    format="<name> <phone>",
    help_="Create a new contact with one phone.",
)
@input_error
def add_contact(args, state):
    if len(args) < 2:
        raise ValueError("Usage: add-contact <name> <phone>")
    name, phone = args[0], args[1]
    if not isinstance(state.contacts, ContactsBook):
        state.contacts = ContactsBook()
    if state.contacts.find(name) is not None:
        raise ValueError(f"Contact '{name}' already exists. Use edit-contact to update.")
    record = Record(name)
    record.add_phone(phone)
    state.contacts.add_record(record)
    return f"✓ Contact '{name}' added."


@command(
    "edit-contact",
    format="<name> <field> <value>",
    help_="Set or replace a field. field: phone | email | address | birthday | tag.",
)
@input_error
def edit_contact(args, state):
    if len(args) < 3:
        raise ValueError("Usage: edit-contact <name> <field> <value>")
    name, field = args[0], args[1].lower()
    value = " ".join(args[2:])
    record = state.contacts.find(name)
    if record is None:
        raise KeyError(name)
    if field == "phone":
        # If contact already has phones, edit the first one. Otherwise add.
        if record.phones:
            record.edit_phone(record.phones[0].value, value)
        else:
            record.add_phone(value)
        return f"✓ Phone updated for '{name}'."
    if field == "email":
        record.set_email(value)
        return f"✓ Email updated for '{name}'."
    if field == "address":
        record.set_address(value)
        return f"✓ Address updated for '{name}'."
    if field == "birthday":
        record.add_birthday(value)
        return f"✓ Birthday set for '{name}'."
    if field == "tag":
        record.add_tag(value)
        return f"✓ Tag '{value.lstrip('#').lower()}' added to '{name}'."
    raise ValueError(
        f"Unknown field '{field}'. Try: phone, email, address, birthday, tag."
    )


@command(
    "delete-contact",
    format="<name>",
    help_="Remove a contact.",
)
@input_error
def delete_contact(args, state):
    if not args:
        raise ValueError("Usage: delete-contact <name>")
    name = " ".join(args)
    state.contacts.delete(name)
    return f"✓ Contact '{name}' deleted."


@command(
    "find-contact",
    format="<query>",
    help_="Substring search across name, phone, email, address, tags.",
)
@input_error
def find_contact(args, state):
    if not args:
        raise ValueError("Usage: find-contact <query>")
    query = " ".join(args)
    results = state.contacts.search(query)
    if not results:
        return f"No contacts matching '{query}'."
    return _render_contacts_text_table(results)


@command(
    "list-contacts",
    help_="List all contacts.",
)
@input_error
def list_contacts(_args, state):
    if not state.contacts or not getattr(state.contacts, "data", {}):
        return "Contacts book is empty."
    records = state.contacts.sorted_by("name") if hasattr(state.contacts, "sorted_by") else list(state.contacts.data.values())
    return _render_contacts_text_table(records)


@command(
    "birthdays",
    format="[days]",
    help_="Upcoming birthdays in the next N days (default 7).",
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
    if not hasattr(state.contacts, "get_upcoming_birthdays"):
        return "Contacts book is empty."
    upcoming = state.contacts.get_upcoming_birthdays(days)
    if not upcoming:
        return f"No birthdays in the next {days} days."
    return _render_birthdays_text_table(upcoming)