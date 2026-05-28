"""REPL loop.

I/O lives here. Each iteration:
  1. read a line via prompt_toolkit (with completer + bottom toolbar)
  2. parse into (cmd, args)
  3. look up handler in COMMAND_REGISTRY
  4. dispatch; print response; if exit-marker, save & break

Stage-0 ships with `hello` and `help` registered inline. Domain
modules (contacts/notes/tags) will register their commands by
importing their handlers — see the import line below this docstring.
"""

from __future__ import annotations

from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory

# === IMPORT-SIDE-EFFECT REGISTRATIONS =========================================
# As domain modules merge, add their handler imports here.
# Each `import` runs the @command decorators and populates COMMAND_REGISTRY.
# Members MUST NOT touch this file. TL adds these lines during integration.
#
from personal_assistant.contacts import handlers as _c_handlers  # noqa: F401
# from personal_assistant.notes import handlers as _n_handlers     # noqa: F401
# from personal_assistant.tags import handlers as _t_handlers      # noqa: F401
# =============================================================================

from personal_assistant.core.paths import contacts_path, notes_path
from personal_assistant.core.registry import COMMAND_REGISTRY, command, primary_commands
from personal_assistant.core.state import AppState
from personal_assistant.core.storage import PickleStorage
from personal_assistant.ui.completer import bottom_toolbar, build_completer
from personal_assistant.ui.fuzzy import suggest_command
from personal_assistant.ui.parser import parse_input
from personal_assistant.core.registry import (
    CTX_CONTACTS, CTX_TAGS, CTX_ROOT, COMMAND_REGISTRY,
)

_STORAGE = PickleStorage()
_EXIT_NAMES = {"exit", "quit", "q"}


# --- Built-in Stage-0 commands -----------------------------------------------

@command("hello", context=CTX_ROOT, help_="Say hi.")
def _hello(args, state):
    return "Hi! Type 'help' to see commands."


@command("help", aliases=("?",),context=CTX_ROOT,  help_="Show available commands.")
def _help(args, state):
    lines = ["Available commands:"]
    for cmd in primary_commands():
        if cmd.name in ("help",):
            continue
        if cmd.format:
            lines.append(f"  {cmd.name} {cmd.format} — {cmd.help_}")
        else:
            lines.append(f"  {cmd.name} — {cmd.help_}")
    lines.append("  help/? — this message.")
    lines.append("  exit/quit/q — leave (auto-saves state).")
    return "\n".join(lines)


# --- Dispatch ---------------------------------------------------------------

def _dispatch(line: str, state: AppState) -> tuple[str, bool]:
    cmd_name, args = parse_input(line)
    if not cmd_name:
        return "", False
    if cmd_name in _EXIT_NAMES:
        return "Good bye!", True

    cmd = COMMAND_REGISTRY.get(cmd_name)
    if cmd is not None:
        return cmd.handler(args, state), False

    candidates = list(COMMAND_REGISTRY.keys()) + list(_EXIT_NAMES)
    guess = suggest_command(cmd_name, candidates)
    if guess:
        return f"Unknown: '{cmd_name}'. Did you mean '{guess}'?", False
    return f"Unknown command: '{cmd_name}'. Type 'help' for commands.", False


# --- Entry point ------------------------------------------------------------

def main() -> None:
    from personal_assistant.contacts.book import ContactsBook
    contacts = _STORAGE.load(contacts_path(), ContactsBook)
    notes = _STORAGE.load(notes_path(), dict)
    state = AppState(contacts=contacts, notes=notes)

    session: PromptSession = PromptSession(
        history=InMemoryHistory(),
        completer=build_completer(),
        bottom_toolbar=lambda: bottom_toolbar(session.app.current_buffer.text),
    )

    print("Personal Assistant. Type 'help' for commands, 'exit' to quit.")
    while True:
        try:
            line = session.prompt("> ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        response, should_exit = _dispatch(line, state)
        if response:
            print(response)
            if "\n" in response:
                print()
        if should_exit:
            break

    _STORAGE.save(state.contacts, contacts_path())
    _STORAGE.save(state.notes, notes_path())