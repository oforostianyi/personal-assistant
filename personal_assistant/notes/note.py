"""Note model.

`title` — required, unique within NotesBook (case-insensitive).
`id` — stable UUID; it's what Records store in `linked_note_ids`, so
renaming a note never breaks links from contacts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from personal_assistant.contacts.fields import Tag


@dataclass
class Note:
    title: str
    text: str = ""
    tags: list[Tag] = field(default_factory=list)
    linked_contact_names: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        t = (self.title or "").strip()
        if not t:
            raise ValueError("Note title cannot be empty.")
        self.title = t

    # --- mutators (each calls touch() so updated_at stays current) ---

    def set_title(self, title: str) -> None:
        t = (title or "").strip()
        if not t:
            raise ValueError("Note title cannot be empty.")
        self.title = t
        self.touch()

    def set_text(self, text: str) -> None:
        self.text = text
        self.touch()

    def add_tag(self, tag: str) -> None:
        new = Tag(tag)
        if new not in self.tags:
            self.tags.append(new)
            self.touch()

    def remove_tag(self, tag: str) -> None:
        target = Tag(tag)
        try:
            self.tags.remove(target)
        except ValueError:
            raise ValueError(f"Tag '{tag}' not found on note '{self.title}'.")
        self.touch()

    def link_contact(self, name: str) -> None:
        if name not in self.linked_contact_names:
            self.linked_contact_names.append(name)
            self.touch()

    def unlink_contact(self, name: str) -> None:
        if name in self.linked_contact_names:
            self.linked_contact_names.remove(name)
            self.touch()

    def touch(self) -> None:
        self.updated_at = datetime.now()
