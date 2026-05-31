"""Flat command registry.

Each handler registers itself via @command(name, ...). Aliases are
stored as additional keys pointing to the same Command instance, so
dispatch is O(1) per token.

Unlike beta v2's context-aware registry, this is intentionally flat —
no hierarchical REPL — to keep scope feasible in 4 days.
"""

from dataclasses import dataclass, field as dc_field
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
    help_: str = ""
    aliases: tuple[str, ...] = dc_field(default_factory=tuple)


COMMAND_REGISTRY: dict[str, Command] = {}


def command(
    name: str,
    *,
    context: str = CTX_ROOT,
    aliases: tuple[str, ...] = (),
    format: str = "",
    help_: str = "",
):
    """Decorator: register a handler under `name` (and any aliases)."""

    def decorator(func: Callable) -> Callable:
        cmd = Command(
            name=name,
            handler=func,
            context=context,
            format=format,
            help_=help_,
            aliases=tuple(aliases),
        )
        COMMAND_REGISTRY[name] = cmd
        for a in aliases:
            COMMAND_REGISTRY[a] = cmd
        return func

    return decorator


def primary_commands() -> list[Command]:
    """Distinct primary commands in insertion order (skipping alias keys)."""
    seen: set[str] = set()
    out: list[Command] = []
    for cmd in COMMAND_REGISTRY.values():
        if cmd.name in seen:
            continue
        seen.add(cmd.name)
        out.append(cmd)
    return out
