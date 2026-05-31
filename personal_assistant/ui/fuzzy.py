"""rapidfuzz wrappers for two needs:

- `suggest_command` — "did you mean?" hint when a command is mistyped.
- `fuzzy_match_all` — all entity names (contact/note/tag) above a cutoff.
"""

from __future__ import annotations

from typing import Iterable

from rapidfuzz import fuzz, process


def suggest_command(
    token: str, candidates: Iterable[str], cutoff: int = 60
) -> str | None:
    candidates = list(candidates)
    if not token or not candidates:
        return None
    result = process.extractOne(
        token,
        candidates,
        scorer=fuzz.ratio,
        score_cutoff=cutoff,
    )
    return result[0] if result else None


def fuzzy_match_all(
    query: str, candidates: Iterable[str], cutoff: int = 80
) -> list[str]:
    """All candidates passing `cutoff` by fuzz.ratio (case-insensitive).

    Plain ratio, not partial: a longer query ('Alexandra') must not match a
    shorter contact ('Alex') — partial_ratio would score 100 and force entry
    into Alex instead of offering to create Alexandra.
    """
    candidates = list(candidates)
    if not query or not candidates:
        return []
    matches = process.extract(
        query,
        candidates,
        scorer=fuzz.ratio,
        processor=str.lower,
        score_cutoff=cutoff,
        limit=len(candidates),
    )
    return [name for name, _score, _idx in matches]
