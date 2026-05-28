"""App state.

Holds both books (contacts, notes). Types are `Any` in Stage-0 because
ContactsBook and NotesBook are not yet defined — they land later in
the team's PRs. Defaults are plain dicts so the app starts with empty
state and persistence works on day 0.

When the Contacts and Notes modules land, replace the `Any` annotations
with the real types and the defaults with `ContactsBook()` / `NotesBook()`.
"""

from __future__ import annotations

from dataclasses import dataclass, field as dc_field
from typing import Any, TYPE_CHECKING

from personal_assistant.core.registry import (
    CTX_ROOT, CTX_CONTACTS, CTX_CONTACT,
    CTX_NOTES, CTX_NOTE, CTX_TAGS, CTX_TAG,
)

if TYPE_CHECKING:
    from personal_assistant.contacts.book import ContactsBook
    #from personal_assistant.notes.book import NotesBook

@dataclass
class AppState:
    contacts: "ContactsBook"
    notes: Any = dc_field(default_factory=dict)     # → NotesBook later
    module: str | None = None         # "contacts" | "notes" | "tags" | None
    entity_key: str | None = None     # name / title / tag, or None

    contacts_sort: tuple[str, bool] = ("name", False)
    notes_sort: tuple[str, bool] = ("title", False)
    tags_sort: tuple[str, bool] = ("name", False)

    @property
    def context(self) -> str:
        if self.module is None:
            return CTX_ROOT
        if self.entity_key is None:
            return {
                "contacts": CTX_CONTACTS,
                "notes": CTX_NOTES,
                "tags": CTX_TAGS,
            }[self.module]
        return {
            "contacts": CTX_CONTACT,
            "notes": CTX_NOTE,
            "tags": CTX_TAG,
        }[self.module]

    def prompt(self) -> str:
        if self.module is None:
            return "> "
        if self.entity_key is None:
            return f"{self.module}> "
        return f"{self.module}/{self.entity_key}> "

    def enter_module(self, name: str) -> None:
        self.module = name
        self.entity_key = None

    def enter_entity(self, key: str) -> None:
        self.entity_key = key

    def go_up(self) -> None:
        if self.entity_key is not None:
            self.entity_key = None
        elif self.module is not None:
            self.module = None

    def go_root(self) -> None:
        self.module = None
        self.entity_key = None