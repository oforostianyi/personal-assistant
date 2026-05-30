"""Notes book container."""

from __future__ import annotations

from collections import UserDict
from uuid import UUID

from personal_assistant.notes.note import Note


class NotesBook(UserDict[UUID, Note]):
    """UUID-keyed collection of notes."""

    def add_note(self, text: str) -> Note:
        """Create, store, and return a new note."""
        note = Note(text=text or "")
        self.data[note.id] = note
        return note

    def delete(self, note_id: UUID) -> None:
        """Remove a note by full UUID."""
        if note_id not in self.data:
            raise KeyError(f"Note '{note_id}' not found.")
        del self.data[note_id]

    def find_by_text(self, query: str) -> list[Note]:
        """Case-insensitive substring search across note text and tag slugs."""
        q = (query or "").strip().lower()
        if not q:
            return []

        results: list[Note] = []
        for note in self.data.values():
            if q in (note.text or "").lower():
                results.append(note)
                continue
            if any(q in tag.value for tag in note.tags):
                results.append(note)
        return results

    def find_by_id_prefix(self, prefix: str) -> Note | None:
        """Resolve a note by UUID hex prefix."""
        p = (prefix or "").strip().lower()
        if not p:
            return None

        matches = [note for note in self.data.values() if note.id.hex.startswith(p)]
        if not matches:
            return None
        if len(matches) > 1:
            raise ValueError(
                f"Ambiguous note id prefix '{prefix}'. "
                f"Matches: {', '.join(note.id_prefix() for note in matches)}."
            )
        return matches[0]

    def list_all(self) -> list[Note]:
        """Return all notes in insertion order."""
        return list(self.data.values())
