"""Auto-tagging for notes.

`extract_hashtags` catches `#word` (unicode letters + digits + `_-`),
returns first-appearance order, lowercased, de-duplicated.

`suggest_tags` is the main "learning-loop": if a word is already a tag
somewhere in the system (on another contact or note) and appears in the
new text, we suggest it as a tag for the new note. This reinforces
existing tags without a new taxonomy. Hashtags always come first
(explicit user intent).
"""

from __future__ import annotations

import re

_HASHTAG_RE = re.compile(r"#([\w-]+)", re.UNICODE)
_WORD_RE = re.compile(r"[\w-]{3,}", re.UNICODE)

# Small stop-list: only the most common 3+ char function words in three
# languages. Deliberately short — we don't want to drop a legitimate domain
# term, just the most banal noise.
_STOPWORDS: frozenset[str] = frozenset({
    # English
    "the", "and", "for", "with", "are", "you", "your", "but", "not", "all",
    "can", "has", "have", "had", "was", "were", "this", "that", "from",
    "our", "out", "who", "how", "what", "when", "where", "why", "any",
    "some", "they", "them", "their", "there", "these", "those",
    "also", "more", "than", "then", "into", "over", "just", "very",
    # Ukrainian
    "для", "але", "або", "при", "від", "що", "як", "так", "цей", "ця", "ці",
    "який", "яка", "які", "його", "її", "ваш", "наш",
    "ще", "вже", "там", "тут", "коли", "куди", "якщо", "тому", "потім",
    "буде", "було", "були", "має", "мало", "мали",
})


def extract_hashtags(text: str) -> list[str]:
    """Hashtags in first-appearance order, de-duplicated, lowercased."""
    seen: set[str] = set()
    out: list[str] = []
    for m in _HASHTAG_RE.finditer(text):
        v = m.group(1).lower()
        if v and v not in seen:
            out.append(v)
            seen.add(v)
    return out


def suggest_tags(text: str, known_tags: set[str]) -> list[str]:
    """Hashtags + words already used as tags somewhere in the system.

    `known_tags` must be a set of already-normalized values (lowercase, no
    `#`). It spans both contacts and notes — tags are cross-cutting.
    """
    hashtags = extract_hashtags(text)
    seen = set(hashtags)
    out = list(hashtags)
    if not known_tags:
        return out

    for m in _WORD_RE.finditer(text.lower()):
        w = m.group()
        if w in seen or w in _STOPWORDS:
            continue
        if w in known_tags:
            out.append(w)
            seen.add(w)
    return out