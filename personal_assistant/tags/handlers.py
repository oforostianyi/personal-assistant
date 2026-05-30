"""Tag commands for the flat command registry."""

from __future__ import annotations

from personal_assistant.contacts.fields import Tag
from personal_assistant.core.decorators import input_error
from personal_assistant.core.registry import command
from personal_assistant.tags.aggregator import TagInfo, collect_tags


def _render_tag_list(infos: list[TagInfo]) -> str:
    """Render tag usage counts as a plain text table."""
    if not infos:
        return "No tags yet."

    headers = ("Tag", "Contacts", "Notes", "Total")
    rows = [
        (info.name, str(info.contact_count), str(info.note_count), str(info.total))
        for info in infos
    ]
    widths = [
        max(len(header), *(len(row[index]) for row in rows))
        for index, header in enumerate(headers)
    ]

    def line(cells: tuple[str, ...]) -> str:
        return "  ".join(
            cells[index].ljust(widths[index])
            for index in range(len(headers))
        )

    return "\n".join([line(headers), *(line(row) for row in rows)])


def _render_find_result(tag_name: str, contacts: list, notes: list) -> str:
    """Render contacts and notes carrying a tag."""
    parts: list[str] = [f"Contacts ({len(contacts)}):"]

    if contacts:
        for record in contacts:
            phones = "; ".join(getattr(phone, "value", str(phone)) for phone in record.phones)
            parts.append(f"  {record.name.value} ({phones or 'no phones'})")
    else:
        parts.append("  (none)")

    parts.append(f"Notes ({len(notes)}):")
    if notes:
        for note in notes:
            uid = getattr(note, "id", None)
            uid_short = uid.hex[:8] if uid is not None else "-"
            text = " ".join((getattr(note, "text", "") or "").split())
            preview = text if len(text) <= 60 else text[:57] + "..."
            parts.append(f"  [{uid_short}] {preview}")
    else:
        parts.append("  (none)")

    return "\n".join(parts)


def _book_values(book):
    """Iterate values from a UserDict-backed book, plain dict, or iterable."""
    if book is None:
        return ()

    data = getattr(book, "data", None)
    if data is not None:
        return data.values()

    if isinstance(book, dict):
        return book.values()

    return book


def _records_with_tag(state, tag_value: str) -> list:
    records = []
    for record in _book_values(getattr(state, "contacts", None)):
        tags = getattr(record, "tags", None) or ()
        if any(getattr(tag, "value", None) == tag_value for tag in tags):
            records.append(record)
    return records


def _notes_with_tag(state, tag_value: str) -> list:
    notes = []
    for note in _book_values(getattr(state, "notes", None)):
        tags = getattr(note, "tags", None) or ()
        if any(getattr(tag, "value", None) == tag_value for tag in tags):
            notes.append(note)
    return notes


@command(
    "list-tags",
    aliases=("tags-list",),
    help_="List all tags with usage counts.",
)
@input_error
def list_tags(_args, state):
    return _render_tag_list(collect_tags(state))


@command(
    "sort-by-tag",
    aliases=("tags-sort",),
    help_="List tags sorted by total usage.",
)
@input_error
def sort_by_tag(_args, state):
    infos = sorted(collect_tags(state), key=lambda info: (-info.total, info.name))
    return _render_tag_list(infos)


@command(
    "find-by-tag",
    format="<tag>",
    aliases=("tag-find",),
    help_="Show contacts and notes that use the given tag.",
)
@input_error
def find_by_tag(args, state):
    if not args:
        raise ValueError("Usage: find-by-tag <tag>")

    tag_value = Tag(args[0]).value
    contacts = _records_with_tag(state, tag_value)
    notes = _notes_with_tag(state, tag_value)
    if not contacts and not notes:
        return f"Nothing tagged '{tag_value}'."
    return _render_find_result(tag_value, contacts, notes)
