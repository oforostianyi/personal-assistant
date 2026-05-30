"""Tags aggregator."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class TagInfo:
    """A tag name and its usage counts in contacts and notes."""

    name: str
    contact_count: int
    note_count: int

    @property
    def total(self) -> int:
        """Return combined usages across both books."""
        return self.contact_count + self.note_count


def _iter_values(book) -> Iterable:
    """Yield values from a UserDict-backed book, plain dict, or iterable."""
    if book is None:
        return ()

    data = getattr(book, "data", None)
    if data is not None:
        return data.values()

    if isinstance(book, dict):
        return book.values()

    return book


def collect_tags(state) -> list[TagInfo]:
    """Return all tags used across contacts and notes, sorted by name."""
    counts: dict[str, list[int]] = {}

    for record in _iter_values(getattr(state, "contacts", None)):
        tags = getattr(record, "tags", None) or ()
        for tag in tags:
            name = getattr(tag, "value", None)
            if name:
                counts.setdefault(name, [0, 0])[0] += 1

    for note in _iter_values(getattr(state, "notes", None)):
        tags = getattr(note, "tags", None) or ()
        for tag in tags:
            name = getattr(tag, "value", None)
            if name:
                counts.setdefault(name, [0, 0])[1] += 1

    return [
        TagInfo(name, contact_count, note_count)
        for name, (contact_count, note_count) in sorted(counts.items())
    ]
