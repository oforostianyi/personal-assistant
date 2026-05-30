"""Lightweight extractors for actionable hints in note text."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from rapidfuzz import fuzz, process

from personal_assistant.contacts.fields import Phone

if TYPE_CHECKING:
    from personal_assistant.contacts.book import ContactsBook


_PHONE_RE = re.compile(r"\b\d{10}\b")
_INTL_PHONE_RE = re.compile(r"\b380\d{9}\b")
_NAME_TOKEN_RE = re.compile(r"\b[A-ZА-ЯЇІЄҐ][a-zа-яїієґ0-9_-]{1,}\b")

_FUZZY_CUTOFF = 80


def extract_phones(text: str) -> list[str]:
    """Return canonical 10-digit phone numbers found in text.

    Values are normalized through the shared Phone field, deduplicated after
    normalization, and returned in first-appearance order.
    """
    if not text:
        return []

    matches = sorted(
        [*_INTL_PHONE_RE.finditer(text), *_PHONE_RE.finditer(text)],
        key=lambda match: match.start(),
    )
    seen: set[str] = set()
    phones: list[str] = []

    for match in matches:
        try:
            canonical = Phone(match.group()).value
        except ValueError:
            continue
        if canonical not in seen:
            seen.add(canonical)
            phones.append(canonical)

    return phones


def suggest_contacts(
    text: str,
    contacts_book: "ContactsBook",
    cutoff: int = _FUZZY_CUTOFF,
) -> list[str]:
    """Return sorted contact names plausibly mentioned in text."""
    if not text:
        return []

    candidates = list(getattr(contacts_book, "data", {}).keys())
    if not candidates:
        return []

    matched: set[str] = set()
    for match in _NAME_TOKEN_RE.finditer(text):
        result = process.extractOne(
            match.group(),
            candidates,
            scorer=fuzz.WRatio,
            score_cutoff=cutoff,
        )
        if result is not None:
            matched.add(result[0])

    return sorted(matched)
