"""Context-aware Tab completion.

We complete:
1. the first word — command names of the current context + globals;
   inside modules, entity names (contacts / notes / tags) are added;
2. arguments of known commands (`sort`, `filter`, `edit`, `link`/`unlink`,
   `tag`/`untag`) by what is expected at that position.

The completer reads `state.context` live on each keystroke, so it only
needs to be passed to PromptSession once at startup.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Iterable

from prompt_toolkit.completion import Completer, Completion

from personal_assistant.core.registry import (
    CTX_CONTACT,
    CTX_CONTACTS,
    CTX_NOTE,
    CTX_NOTES,
    CTX_TAGS,
    REGISTRY,
)

if TYPE_CHECKING:
    from personal_assistant.core.state import AppState


_GLOBAL_NAMES = ("help", "exit", "quit", "q", "..", "/", "?")
_CONTACT_EDIT_FIELDS = ("name", "phone", "email", "address", "birthday", "tags")
_PHONE_OPS = ("add", "remove", "edit")
_TAGS_OPS = ("add", "remove")


def _yield_prefix(prefix: str, candidates: Iterable[str]):
    p = prefix.lower()
    for c in candidates:
        if c.lower().startswith(p):
            yield Completion(c, start_position=-len(prefix))


def _module_entities(state: "AppState") -> list[str]:
    if state.context == CTX_CONTACTS:
        return list(state.contacts.data.keys())
    if state.context == CTX_NOTES:
        return [n.title for n in state.notes.data.values()]
    if state.context == CTX_TAGS:
        from personal_assistant.tags.aggregator import collect_tags

        return [t.name for t in collect_tags(state)]
    return []


def _sort_fields_for(state: "AppState") -> tuple[str, ...]:
    if state.context == CTX_CONTACTS:
        from personal_assistant.contacts.book import _VALID_SORT_FIELDS

        return _VALID_SORT_FIELDS
    if state.context == CTX_NOTES:
        from personal_assistant.notes.book import _VALID_SORT_FIELDS

        return _VALID_SORT_FIELDS
    if state.context == CTX_TAGS:
        return ("name", "usage", "contacts", "notes")
    return ()


class ContextCompleter(Completer):
    """Tab-completion that reads state.context live on each keystroke."""

    def __init__(self, state: "AppState") -> None:
        self.state = state

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        if " " not in text:
            yield from self._first_word(text)
            return

        tokens = text.split()
        current = "" if text.endswith(" ") else tokens[-1]
        prior = tokens[:-1] if not text.endswith(" ") else tokens

        first = prior[0].lower()
        arg_position = len(prior) - 1  # 0 = position of first arg
        yield from self._arg_completions(first, prior, current, arg_position)

    # --- first word ------------------------------------------------------

    def _first_word(self, prefix: str):
        ctx_cmds = REGISTRY.get(self.state.context, {})
        names: list[str] = []
        seen = set()
        for cmd in ctx_cmds.values():
            if cmd.name not in seen:
                names.append(cmd.name)
                seen.add(cmd.name)
        for g in _GLOBAL_NAMES:
            if g not in seen:
                names.append(g)
                seen.add(g)
        yield from _yield_prefix(prefix, names)

        for entity in _module_entities(self.state):
            yield from _yield_prefix(prefix, [entity])

    # --- argument completions -------------------------------------------

    def _arg_completions(self, first: str, prior: list[str], current: str, pos: int):
        ctx = self.state.context

        if first == "sort":
            if pos == 0:
                yield from _yield_prefix(current, _sort_fields_for(self.state))
                return
            if pos == 1:
                yield from _yield_prefix(current, ("asc", "desc"))
                return

        if first == "filter":
            if pos == 0:
                kinds = ("tag", "contact") if ctx == CTX_NOTES else ("tag",)
                yield from _yield_prefix(current, kinds)
                return
            if pos == 1:
                kind = prior[1].lower() if len(prior) > 1 else ""
                if kind == "tag":
                    from personal_assistant.tags.aggregator import collect_tags

                    names = [t.name for t in collect_tags(self.state)]
                elif kind == "contact":
                    names = list(self.state.contacts.data.keys())
                else:
                    names = []
                yield from _yield_prefix(current, names)
                return

        if first == "edit" and ctx == CTX_CONTACT:
            if pos == 0:
                yield from _yield_prefix(current, _CONTACT_EDIT_FIELDS)
                return
            field = prior[1].lower() if len(prior) > 1 else ""
            if pos == 1:
                if field == "phone":
                    yield from _yield_prefix(current, _PHONE_OPS)
                    return
                if field == "tags":
                    yield from _yield_prefix(current, _TAGS_OPS)
                    return

        if first in ("link", "unlink") and ctx == CTX_NOTE and pos == 0:
            if first == "unlink":
                note = self.state.notes.find_by_title(self.state.entity_key)
                names = list(note.linked_contact_names) if note else []
            else:
                names = list(self.state.contacts.data.keys())
            yield from _yield_prefix(current, names)
            return

        if first in ("tag", "untag") and ctx == CTX_NOTE and pos == 0:
            from personal_assistant.tags.aggregator import collect_tags

            yield from _yield_prefix(
                current, [t.name for t in collect_tags(self.state)]
            )
            return
