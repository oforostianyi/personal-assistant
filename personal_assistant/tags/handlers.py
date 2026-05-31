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


def _replace_tag(state, old_value: str, new_value: str) -> tuple[int, int]:
    """Replace old_value with new_value across contacts and notes."""
    contacts_affected = 0
    notes_affected = 0

    for record in _book_values(getattr(state, "contacts", None)):
        tags = getattr(record, "tags", None)
        if tags is None:
            continue
        if not any(getattr(tag, "value", None) == old_value for tag in tags):
            continue

        kept = [
            tag
            for tag in tags
            if getattr(tag, "value", None) != old_value
        ]
        if not any(getattr(tag, "value", None) == new_value for tag in kept):
            kept.append(Tag(new_value))
        record.tags = kept
        contacts_affected += 1

    for note in _book_values(getattr(state, "notes", None)):
        tags = getattr(note, "tags", None)
        if tags is None:
            continue
        if not any(getattr(tag, "value", None) == old_value for tag in tags):
            continue

        kept = [
            tag
            for tag in tags
            if getattr(tag, "value", None) != old_value
        ]
        if not any(getattr(tag, "value", None) == new_value for tag in kept):
            kept.append(Tag(new_value))
        note.tags = kept

        touch = getattr(note, "touch", None)
        if callable(touch):
            touch()
        notes_affected += 1

    return contacts_affected, notes_affected


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


@command(
    "rename-tag",
    format="<old> <new>",
    aliases=("tag-rename",),
    help_="Rename a tag everywhere across contacts and notes.",
)
@input_error
def rename_tag(args, state):
    if len(args) < 2:
        raise ValueError("Usage: rename-tag <old> <new>")

    old_value = Tag(args[0]).value
    new_value = Tag(args[1]).value
    if old_value == new_value:
        return f"Nothing to do: '{old_value}' is the same as '{new_value}'."

    contacts_affected, notes_affected = _replace_tag(state, old_value, new_value)
    if contacts_affected == 0 and notes_affected == 0:
        return f"No items tagged '{old_value}'."

    contact_word = "contacts" if contacts_affected != 1 else "contact"
    note_word = "notes" if notes_affected != 1 else "note"
    return (
        f"Renamed '{old_value}' -> '{new_value}'. "
        f"Affected: {contacts_affected} {contact_word}, "
        f"{notes_affected} {note_word}."
    )


@command(
    "merge-tags",
    format="<t1> <t2>",
    aliases=("tags-merge",),
    help_="Merge <t1> into <t2> across contacts and notes.",
)
@input_error
def merge_tags(args, state):
    if len(args) < 2:
        raise ValueError("Usage: merge-tags <t1> <t2>")

    source_value = Tag(args[0]).value
    target_value = Tag(args[1]).value
    if source_value == target_value:
        raise ValueError("Cannot merge a tag with itself.")

    contacts_affected, notes_affected = _replace_tag(
        state,
        source_value,
        target_value,
    )
    if contacts_affected == 0 and notes_affected == 0:
        return f"No items tagged '{source_value}'. Nothing merged."

    total = len(_records_with_tag(state, target_value)) + len(
        _notes_with_tag(state, target_value)
    )
    usage_word = "usages" if total != 1 else "usage"
    return (
        f"Merged '{source_value}' into '{target_value}'. "
        f"Now '{target_value}' has {total} {usage_word}."
    )
