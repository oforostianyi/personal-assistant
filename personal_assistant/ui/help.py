"""Auto-generated help text from the flat command registry."""

from __future__ import annotations

from personal_assistant.core.registry import Command, command, primary_commands


_SECTION_ORDER: tuple[str, ...] = ("Contacts", "Notes", "Tags", "Built-in")

_EXPLICIT_SECTION: dict[str, str] = {
    "birthdays": "Contacts",
    "list-tags": "Tags",
    "find-by-tag": "Tags",
    "sort-by-tag": "Tags",
    "rename-tag": "Tags",
    "merge-tags": "Tags",
    "hello": "Built-in",
    "help": "Built-in",
    "exit": "Built-in",
    "quit": "Built-in",
    "q": "Built-in",
}

_SLUG_TO_SECTION: dict[str, str] = {
    "contact": "Contacts",
    "note": "Notes",
    "tag": "Tags",
}


def _section_for(cmd: Command) -> str:
    """Return the display section for a command."""
    if cmd.name in _EXPLICIT_SECTION:
        return _EXPLICIT_SECTION[cmd.name]

    parts = cmd.name.split("-")
    if len(parts) >= 2:
        tail = parts[-1].rstrip("s")
        section = _SLUG_TO_SECTION.get(tail)
        if section:
            return section

    return "Built-in"


def _format_command_line(cmd: Command) -> str:
    """Format a command with its format hint and help text."""
    head = cmd.name
    if cmd.format:
        head = f"{cmd.name} {cmd.format}"
    if cmd.help_:
        return f"  {head:<36}{cmd.help_}"
    return f"  {head}"


def _ordered_section_names(sections: dict[str, list[Command]]) -> list[str]:
    """Return known sections first, then unknown sections alphabetically."""
    known = [section for section in _SECTION_ORDER if section in sections]
    unknown = sorted(section for section in sections if section not in _SECTION_ORDER)
    return known + unknown


def render_help() -> str:
    """Return grouped help text for currently registered commands."""
    sections: dict[str, list[Command]] = {}
    for cmd in primary_commands():
        sections.setdefault(_section_for(cmd), []).append(cmd)

    lines: list[str] = ["Available commands:"]
    for section_name in _ordered_section_names(sections):
        commands = sorted(sections[section_name], key=lambda item: item.name)
        if not commands:
            continue
        lines.append("")
        lines.append(f"[{section_name}]")
        for cmd in commands:
            lines.append(_format_command_line(cmd))

    lines.append("")
    lines.append("[Global]")
    lines.append(f"  {'help, ?':<36}Show this message.")
    lines.append(f"  {'exit, quit, q':<36}Leave (auto-saves state).")
    return "\n".join(lines)


@command("help", aliases=("?",), help_="Show all commands grouped by module.")
def _help_handler(_args, _state):
    return render_help()
