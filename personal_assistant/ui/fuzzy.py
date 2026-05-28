"""Did-you-mean suggestions via rapidfuzz.

`suggest_command(token, candidates)` returns the single best fuzzy
match (above cutoff) or None. Used as a last-resort hint when a
command isn't recognized.
"""

from __future__ import annotations

from typing import Iterable

from rapidfuzz import fuzz, process


def suggest_command(token: str, candidates: Iterable[str], cutoff: int = 60) -> str | None:
    candidates = list(candidates)
    if not token or not candidates:
        return None
    result = process.extractOne(
        token, candidates, scorer=fuzz.ratio, score_cutoff=cutoff,
    )
    return result[0] if result else None