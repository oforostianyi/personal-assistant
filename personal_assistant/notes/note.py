"""Note model."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from personal_assistant.contacts.fields import Tag


@dataclass
class Note:
    """Free-form text note with tags, contact links, and timestamps."""

    text: str = ""
    tags: list[Tag] = field(default_factory=list)
    linked_contact_names: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    id: UUID = field(default_factory=uuid4)

    def set_text(self, text: str) -> None:
        """Replace the note body. Empty text is allowed."""
        self.text = text or ""
        self.touch()

    def add_tag(self, tag: str) -> None:
        """Append a normalized tag if it is not already present."""
        new = Tag(tag)
        if new not in self.tags:
            self.tags.append(new)
            self.touch()

    def remove_tag(self, tag: str) -> None:
        """Remove a normalized tag, raising ValueError if it is absent."""
        target = Tag(tag)
        try:
            self.tags.remove(target)
        except ValueError:
            raise ValueError(f"Tag '{tag}' not found on note '{self.id_prefix()}'.")
        self.touch()

    def link_contact(self, name: str) -> None:
        """Record a link to a contact by display name."""
        if name and name not in self.linked_contact_names:
            self.linked_contact_names.append(name)
            self.touch()

    def unlink_contact(self, name: str) -> None:
        """Remove a contact link. Missing links are ignored."""
        if name in self.linked_contact_names:
            self.linked_contact_names.remove(name)
            self.touch()

    def touch(self) -> None:
        """Update the modification timestamp."""
        self.updated_at = datetime.now()

    def id_prefix(self) -> str:
        """Return the 8-character UUID hex prefix used by commands."""
        return self.id.hex[:8]

    def preview(self, width: int = 60) -> str:
        """Return a compact one-line preview of the note text."""
        flat = " ".join((self.text or "").split())
        if len(flat) <= width:
            return flat
        return flat[: width - 1] + "..."

    def __str__(self) -> str:
        tags_str = ", ".join(tag.value for tag in self.tags) if self.tags else "-"
        return f"[{self.id_prefix()}] {self.preview()}  tags: {tags_str}"
