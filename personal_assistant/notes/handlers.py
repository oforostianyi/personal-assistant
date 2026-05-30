"""Flat-style REPL commands for the Notes domain."""

from __future__ import annotations

from typing import TYPE_CHECKING

from personal_assistant.core.decorators import input_error
from personal_assistant.core.registry import command
from personal_assistant.notes.book import NotesBook
from personal_assistant.notes.note import Note
from personal_assistant.notes.tagger import extract_tags
from personal_assistant.notes.text_parser import extract_phones, suggest_contacts

if TYPE_CHECKING:
    from personal_assistant.contacts.record import Record


def _ensure_notes(state) -> NotesBook:
    """Return state.notes as a NotesBook, upgrading empty dict state lazily."""
    if isinstance(state.notes, NotesBook):
        return state.notes
    if isinstance(state.notes, dict) and not state.notes:
        state.notes = NotesBook()
        return state.notes
    raise RuntimeError(
        "Notes storage is in an unexpected state. "
        "Ask the TL to apply the Card 09 integration step in app.py."
    )


def _known_tag_vocabulary(state) -> set[str]:
    """Collect tag slugs currently used by contacts and notes."""
    vocab: set[str] = set()

    contacts = getattr(state, "contacts", None)
    contact_data = getattr(contacts, "data", None) if contacts else None
    if contact_data:
        for record in contact_data.values():
            for tag in getattr(record, "tags", []):
                vocab.add(tag.value)

    notes = getattr(state, "notes", None)
    note_data = getattr(notes, "data", None) if notes else None
    if note_data:
        for note in note_data.values():
            for tag in note.tags:
                vocab.add(tag.value)

    return vocab


def _resolve_note(state, id_prefix: str) -> Note:
    """Resolve a note by UUID prefix or raise a user-facing lookup error."""
    note = _ensure_notes(state).find_by_id_prefix(id_prefix)
    if note is None:
        raise KeyError(id_prefix)
    return note


def _sync_link(record: "Record", note: Note) -> None:
    """Create a contact-note link on both sides."""
    record.link_note(note.id)
    note.link_contact(record.name.value)


def _sync_unlink(record: "Record", note: Note) -> None:
    """Remove a contact-note link from both sides."""
    record.unlink_note(note.id)
    note.unlink_contact(record.name.value)


def _render_notes_table(notes: list[Note]) -> str:
    """Render notes as a simple text table until Rich tables are available."""
    if not notes:
        return "No notes yet."

    header = f"{'ID':<10}{'TEXT':<62}{'TAGS':<16}{'LINKED'}"
    sep = f"{'-' * 8:<10}{'-' * 60:<62}{'-' * 14:<16}{'-' * 14}"
    lines = [header, sep]
    for note in notes:
        tags = ", ".join(tag.value for tag in note.tags) if note.tags else "-"
        linked = ", ".join(note.linked_contact_names) if note.linked_contact_names else "-"
        if len(tags) > 14:
            tags = tags[:13] + "..."
        if len(linked) > 30:
            linked = linked[:29] + "..."
        lines.append(
            f"{note.id_prefix():<10}{note.preview(60):<62}{tags:<16}{linked}"
        )
    return "\n".join(lines)


@command(
    "add-note",
    format="<text>",
    help_="Create a note. Auto-tags from #hashtags and known vocabulary.",
)
@input_error
def add_note(args, state):
    if not args:
        raise ValueError("Usage: add-note <text>")

    text = " ".join(args).strip()
    if not text:
        raise ValueError("Note text cannot be empty.")

    note = _ensure_notes(state).add_note(text)
    for slug in extract_tags(text, _known_tag_vocabulary(state)):
        note.add_tag(slug)

    contacts = getattr(state, "contacts", None)
    suggested: list[str] = []
    if contacts is not None and hasattr(contacts, "data"):
        suggested = suggest_contacts(text, contacts)

    phones = extract_phones(text)

    parts = [f"Note added. ID: {note.id_prefix()}."]
    if note.tags:
        parts.append("Tags: " + ", ".join(tag.value for tag in note.tags) + ".")
    if suggested:
        parts.append("Suggested links: " + ", ".join(suggested) + ".")
        parts.append(f"Use `link-note {note.id_prefix()} <name>` to confirm a link.")
    if phones:
        parts.append("Phones detected: " + ", ".join(phones) + ".")
    return "\n".join(parts)


@command(
    "edit-note",
    format="<id> <new text>",
    help_="Replace the text of a note. Tags and links are preserved.",
)
@input_error
def edit_note(args, state):
    if len(args) < 2:
        raise ValueError("Usage: edit-note <id> <new text>")

    id_prefix, *text_parts = args
    new_text = " ".join(text_parts).strip()
    if not new_text:
        raise ValueError("New text cannot be empty.")

    note = _resolve_note(state, id_prefix)
    note.set_text(new_text)
    return f"Note '{note.id_prefix()}' updated."


@command(
    "delete-note",
    format="<id>",
    help_="Delete a note. Also unlinks it from every contact it was linked to.",
)
@input_error
def delete_note(args, state):
    if not args:
        raise ValueError("Usage: delete-note <id>")

    note = _resolve_note(state, args[0])
    contacts = getattr(state, "contacts", None)
    if contacts is not None and hasattr(contacts, "data"):
        for name in list(note.linked_contact_names):
            record = contacts.find(name) if hasattr(contacts, "find") else None
            if record is None:
                record = contacts.data.get(name)
            if record is not None:
                _sync_unlink(record, note)

    _ensure_notes(state).delete(note.id)
    return f"Note '{note.id_prefix()}' deleted."


@command(
    "find-note",
    format="<query>",
    help_="Case-insensitive substring search across note text and tag slugs.",
)
@input_error
def find_note(args, state):
    if not args:
        raise ValueError("Usage: find-note <query>")

    query = " ".join(args)
    results = _ensure_notes(state).find_by_text(query)
    if not results:
        return f"No notes matching '{query}'."
    return _render_notes_table(results)


@command("list-notes", help_="Show all notes as a table.")
@input_error
def list_notes(_args, state):
    return _render_notes_table(_ensure_notes(state).list_all())


@command(
    "link-note",
    format="<id> <contact name>",
    help_="Link an existing note to an existing contact.",
)
@input_error
def link_note(args, state):
    if len(args) < 2:
        raise ValueError("Usage: link-note <id> <contact name>")

    id_prefix, *name_parts = args
    name = " ".join(name_parts).strip()
    if not name:
        raise ValueError("Contact name cannot be empty.")

    contacts = getattr(state, "contacts", None)
    if contacts is None or not hasattr(contacts, "data"):
        raise RuntimeError("Contacts module is not loaded.")

    record = contacts.find(name) if hasattr(contacts, "find") else None
    if record is None:
        record = contacts.data.get(name)
    if record is None:
        raise KeyError(name)

    note = _resolve_note(state, id_prefix)
    _sync_link(record, note)
    return f"Linked note '{note.id_prefix()}' to contact '{record.name.value}'."


@command(
    "unlink-note",
    format="<id> <contact name>",
    help_="Remove the link between a note and a contact.",
)
@input_error
def unlink_note(args, state):
    if len(args) < 2:
        raise ValueError("Usage: unlink-note <id> <contact name>")

    id_prefix, *name_parts = args
    name = " ".join(name_parts).strip()
    if not name:
        raise ValueError("Contact name cannot be empty.")

    contacts = getattr(state, "contacts", None)
    if contacts is None or not hasattr(contacts, "data"):
        raise RuntimeError("Contacts module is not loaded.")

    record = contacts.find(name) if hasattr(contacts, "find") else None
    if record is None:
        record = contacts.data.get(name)
    if record is None:
        raise KeyError(name)

    note = _resolve_note(state, id_prefix)
    _sync_unlink(record, note)
    return f"Unlinked note '{note.id_prefix()}' from contact '{record.name.value}'."
