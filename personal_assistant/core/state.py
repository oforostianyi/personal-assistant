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
from typing import Any


@dataclass
class AppState:
    contacts: Any = dc_field(default_factory=dict)  # → ContactsBook later
    notes: Any = dc_field(default_factory=dict)     # → NotesBook later