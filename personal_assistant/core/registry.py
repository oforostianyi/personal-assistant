"""Context-aware command registry.

Each handler is registered for a concrete context (root / contacts /
contacts/* / notes / notes/* / tags / tags/*). Aliases register as
separate keys pointing to the same Command, so the dispatcher lookup
stays O(1) per token.
"""

from dataclasses import dataclass
from dataclasses import field as dc_field
from typing import Callable

CTX_ROOT = "root"
CTX_CONTACTS = "contacts"
CTX_CONTACT = "contacts/*"
CTX_NOTES = "notes"
CTX_NOTE = "notes/*"
CTX_TAGS = "tags"
CTX_TAG = "tags/*"


@dataclass(frozen=True)
class Command:
    name: str
    handler: Callable
    context: str
    format: str = ""
    help_text: str = ""
    aliases: tuple[str, ...] = dc_field(default_factory=tuple)


REGISTRY: dict[str, dict[str, Command]] = {}


def command(name, *, context, aliases=(), format="", help_text=""):
    def decorator(func):
        cmd = Command(name, func, context, format, help_text, tuple(aliases))
        REGISTRY.setdefault(context, {})[name] = cmd
        for a in aliases:
            REGISTRY[context][a] = cmd
        return func

    return decorator


def commands_for(context: str) -> list[Command]:
    """Unique primary commands registered for this context, in insertion order."""
    seen, out = set(), []
    for cmd in REGISTRY.get(context, {}).values():
        if cmd.name not in seen:
            seen.add(cmd.name)
            out.append(cmd)
    return out
