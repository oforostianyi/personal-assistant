"""rich-based renderers for tables and cards.

Everything is printed into a plain string via
`Console(file=StringIO(), force_terminal=False)`, so a handler can return
the result directly as its response string.
"""

from __future__ import annotations

from datetime import date
from io import StringIO
from typing import TYPE_CHECKING, Iterable

from rich.console import Console
from rich.table import Table

if TYPE_CHECKING:
    from personal_assistant.contacts.record import Record
    from personal_assistant.notes.note import Note
    from personal_assistant.tags.aggregator import TagInfo


_TABLE_WIDTH = 120


def _render_table(table: Table) -> str:
    buf = StringIO()
    Console(file=buf, force_terminal=False, width=_TABLE_WIDTH).print(table)
    return buf.getvalue().rstrip("\n")


def render_contacts_table(records: Iterable["Record"]) -> str:
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
    for r in records:
        phones = "; ".join(p.value for p in r.phones) if r.phones else "—"
        email = r.email.value if r.email else "—"
        address = r.address.value if r.address else "—"
        birthday = str(r.birthday) if r.birthday else "—"
        tags = ", ".join(t.value for t in r.tags) if r.tags else "—"
        notes = str(len(r.linked_note_ids)) if r.linked_note_ids else "0"
        table.add_row(r.name.value, phones, email, address, birthday, tags, notes)
    return _render_table(table)


def _days_until_birthday(bday: date) -> int:
    today = date.today()
    try:
        this_year = bday.replace(year=today.year)
    except ValueError:
        this_year = bday.replace(year=today.year, day=28)
    if this_year < today:
        try:
            this_year = bday.replace(year=today.year + 1)
        except ValueError:
            this_year = bday.replace(year=today.year + 1, day=28)
    return (this_year - today).days


def render_contact_card(record: "Record") -> str:
    r = record
    lines: list[str] = []
    lines.append(f"Name:      {r.name.value}")
    if r.phones:
        for i, p in enumerate(r.phones):
            label = "Phones:    " if i == 0 else "           "
            lines.append(f"{label}{p.value}")
    else:
        lines.append("Phones:    —")
    lines.append(f"Email:     {r.email.value if r.email else '—'}")
    lines.append(f"Address:   {r.address.value if r.address else '—'}")
    if r.birthday:
        days = _days_until_birthday(r.birthday.value)
        hint = ""
        if 0 <= days <= 7:
            hint = (
                f"  (in {days} day{'s' if days != 1 else ''})"
                if days > 0
                else "  (today!)"
            )
        lines.append(f"Birthday:  {r.birthday}{hint}")
    else:
        lines.append("Birthday:  —")
    lines.append(f"Tags:      {', '.join(t.value for t in r.tags) if r.tags else '—'}")
    lines.append(f"Notes:     {len(r.linked_note_ids)} linked")
    return "\n".join(lines)


# --- notes -----------------------------------------------------------------


def render_notes_table(notes: Iterable["Note"]) -> str:
    notes = list(notes)
    if not notes:
        return "(no notes)"
    table = Table(show_header=True, header_style="bold")
    table.add_column("Title")
    table.add_column("Tags")
    table.add_column("Contacts")
    table.add_column("Updated")
    for n in notes:
        title = n.title if len(n.title) <= 40 else (n.title[:39] + "…")
        tags = ", ".join(t.value for t in n.tags) if n.tags else "—"
        contacts = ", ".join(n.linked_contact_names) if n.linked_contact_names else "—"
        updated = n.updated_at.strftime("%Y-%m-%d")
        table.add_row(title, tags, contacts, updated)
    return _render_table(table)


def render_tags_table(infos: Iterable["TagInfo"]) -> str:
    infos = list(infos)
    if not infos:
        return "(no tags yet)"
    table = Table(show_header=True, header_style="bold")
    table.add_column("Name")
    table.add_column("Contacts", justify="right")
    table.add_column("Notes", justify="right")
    table.add_column("Total", justify="right")
    for info in infos:
        table.add_row(
            info.name,
            str(info.contact_count),
            str(info.note_count),
            str(info.total),
        )
    return _render_table(table)


def render_tag_card(info: "TagInfo") -> str:
    return (
        f"Tag:      {info.name}\n"
        f"Contacts: {info.contact_count}\n"
        f"Notes:    {info.note_count}\n"
        f"Total:    {info.total}"
    )


def render_note_card(note: "Note") -> str:
    lines: list[str] = []
    lines.append(f"Title:     {note.title}")
    lines.append(f"Created:   {note.created_at.strftime('%Y-%m-%d %H:%M')}")
    if note.updated_at and note.updated_at != note.created_at:
        lines.append(f"Updated:   {note.updated_at.strftime('%Y-%m-%d %H:%M')}")
    lines.append("")
    lines.append(note.text if note.text else "(empty body)")
    lines.append("")
    lines.append(
        f"Tags:      {', '.join(t.value for t in note.tags) if note.tags else '—'}"
    )
    lines.append(
        f"Linked:    "
        f"{', '.join(note.linked_contact_names) if note.linked_contact_names else '—'}"
    )
    return "\n".join(lines)
