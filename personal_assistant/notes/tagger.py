"""Tag inference for notes."""

from __future__ import annotations

import re


_HASHTAG_RE = re.compile(r"#([\w-]+)", re.UNICODE)
_WORD_RE = re.compile(r"[\w-]{3,}", re.UNICODE)
_TAG_SLUG_RE = re.compile(r"^[\w-]+$", re.UNICODE)


_STOPWORDS: frozenset[str] = frozenset(
    {
        # English
        "the",
        "a",
        "an",
        "is",
        "are",
        "and",
        "or",
        "to",
        "of",
        "in",
        "on",
        "at",
        "for",
        "with",
        "by",
        "but",
        # Ukrainian
        "не",
        "та",
        "і",
        "в",
        "на",
        "з",
        "до",
        "від",
        "за",
        "як",
    }
)


def _is_valid_slug(word: str) -> bool:
    """Return True when word is compatible with the shared Tag field."""
    return bool(word) and bool(_TAG_SLUG_RE.match(word))


def extract_tags(text: str, known_tags: set[str]) -> list[str]:
    """Return sorted lowercase tag slugs inferred from note text.

    Tags come from explicit hashtags and from plain words already present
    in the known tag vocabulary. Invalid candidates and stopwords are skipped.
    """
    if not text:
        return []

    found: set[str] = set()

    for match in _HASHTAG_RE.finditer(text):
        slug = match.group(1).lower()
        if _is_valid_slug(slug):
            found.add(slug)

    if known_tags:
        normalized_known = {tag.lower() for tag in known_tags if tag}
        for match in _WORD_RE.finditer(text.lower()):
            word = match.group()
            if word in _STOPWORDS:
                continue
            if _is_valid_slug(word) and word in normalized_known:
                found.add(word)

    return sorted(found)
