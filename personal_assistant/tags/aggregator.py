"""Tag aggregations.

The `tags` module is virtual: no `*.pkl` of its own. Every operation walks
both books live. This is more expensive to compute, but it's the only way
to keep tags always consistent with contacts/notes without a cache layer.
"""

from __future__ import annotations

from dataclasses import dataclass

from personal_assistant.contacts.fields import Tag


@dataclass(frozen=True)
class TagInfo:
    name: str
    contact_count: int
    note_count: int

    @property
    def total(self) -> int:
        return self.contact_count + self.note_count


def collect_tags(state) -> list[TagInfo]:
    counts: dict[str, list[int]] = {}  # name → [contact_count, note_count]
    for record in state.contacts.data.values():
        for t in record.tags:
            counts.setdefault(t.value, [0, 0])[0] += 1
    for note in state.notes.data.values():
        for t in note.tags:
            counts.setdefault(t.value, [0, 0])[1] += 1
    return [TagInfo(name, c, n) for name, (c, n) in counts.items()]


def _normalize(name: str) -> str:
    return name.strip().lstrip("#").lower()


def find_tag(state, name: str) -> TagInfo | None:
    q = _normalize(name)
    for info in collect_tags(state):
        if info.name == q:
            return info
    return None


def _replace_tag_everywhere(state, old: str, new: str) -> int:
    """Replace one tag with another — shared by `rename` and `merge`.

    No duplicates arise: if a record already had both `old` and `new`, only
    `new` remains afterwards. Affected count is per record/note, not per tag.
    """
    old_v = _normalize(old)
    new_tag = Tag(new)  # format validation
    affected = 0
    for record in state.contacts.data.values():
        if any(t.value == old_v for t in record.tags):
            record.tags = [t for t in record.tags if t.value != old_v]
            if new_tag not in record.tags:
                record.tags.append(new_tag)
            affected += 1
    for note in state.notes.data.values():
        if any(t.value == old_v for t in note.tags):
            note.tags = [t for t in note.tags if t.value != old_v]
            if new_tag not in note.tags:
                note.tags.append(new_tag)
            note.touch()
            affected += 1
    return affected


def rename_tag(state, old: str, new: str) -> int:
    """Rename a tag everywhere. Returns the number of changed entities."""
    return _replace_tag_everywhere(state, old, new)


def merge_tag(state, source: str, target: str) -> int:
    """Merge source into target everywhere. Returns changed-entity count."""
    return _replace_tag_everywhere(state, source, target)


def delete_tag(state, name: str) -> int:
    """Remove `name` from all records. Returns the number of changed entities."""
    v = _normalize(name)
    affected = 0
    for record in state.contacts.data.values():
        if any(t.value == v for t in record.tags):
            record.tags = [t for t in record.tags if t.value != v]
            affected += 1
    for note in state.notes.data.values():
        if any(t.value == v for t in note.tags):
            note.tags = [t for t in note.tags if t.value != v]
            note.touch()
            affected += 1
    return affected
