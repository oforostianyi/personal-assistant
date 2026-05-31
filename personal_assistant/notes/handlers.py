"""Notes module commands.

CTX_ROOT  : `notes` — enter the module.
CTX_NOTES : list / sort / find / filter / new.
CTX_NOTE  : show / edit / rename / tag / untag / link / unlink / delete.

`create_note_from_input` is the shared creation path for the `new` command
and the entity-enter fallback (typing a note title at `notes>`). The user
never sees a UUID; the stable cross-contact reference is the UUID, so
renaming a note breaks nothing.
"""

from __future__ import annotations

from prompt_toolkit import PromptSession
from rapidfuzz import fuzz, process

from personal_assistant.core.decorators import input_error
from personal_assistant.core.registry import (
    CTX_NOTE,
    CTX_NOTES,
    CTX_ROOT,
    command,
)
from personal_assistant.notes.book import _VALID_SORT_FIELDS
from personal_assistant.notes.note import Note
from personal_assistant.notes.tagger import extract_hashtags, suggest_tags
from personal_assistant.notes.text_parser import (
    extract_phones,
    suggest_contacts,
)
from personal_assistant.ui.views import (
    render_note_card,
    render_notes_table,
)

# --- shared helpers --------------------------------------------------------

def _ask(prompt: str) -> str | None:
    try:
        return input(prompt)
    except (EOFError, KeyboardInterrupt):
        print()
        return None


def _read_multiline_body() -> str | None:
    """Read lines until a blank line (Enter on an empty line).

    Ctrl-C / EOF → None (cancel).
    """
    print("Text (blank line to finish, Ctrl+C to cancel):")
    lines: list[str] = []
    while True:
        try:
            line = input("> ")
        except (EOFError, KeyboardInterrupt):
            print()
            return None
        if line == "":
            break
        lines.append(line)
    return "\n".join(lines)


def _collect_known_tags(state) -> set[str]:
    """All tags already in the system (across both books)."""
    out: set[str] = set()
    for r in state.contacts.data.values():
        out.update(t.value for t in r.tags)
    for n in state.notes.data.values():
        out.update(t.value for t in n.tags)
    return out


def _create_note_with_body(title: str, state) -> str:
    """Shared flow: body, auto-tags, contact suggestion, enter the note."""
    body = _read_multiline_body()
    if body is None:
        return "Cancelled."

    note = Note(title=title, text=body)

    # Hashtags first — explicit user intent.
    for tag in extract_hashtags(body):
        try:
            note.add_tag(tag)
        except ValueError:
            pass

    # Suggested tags — only words that already exist as tags somewhere.
    known = _collect_known_tags(state)
    for tag in suggest_tags(body + " " + title, known):
        try:
            note.add_tag(tag)
        except ValueError:
            pass

    # Contact suggestions: first by phone (exact), then by name (fuzzy).
    # Keep first-appearance order, drop duplicates.
    suggested: list[str] = []
    phones_in_text = extract_phones(body + " " + title)
    if phones_in_text:
        for record in state.contacts.data.values():
            if any(p.value in phones_in_text for p in record.phones):
                if record.name.value not in suggested:
                    suggested.append(record.name.value)
    for name in suggest_contacts(body + " " + title, state.contacts):
        if name not in suggested:
            suggested.append(name)

    state.notes.add_note(note)
    state.enter_entity(note.title)

    msgs = [f"Created note '{note.title}'."]
    if note.tags:
        msgs.append(f"Auto tags: {', '.join(t.value for t in note.tags)}")
    if suggested:
        msgs.append(f"Suggested contacts: {', '.join(suggested)}")
        msgs.append("Tip: from inside this note, use 'link <name>'.")
    return "\n".join(msgs)


# --- root: enter module ---------------------------------------------------

@command(
    "notes",
    context=CTX_ROOT,
    help_text="Enter the notes module.",
)
@input_error
def enter_notes(_args, state):
    state.enter_module("notes")
    return ""


# --- shared creation path (entity-enter fallback uses this) ---------------

@input_error
def create_note_from_input(query: str, state) -> str:
    """Create a note titled `query` and run the body flow."""
    title = (query or "").strip()
    if not title:
        return "Cancelled."
    if state.notes.is_title_taken(title):
        raise ValueError(f"A note titled '{title}' already exists.")
    return _create_note_with_body(title, state)


# --- CTX_NOTES: list / sort / find / filter / new -------------------------

@command(
    "list",
    context=CTX_NOTES,
    help_text="List all notes.",
)
@input_error
def list_notes(_args, state):
    if not state.notes.data:
        return "Notes book is empty."
    field, reverse = state.notes_sort
    return render_notes_table(state.notes.sorted_by(field, reverse))


@command(
    "sort",
    context=CTX_NOTES,
    format="<field> [asc|desc]",
    help_text="Set the sort key for `list`.",
)
@input_error
def sort_notes(args, state):
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
    state.notes_sort = (field, direction == "desc")
    return f"Sort: {field} {direction}"


@command(
    "find",
    context=CTX_NOTES,
    format="<query>",
    help_text="Substring search across title and text.",
)
@input_error
def find_notes(args, state):
    if not args:
        raise ValueError("Usage: find <query>")
    query = " ".join(args)
    results = state.notes.search(query)
    if not results:
        return f"No notes matching '{query}'."
    return render_notes_table(results)


@command(
    "filter",
    context=CTX_NOTES,
    format="tag <tag> | contact <name>",
    help_text="Filter notes by tag or by linked contact.",
)
@input_error
def filter_notes(args, state):
    if not args or args[0].lower() not in ("tag", "contact"):
        raise ValueError("Usage: filter tag <tag> | filter contact <name>")
    kind = args[0].lower()
    if len(args) < 2:
        raise ValueError(f"Usage: filter {kind} <value>")
    value = " ".join(args[1:])
    if kind == "tag":
        results = state.notes.find_by_tag(value)
        empty = f"No notes tagged '{value.lstrip('#').lower()}'."
    else:
        results = state.notes.find_by_contact(value)
        empty = f"No notes linked to '{value}'."
    return render_notes_table(results) if results else empty


@command(
    "new",
    context=CTX_NOTES,
    format="[title]",
    help_text="Create a new note. Prompts for title if not given, then body.",
)
@input_error
def new_note(args, state):
    title = " ".join(args).strip() if args else ""
    if not title:
        got = _ask("Title: ")
        if got is None or not got.strip():
            return "Cancelled."
        title = got.strip()
    while state.notes.is_title_taken(title):
        print(f"A note titled '{title}' already exists. Try a different title.")
        got = _ask("Title: ")
        if got is None or not got.strip():
            return "Cancelled."
        title = got.strip()
    return _create_note_with_body(title, state)


# --- CTX_NOTE: show / edit / rename / tag / untag / link / unlink / delete ---

@command(
    "show",
    context=CTX_NOTE,
    help_text="Show this note.",
)
@input_error
def show_note(_args, state):
    note = state.notes.find_by_title(state.entity_key)
    if note is None:
        raise KeyError(state.entity_key)
    return render_note_card(note)


def _edit_text(initial: str) -> str | None:
    """Open multi-line editor. Returns new text or None if cancelled."""
    try:
        return PromptSession(multiline=True).prompt(
            "Edit (Esc Enter to save, Ctrl-C to cancel):\n",
            default=initial,
        )
    except KeyboardInterrupt:
        return None
    except EOFError:
        return None


@command(
    "edit",
    context=CTX_NOTE,
    help_text="Edit the note's body in a multi-line editor.",
)
@input_error
def edit_note(_args, state):
    note = state.notes.find_by_title(state.entity_key)
    if note is None:
        raise KeyError(state.entity_key)
    new_text = _edit_text(note.text)
    if new_text is None:
        return "Cancelled."
    note.set_text(new_text)
    # Re-run suggest_tags additively — manually-applied tags are never stripped.
    known = _collect_known_tags(state)
    for tag in suggest_tags(new_text + " " + note.title, known):
        try:
            note.add_tag(tag)
        except ValueError:
            pass
    return "✓ Updated."


@command(
    "rename",
    context=CTX_NOTE,
    format="<new title>",
    help_text="Rename this note.",
)
@input_error
def rename_note(args, state):
    if not args:
        raise ValueError("Usage: rename <new title>")
    new_title = " ".join(args).strip()
    if not new_title:
        raise ValueError("Note title cannot be empty.")
    state.notes.rename(state.entity_key, new_title)
    # `Note.set_title` already stripped; take it from the object.
    renamed = state.notes.find_by_title(new_title)
    state.entity_key = renamed.title if renamed else new_title
    return "✓ Renamed."


@command(
    "tag",
    context=CTX_NOTE,
    format="<tag>",
    help_text="Add a tag to this note.",
)
@input_error
def tag_note(args, state):
    if not args:
        raise ValueError("Usage: tag <tag>")
    note = state.notes.find_by_title(state.entity_key)
    if note is None:
        raise KeyError(state.entity_key)
    note.add_tag(args[0])
    return "✓ Tagged."


@command(
    "untag",
    context=CTX_NOTE,
    format="<tag>",
    help_text="Remove a tag from this note.",
)
@input_error
def untag_note(args, state):
    if not args:
        raise ValueError("Usage: untag <tag>")
    note = state.notes.find_by_title(state.entity_key)
    if note is None:
        raise KeyError(state.entity_key)
    note.remove_tag(args[0])
    return "✓ Untagged."


def _resolve_contact(name: str, state) -> str | None:
    """Exact case-insensitive first, then fuzzy (WRatio, cutoff=80)."""
    candidates = list(state.contacts.data.keys())
    if not candidates:
        return None
    name_low = name.lower()
    for k in candidates:
        if k.lower() == name_low:
            return k
    result = process.extractOne(
        name, candidates, scorer=fuzz.WRatio, score_cutoff=80,
    )
    return result[0] if result else None


@command(
    "link",
    context=CTX_NOTE,
    format="<contact>",
    help_text="Link a contact to this note (bidirectional).",
)
@input_error
def link_to_note(args, state):
    if not args:
        raise ValueError("Usage: link <contact>")
    query = " ".join(args)
    note = state.notes.find_by_title(state.entity_key)
    if note is None:
        raise KeyError(state.entity_key)
    resolved = _resolve_contact(query, state)
    if resolved is None:
        raise ValueError(f"Contact '{query}' not found.")
    record = state.contacts.find(resolved)
    note.link_contact(record.name.value)
    record.link_note(note.id)
    return f"✓ Linked '{record.name.value}'."


@command(
    "unlink",
    context=CTX_NOTE,
    format="<contact>",
    help_text="Unlink a contact from this note.",
)
@input_error
def unlink_from_note(args, state):
    if not args:
        raise ValueError("Usage: unlink <contact>")
    query = " ".join(args)
    note = state.notes.find_by_title(state.entity_key)
    if note is None:
        raise KeyError(state.entity_key)
    target = None
    q_low = query.lower()
    for n in note.linked_contact_names:
        if n.lower() == q_low:
            target = n
            break
    if target is None:
        raise ValueError(f"Contact '{query}' is not linked to this note.")
    note.unlink_contact(target)
    record = state.contacts.find(target)
    if record is not None:
        record.unlink_note(note.id)
    return f"✓ Unlinked '{target}'."


@command(
    "delete",
    context=CTX_NOTE,
    help_text="Delete this note (with confirmation).",
)
@input_error
def delete_note(_args, state):
    title = state.entity_key
    try:
        ans = input(f"Delete note '{title}'? (y/N): ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return "Cancelled."
    if ans not in ("y", "yes"):
        return "Cancelled."
    note = state.notes.find_by_title(title)
    if note is None:
        raise KeyError(title)
    for name in list(note.linked_contact_names):
        record = state.contacts.find(name)
        if record is not None:
            record.unlink_note(note.id)
    state.notes.delete_by_title(title)
    state.go_up()
    return f"✓ Deleted '{title}'."