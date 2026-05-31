"""Notes book.

Key = `title.strip().lower()`, value = Note (original case kept in
`note.title`). This gives case-insensitive title uniqueness while
preserving the display form the user typed.
"""

from __future__ import annotations

from collections import UserDict
from uuid import UUID

from personal_assistant.notes.note import Note

_VALID_SORT_FIELDS = ("title", "created", "updated", "tag", "contact")


class NotesBook(UserDict):
    """Keyed by lowercased title."""

    def _key(self, title: str) -> str:
        return (title or "").strip().lower()

    # --- create / read / update / delete -----------------------------------

    def add_note(self, note: Note) -> Note:
        k = self._key(note.title)
        if k in self.data:
            raise ValueError(f"Note titled '{note.title}' already exists.")
        self.data[k] = note
        return note

    def find_by_title(self, title: str) -> Note | None:
        return self.data.get(self._key(title))

    def find_by_uuid(self, uid: UUID) -> Note | None:
        for n in self.data.values():
            if n.id == uid:
                return n
        return None

    def is_title_taken(self, title: str) -> bool:
        return self._key(title) in self.data

    def rename(self, old_title: str, new_title: str) -> None:
        old_key = self._key(old_title)
        if old_key not in self.data:
            raise KeyError(old_title)
        new_key = self._key(new_title)
        if new_key != old_key and new_key in self.data:
            raise ValueError(f"Note titled '{new_title}' already exists.")
        note = self.data.pop(old_key)
        note.set_title(new_title)
        # Rebuild to preserve insertion order under the new key.
        self.data[new_key] = note

    def delete_by_title(self, title: str) -> None:
        k = self._key(title)
        if k not in self.data:
            raise KeyError(title)
        del self.data[k]

    # --- search / filter / sort --------------------------------------------

    def search(self, query: str) -> list[Note]:
        """Substring across title and text, case-insensitive."""
        q = query.strip().lower()
        if not q:
            return []
        return [
            n for n in self.data.values()
            if q in n.title.lower() or q in n.text.lower()
        ]

    def find_by_tag(self, tag: str) -> list[Note]:
        q = tag.strip().lstrip("#").lower()
        return [
            n for n in self.data.values() if any(t.value == q for t in n.tags)
        ]

    def find_by_contact(self, name: str) -> list[Note]:
        return [n for n in self.data.values() if name in n.linked_contact_names]

    def sorted_by(self, field: str, reverse: bool = False) -> list[Note]:
        """Fields: title / created / updated / tag (first) / contact (first).

        Notes with no value for the field (no tags / no links) always sort
        to the end.
        """
        if field not in _VALID_SORT_FIELDS:
            raise ValueError(
                f"Cannot sort by '{field}'. Available: {', '.join(_VALID_SORT_FIELDS)}."
            )

        def has_value(n: Note) -> bool:
            if field in ("title", "created", "updated"):
                return True
            if field == "tag":
                return bool(n.tags)
            if field == "contact":
                return bool(n.linked_contact_names)
            return False

        def key(n: Note):
            if field == "title":
                return n.title.lower()
            if field == "created":
                return n.created_at
            if field == "updated":
                return n.updated_at
            if field == "tag":
                return n.tags[0].value
            if field == "contact":
                return n.linked_contact_names[0].lower()

        present = [n for n in self.data.values() if has_value(n)]
        missing = [n for n in self.data.values() if not has_value(n)]
        present.sort(key=key, reverse=reverse)
        missing.sort(key=lambda n: n.title.lower())
        return present + missing