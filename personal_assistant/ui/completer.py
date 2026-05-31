"""Tab-completion + format-hint bottom toolbar driven by the registry.

build_completer() — WordCompleter listing every registered command
plus the global exit aliases. Case-insensitive prefix match.

bottom_toolbar(text) — when the user has started typing, looks up the
first token in the registry and returns "format: <name> <format>" to
display under the prompt.

This is intentionally simpler than beta v2's ContextCompleter — no
context awareness, no entity completion. The Contacts/Notes owners
may extend this with arg-level completion if time permits.
"""

from __future__ import annotations

from prompt_toolkit.completion import WordCompleter

from personal_assistant.core.registry import COMMAND_REGISTRY

_EXIT_NAMES = ("exit", "quit", "q")


def build_completer() -> WordCompleter:
    words = sorted(set(COMMAND_REGISTRY.keys()) | set(_EXIT_NAMES))
    return WordCompleter(words, ignore_case=True)


def bottom_toolbar(text: str) -> str:
    """Return a format-hint string for the command currently being typed."""
    text = (text or "").strip()
    if not text:
        return ""
    first = text.split()[0].lower()
    cmd = COMMAND_REGISTRY.get(first)
    if cmd is None:
        return ""
    if cmd.format:
        return f"format: {cmd.name} {cmd.format}"
    return f"command: {cmd.name}"
