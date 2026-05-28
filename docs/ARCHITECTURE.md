# Architecture

## Package map

```
personal_assistant/
├── __main__.py           # `python -m personal_assistant` entry
├── app.py                # REPL loop + dispatch + built-in hello/help (TL)
├── core/                 # Shared infrastructure (TL)
│   ├── fields.py         # Field base class
│   ├── decorators.py     # @input_error
│   ├── registry.py       # @command + COMMAND_REGISTRY (flat dict)
│   ├── storage.py        # Storage ABC + PickleStorage (atomic)
│   ├── paths.py          # ~/.personal-assistant/* paths
│   └── state.py          # AppState dataclass
├── contacts/             # Contacts module (TL)
│   ├── fields.py         # Name, Phone, Email, Address, Birthday, Tag
│   ├── record.py         # Record
│   ├── book.py           # ContactsBook(UserDict[str, Record])
│   └── handlers.py       # add-contact, edit-contact, ...
├── notes/                # Notes module (Person 2)
│   ├── note.py           # Note (UUID, text, tags, links, timestamps)
│   ├── book.py           # NotesBook(UserDict[UUID, Note])
│   ├── tagger.py         # auto-extract tags from text
│   ├── text_parser.py    # extract phones/names, suggest links
│   └── handlers.py       # add-note, find-note, link-note, ...
├── tags/                 # Tags module (Person 3) — virtual, no separate file
│   ├── aggregator.py     # collect_tags(state) — walks both books
│   └── handlers.py       # list-tags, find-by-tag, rename-tag, merge-tags
└── ui/                   # UI helpers
    ├── parser.py         # parse_input (TL→P4)
    ├── completer.py      # WordCompleter + bottom toolbar (TL)
    ├── fuzzy.py          # suggest_command — rapidfuzz wrapper (TL)
    ├── tables.py         # rich.Table renderers (P4)
    └── help.py           # autogen help from registry (P4)
```

## Command dispatch

Flat. Each handler registers itself with `@command(name, aliases=..., format=..., help_=...)`. `app.py` looks up by lowercased first token; on miss, suggests via fuzzy.

```
user input → parse_input → (cmd, args)
                              │
                              ▼
                      COMMAND_REGISTRY[cmd]?
                       ├── yes → handler(args, state) → response string
                       └── no  → suggest_command(...) → "Did you mean ...?"
```

## Data flow

```
PromptSession      ← reads keystrokes, runs WordCompleter on Tab,
   │                  pulls bottom_toolbar(text) on each render
   ▼
app._dispatch ────► handler(args, state)
                          │
                          ├─ mutates state.contacts / state.notes
                          └─ returns response string

on exit:
   PickleStorage.save(state.contacts, contacts_path())
   PickleStorage.save(state.notes,    notes_path())
```

## M:N contacts ↔ notes

A `Record` holds `linked_note_ids: list[UUID]`. A `Note` holds
`linked_contact_names: list[str]`. Both sides must be updated in sync.
The team agrees: a single service function
`link_note(record, note)` in `contacts/book.py` mutates both. Handlers
on either side call that function — they never edit the other side's
list directly.

## Tags as a virtual module

`tags/` does **not** have its own pickle file. `tags/aggregator.py`
provides `collect_tags(state)` which walks both books on demand and
returns a list of unique tag names. `rename-tag` and `merge-tag` are
bulk updates: they iterate both books and replace the tag in every
record and note that uses it.