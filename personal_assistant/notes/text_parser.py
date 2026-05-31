"""Phone extraction and contact suggestion from note text.

`extract_phones` — exactly 10 digits, like our Phone validator.
`suggest_contacts` — find capitalized tokens and fuzzy-match contact names.
partial_ratio is intentional: a note may mention only a first name ("Alex")
while the contact is stored as "Alex Petrenko" — partial_ratio scores high.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from rapidfuzz import fuzz, process

if TYPE_CHECKING:
    from personal_assistant.contacts.book import ContactsBook


_PHONE_RE = re.compile(r"\b\d{10}\b")
_NAME_TOKEN_RE = re.compile(
    r"\b[A-ZА-ЯЇІЄҐ][a-zа-яїієґ0-9_-]+\b",
)


def extract_phones(text: str) -> list[str]:
    """Unique 10-digit sequences, in first-appearance order."""
    seen: set[str] = set()
    out: list[str] = []
    for m in _PHONE_RE.finditer(text):
        v = m.group()
        if v not in seen:
            out.append(v)
            seen.add(v)
    return out


def suggest_contacts(
    text: str,
    contacts: "ContactsBook",
    cutoff: int = 80,
) -> list[str]:
    """Contact names that are likely mentioned in the text."""
    candidates = list(contacts.data.keys())
    if not candidates:
        return []
    seen: set[str] = set()
    out: list[str] = []
    for m in _NAME_TOKEN_RE.finditer(text):
        token = m.group()
        match = process.extractOne(
            token,
            candidates,
            scorer=fuzz.partial_ratio,
            score_cutoff=cutoff,
        )
        if match:
            name = match[0]
            if name not in seen:
                out.append(name)
                seen.add(name)
    return out
