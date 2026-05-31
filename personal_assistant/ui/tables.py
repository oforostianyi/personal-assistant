"""Rich-based renderers for tables and single-entity cards."""

from __future__ import annotations

from io import StringIO
from typing import TYPE_CHECKING, Iterable

from rich.console import Console
from rich.table import Table

if TYPE_CHECKING:
    from personal_assistant.contacts.record import Record
    from personal_assistant.notes.note import Note
    from personal_assistant.tags.aggregator import TagInfo


_TABLE_WIDTH = 120
_MAX_CELL = 60


def _render_to_string(table: Table) -> str:
    """Render a Rich table to a plain string without ANSI escapes."""
    buffer = StringIO()
    Console(file=buffer, force_terminal=False, width=_TABLE_WIDTH).print(table)
    return buffer.getvalue().rstrip("\n")


def _truncate(value: object, limit: int = _MAX_CELL) -> str:
    """Return value as text, shortened to limit characters when needed."""
    if value is None:
        return "—"
    text = str(value)
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "…"


def render_contacts_table(records: "Iterable[Record]") -> str:
    """Render contacts as a Rich table."""
    records = list(records)
    if not records:
        return "(no contacts)"

    table = Table(show_header=True, header_style="bold")
    table.add_column("Name")
    table.add_column("Phones")
    table.add_column("Email")
    table.add_column("Address")
    table.add_column("Birthday")
    table.add_column("Tags")
    table.add_column("Notes", justify="right")

    for record in records:
        phones = (
            "; ".join(phone.value for phone in record.phones)
            if record.phones
            else "—"
        )
        email = record.email.value if record.email else "—"
        address = record.address.value if record.address else "—"
        birthday = str(record.birthday) if record.birthday else "—"
        tags = ", ".join(tag.value for tag in record.tags) if record.tags else "—"
        notes = str(len(record.linked_note_ids)) if record.linked_note_ids else "0"
        table.add_row(
            _truncate(record.name.value),
            _truncate(phones),
            _truncate(email),
            _truncate(address),
            birthday,
            _truncate(tags),
            notes,
        )

    return _render_to_string(table)


def render_contact_card(record: "Record") -> str:
    """Render one contact as a label-aligned card."""
    lines: list[str] = [f"Name:      {record.name.value}"]

    if record.phones:
        for index, phone in enumerate(record.phones):
            label = "Phones:    " if index == 0 else "           "
            lines.append(f"{label}{phone.value}")
    else:
        lines.append("Phones:    —")

    lines.append(f"Email:     {record.email.value if record.email else '—'}")
    lines.append(f"Address:   {record.address.value if record.address else '—'}")
    lines.append(f"Birthday:  {record.birthday if record.birthday else '—'}")
    lines.append(
        f"Tags:      {', '.join(tag.value for tag in record.tags) if record.tags else '—'}"
    )
    lines.append(f"Notes:     {len(record.linked_note_ids)} linked")
    return "\n".join(lines)


def _note_preview(text: str, limit: int = _MAX_CELL) -> str:
    """Return one-line note preview with collapsed whitespace."""
    if not text:
        return "(empty)"
    return _truncate(" ".join(text.split()), limit)


def render_notes_table(notes: "Iterable[Note]") -> str:
    """Render notes as a Rich table."""
    notes = list(notes)
    if not notes:
        return "(no notes)"

    table = Table(show_header=True, header_style="bold")
    table.add_column("ID")
    table.add_column("Preview")
    table.add_column("Tags")
    table.add_column("Linked")
    table.add_column("Updated")

    for note in notes:
        note_id = note.id.hex[:8] if hasattr(note.id, "hex") else str(note.id)[:8]
        tags = ", ".join(tag.value for tag in note.tags) if note.tags else "—"
        linked = (
            ", ".join(note.linked_contact_names)
            if note.linked_contact_names
            else "—"
        )
        updated = note.updated_at.strftime("%Y-%m-%d") if note.updated_at else "—"
        table.add_row(
            note_id,
            _note_preview(note.text),
            _truncate(tags),
            _truncate(linked),
            updated,
        )

    return _render_to_string(table)


def render_note_card(note: "Note") -> str:
    """Render one note as a label-aligned card."""
    note_id = note.id.hex[:8] if hasattr(note.id, "hex") else str(note.id)[:8]
    lines: list[str] = [
        f"ID:        {note_id}",
        f"Created:   {note.created_at.strftime('%Y-%m-%d %H:%M')}",
    ]

    if note.updated_at and note.updated_at != note.created_at:
        lines.append(f"Updated:   {note.updated_at.strftime('%Y-%m-%d %H:%M')}")

    lines.extend([
        "",
        note.text if note.text else "(empty body)",
        "",
        f"Tags:      {', '.join(tag.value for tag in note.tags) if note.tags else '—'}",
        "Linked:    "
        f"{', '.join(note.linked_contact_names) if note.linked_contact_names else '—'}",
    ])
    return "\n".join(lines)


def render_tags_table(infos: "Iterable[TagInfo]") -> str:
    """Render tag usage stats as a Rich table."""
    infos = list(infos)
    if not infos:
        return "(no tags yet)"

    table = Table(show_header=True, header_style="bold")
    table.add_column("Name")
    table.add_column("Contacts", justify="right")
    table.add_column("Notes", justify="right")
    table.add_column("Total", justify="right")

    for info in infos:
        total = (
            info.total
            if hasattr(info, "total")
            else info.contact_count + info.note_count
        )
        table.add_row(
            info.name,
            str(info.contact_count),
            str(info.note_count),
            str(total),
        )

    return _render_to_string(table)
