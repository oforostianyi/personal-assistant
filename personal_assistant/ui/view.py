"""Compatibility shim for rendering imports.

This file exists for legacy import lines that reference ui.views.* (a name from
the solo beta prototype). The real implementation lives in ui/tables.py once
Card 13 lands. Until then, these functions delegate to the text fallback in
contacts/handlers.py.

When Card 13 ships, this file may either be deleted (with a follow-up PR
adjusting any remaining imports) or kept as thin re-exports of ui.tables.
"""

from __future__ import annotations


def render_contacts_table(records) -> str:
    from personal_assistant.contacts.handlers import _render_contacts_text_table
    return _render_contacts_text_table(records)


def render_notes_table(notes) -> str:
    notes = list(notes)
    if not notes:
        return "(no notes)"
    lines = [f"{'ID':<10} {'Preview':<60} {'Tags':<20} {'Linked':<20}"]
    lines.append("-" * len(lines[0]))
    for n in notes:
        nid = str(getattr(n, "id", ""))[:8]
        text = getattr(n, "text", "")
        preview = (text[:59] + "…") if len(text) > 60 else text
        tags = ", ".join(t.value for t in getattr(n, "tags", [])) or "—"
        linked = ", ".join(getattr(n, "linked_contact_names", [])) or "—"
        lines.append(f"{nid:<10} {preview:<60} {tags:<20} {linked:<20}")
    return "\n".join(lines)


def render_contact_card(record) -> str:
    lines = []
    lines.append(f"Name:      {record.name.value}")
    lines.append(f"Phones:    {'; '.join(p.value for p in record.phones) or '—'}")
    lines.append(f"Email:     {record.email.value if record.email else '—'}")
    lines.append(f"Address:   {record.address.value if record.address else '—'}")
    lines.append(f"Birthday:  {record.birthday if record.birthday else '—'}")
    lines.append(f"Tags:      {', '.join(t.value for t in record.tags) or '—'}")
    lines.append(f"Notes:     {len(record.linked_note_ids)} linked")
    return "\n".join(lines)