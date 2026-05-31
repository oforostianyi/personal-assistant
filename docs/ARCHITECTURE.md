# Architecture

## Package Map

```text
personal_assistant/
├── __main__.py           # python -m personal_assistant entry
├── app.py                # REPL loop, context dispatch, global navigation
├── seed.py               # demo data loader
├── core/                 # shared infrastructure
│   ├── fields.py         # Field base class
│   ├── decorators.py     # @input_error
│   ├── registry.py       # context-aware @command registry
│   ├── storage.py        # PickleStorage
│   ├── paths.py          # ~/.personal-assistant/* paths
│   └── state.py          # AppState: books + module/entity context
├── contacts/             # contact fields, records, book, context commands
├── notes/                # note model, book, parser/tagger, context commands
├── tags/                 # virtual tag aggregation and tag context commands
└── ui/                   # tokenizer, completer, fuzzy, help, Rich views
```

Launcher scripts:

```text
personal-assistance.sh
personal-assistance.bat
```

## Context Model

The REPL is context-aware. `AppState` stores:

- `contacts`: contacts book
- `notes`: notes book
- `module`: `contacts`, `notes`, `tags`, or `None`
- `entity_key`: active contact name, note title, tag name, or `None`

The prompt is derived from that state:

```text
>                         # root
contacts>                 # module
notes/Project kickoff>    # entity
```

Navigation commands:

- `contacts`, `notes`, `tags`: enter a module from root.
- `..`: move one level up.
- `/`: return to root.
- `exit`, `quit`, `q`: save and close.

## Command Registry

Each handler registers for a concrete context:

```text
root
contacts
contacts/*
notes
notes/*
tags
tags/*
```

`core.registry.REGISTRY` maps context names to command dictionaries. Aliases point to the same `Command` object. `commands_for(context)` returns unique primary commands for help and completion.

## Dispatch Flow

```text
user input
  |
  v
ui.parser.tokenize(line)
  |
  v
global command? ---- yes ---> help/navigation/exit
  |
  no
  |
  v
REGISTRY[state.context][first_token]?
  | yes
  v
handler(args, state) -> response
  |
  no
  |
  v
module entity-enter?
  | yes -> state.enter_entity(...) -> auto show entity card
  | no  -> fuzzy command suggestion or unknown-command message
```

## Entity Enter

Inside `contacts>`, `notes>`, or `tags>`, typing an existing entity name/title/tag opens that entity. Exact case-insensitive matches are preferred. Substring and fuzzy matches are used when appropriate. Multiple matches return a numbered list instead of guessing.

If no contact or note matches, the app may offer to create a new entity.

## Data Flow

```text
Application start
  |
  v
PickleStorage.load contacts.pkl + notes.pkl
  |
  v
AppState
  |
  v
Context handlers mutate contacts / notes / tags
  |
  v
Application exit
  |
  v
PickleStorage.save contacts.pkl + notes.pkl
```

Storage location:

```text
~/.personal-assistant/
  contacts.pkl
  notes.pkl
```

## Contacts And Notes

Contacts are keyed by contact name. Notes are keyed by normalized title for user-facing entity navigation and keep a stable UUID internally.

Relationships are many-to-many:

```text
Record.linked_note_ids      links with      Note.linked_contact_names
```

Handlers keep both sides synchronized when linking, unlinking, deleting, or renaming relevant data.

## Tags

Tags are virtual. There is no separate tag pickle file. The tags module aggregates tags from contacts and notes on demand.

Supported tag operations include:

- list and sort tag usage
- find tags
- open tag entity
- list contacts/notes for a tag
- rename tags across contacts and notes
- merge tags
- delete tags from all entities

## UI Helpers

The `ui/` package owns presentation and input assistance:

- `parser.py`: quote-aware tokenization
- `completer.py`: context-aware command and entity completion
- `fuzzy.py`: command suggestions and entity matching
- `help.py`: context help from registry
- `views.py` / `tables.py`: Rich table and card rendering

## Demo Seed

`python -m personal_assistant.seed --force` writes a repeatable demo dataset: 15 contacts, 15 notes, shared tags, links, and useful birthday dates. It overwrites the local pickle files, so it is intended for demo/review setup rather than normal user operation.
