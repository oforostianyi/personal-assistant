"""Render help text for the current context."""

from __future__ import annotations

from typing import TYPE_CHECKING

from personal_assistant.core.registry import (
    CTX_CONTACTS,
    CTX_NOTES,
    CTX_TAGS,
    commands_for,
)

if TYPE_CHECKING:
    from personal_assistant.core.state import AppState


_GLOBAL_HELP = [
    ("..", "Up one level"),
    ("/", "Go to root"),
    ("help / ?", "Show this help"),
    ("exit / quit / q", "Save and quit"),
]


def _entity_enter_hint(ctx: str) -> tuple[str, str] | None:
    if ctx == CTX_CONTACTS:
        return ("<name>", "Enter a contact (or create if not found)")
    if ctx == CTX_NOTES:
        return ("<title>", "Enter a note (or create if not found)")
    if ctx == CTX_TAGS:
        return ("<tag>", "Enter a tag")
    return None


def render_help(state: "AppState") -> str:
    cmds = commands_for(state.context)
    lines: list[str] = []
    lines.append(f"Context: {state.context}")
    lines.append("")
    if cmds:
        lines.append("Commands:")
        for c in cmds:
            head = c.name
            if c.format:
                head = f"{c.name} {c.format}"
            if c.aliases:
                head += f"  (aliases: {', '.join(c.aliases)})"
            tail = f"  — {c.help_text}" if c.help_text else ""
            lines.append(f"  {head}{tail}")
    else:
        lines.append("Commands: (none registered for this context yet)")

    hint = _entity_enter_hint(state.context)
    if hint:
        lines.append("")
        lines.append(f"  {hint[0]:<20} {hint[1]}")

    lines.append("")
    lines.append("Global:")
    for name, descr in _GLOBAL_HELP:
        lines.append(f"  {name:<20} {descr}")
    return "\n".join(lines)
