"""REPL loop.

All I/O lives here (except the interactive `edit`/`new` menus in later
cards — there handlers may read extra input). The dispatcher selects a
command by the current context, adding global navigation, entity-enter
inside modules, and a fuzzy "did you mean?" fallback.
"""

from __future__ import annotations

from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory

# Importing the package registers every module's handlers via @command.
import personal_assistant  # noqa: F401
from personal_assistant.contacts.book import ContactsBook

# from personal_assistant.contacts.handlers import create_contact_from_input  # TODO(card-20)
from personal_assistant.core.paths import contacts_path, notes_path
from personal_assistant.core.registry import (
    CTX_CONTACTS,
    CTX_NOTES,
    CTX_TAGS,
    REGISTRY,
)
from personal_assistant.core.state import AppState
from personal_assistant.core.storage import PickleStorage
from personal_assistant.notes.book import NotesBook

# from personal_assistant.notes.handlers import create_note_from_input  # TODO(card-22)
from personal_assistant.ui.completer import ContextCompleter
from personal_assistant.ui.fuzzy import fuzzy_match_all, suggest_command
from personal_assistant.ui.help import render_help
from personal_assistant.ui.parser import tokenize

_STORAGE = PickleStorage()
_GLOBAL_EXITS = {"exit", "quit", "q"}
_GLOBAL_NAMES = ["help", "?", "..", "/", "exit", "quit", "q"]


def _entities_for_module(state: AppState) -> list[str]:
    if state.context == CTX_CONTACTS:
        return list(state.contacts.data.keys())
    if state.context == CTX_NOTES:
        return [n.title for n in state.notes.data.values()]
    if state.context == CTX_TAGS:
        from personal_assistant.tags.aggregator import collect_tags
        return [t.name for t in collect_tags(state)]
    return []


def _format_numbered(matches: list[str]) -> str:
    lines = ["Multiple matches:"]
    for i, m in enumerate(matches, 1):
        lines.append(f"  {i}. {m}")
    lines.append("Type the exact name to enter, or refine your query.")
    return "\n".join(lines)


def _confirm_create(query: str, kind: str) -> bool:
    """y/N confirmation. Any EOF/Ctrl-C → no."""
    try:
        answer = input(f"Create {kind} '{query}'? (y/N): ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return False
    return answer in ("y", "yes")


def _try_enter_entity(line: str, state: AppState) -> str | None:
    query = line.strip()
    if not query:
        return None

    entities = _entities_for_module(state)
    if not entities:
        return None

    q_low = query.lower()
    exact = [e for e in entities if e.lower() == q_low]
    if exact:
        state.enter_entity(exact[0])
        return ""

    matches = [e for e in entities if q_low in e.lower()]
    if not matches:
        matches = fuzzy_match_all(query, entities, cutoff=80)

    if len(matches) == 1:
        state.enter_entity(matches[0])
        return ""
    if len(matches) > 1:
        return _format_numbered(matches)

    first_token = (query.split() or [""])[0].lower()
    ctx_cmds = REGISTRY.get(state.context, {})
    if suggest_command(first_token, list(ctx_cmds.keys()) + _GLOBAL_NAMES, cutoff=70):
        return None

    if state.context == CTX_CONTACTS:
        # if _confirm_create(query, "contact"):              # TODO(card-20)
        #     return create_contact_from_input(query, state)  # TODO(card-20)
        return ""
    if state.context == CTX_NOTES:
        # if _confirm_create(query, "note"):                 # TODO(card-22)
        #     return create_note_from_input(query, state)     # TODO(card-22)
        return ""
    return None


def _auto_show(state: AppState) -> str:
    show_cmd = REGISTRY.get(state.context, {}).get("show")
    if show_cmd is None:
        return ""
    return show_cmd.handler([], state)


def _dispatch_inner(line: str, state: AppState) -> tuple[str, bool]:
    tokens = tokenize(line)
    if not tokens:
        return "", False

    first = tokens[0].lower()
    rest = tokens[1:]

    if first in _GLOBAL_EXITS:
        return "Good bye!", True
    if first == "..":
        state.go_up()
        return "", False
    if first == "/":
        state.go_root()
        return "", False
    if first in ("help", "?"):
        return render_help(state), False

    ctx_commands = REGISTRY.get(state.context, {})
    if first in ctx_commands:
        return ctx_commands[first].handler(rest, state), False

    if state.context in (CTX_CONTACTS, CTX_NOTES, CTX_TAGS):
        resolved = _try_enter_entity(line, state)
        if resolved is not None:
            return resolved, False

    candidates = list(ctx_commands.keys()) + _GLOBAL_NAMES
    guess = suggest_command(first, candidates)
    if guess:
        return f"Unknown: '{first}'. Did you mean '{guess}'?", False
    return f"Unknown command: '{first}'. Type 'help' for available commands.", False


def _dispatch(line: str, state: AppState) -> tuple[str, bool]:
    before = (state.module, state.entity_key)
    response, should_exit = _dispatch_inner(line, state)
    after = (state.module, state.entity_key)
    entered_new_entity = (
        not should_exit
        and state.entity_key is not None
        and before[1] is None
        and after != before
    )
    if entered_new_entity:
        card = _auto_show(state)
        if card:
            response = f"{response}\n{card}" if response else card
    return response, should_exit


def main() -> None:
    contacts = _STORAGE.load(contacts_path(), ContactsBook)
    notes = _STORAGE.load(notes_path(), NotesBook)
    state = AppState(contacts=contacts, notes=notes)

    session = PromptSession(
        history=InMemoryHistory(),
        completer=ContextCompleter(state),
    )
    print("Personal Assistant. Type 'help' for commands, 'exit' to quit.")
    while True:
        try:
            line = session.prompt(state.prompt())
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