# Personal Assistant

# Solution Architecture Specification

## Cloud Operating Environment

Personal Assistant does not operate in a cloud environment. It is a local, single-user Python CLI application.

### Runtime Environment

| Area | Specification |
| :---- | :---- |
| Hardware platform | User's local machine |
| Operating system | macOS, Linux, or another OS capable of running Python and the required packages |
| Runtime | Python 3.x |
| Entry point | `python -m personal_assistant`; optional launchers `personal-assistance.sh` and `personal-assistance.bat` |
| User location | Local terminal session |
| Server location | Not applicable |
| Database location | Not applicable; data is stored in local pickle files |
| Hosting organization | Not applicable |
| Required software | Python 3.10+, `rich`, `prompt_toolkit`, `rapidfuzz` |

### Local Storage

The application stores user data in the user's home directory:

```text
~/.personal-assistant/
  contacts.pkl
  notes.pkl
```

No new technical infrastructure, network service, cloud account, database server, or hosted website is required.

## Assumptions and Dependencies

### Assumptions

- Users can run Python locally.
- Users interact with the application through a terminal.
- The application is single-user and offline.
- Pickle persistence is acceptable for course-project scope.
- Data volume is personal-scale: a few hundred contacts and notes, not enterprise-scale datasets.
- Feature modules are integrated through command registration and TL-controlled imports.
- The current user experience is context-aware: root context, module context, and entity context.
- The demo seed command may overwrite local pickle data when run with `--force`.

### Dependencies

| Dependency | Purpose | Impact if Missing |
| :---- | :---- | :---- |
| Python runtime | Executes the application | Application cannot run |
| `rich` | Rich table rendering | Tables fall back or fail depending on integration |
| `prompt_toolkit` | REPL input, history, completer, toolbar | Interactive REPL cannot operate as designed |
| `rapidfuzz` | Fuzzy command suggestion and contact suggestion | Typo suggestions and fuzzy matching fail |
| Local filesystem | Stores pickle files | Data cannot persist |
| Launcher scripts | Start the app consistently across platforms | Users must run the module command manually |
| Demo seed loader | Creates repeatable review data | Manual demo setup takes longer |
| GitHub | Development workflow and final evidence | Branch/PR evidence unavailable |
| Trello | Task tracking | Card workflow evidence unavailable |

## System Structure and Features Allocation

The solution is divided into independent software items. Each item owns a clear part of the functional scope and communicates with other items through explicit data objects, command handlers, or helper APIs.

### SI-01 REPL Application

**Package:** `personal_assistant/app.py`, `personal_assistant/__main__.py`, `personal-assistance.sh`, `personal-assistance.bat`

**Description:** Starts the application, loads state, reads user input, tracks context, dispatches commands, prints returned strings, and saves state on exit.

**Related use cases:**

- UC-UX-HELP
- UC-UX-FUZZY
- UC-PERS-SAVE
- UC-PERS-LOAD

**Flow responsibility:**

1. Read line from terminal.
2. Tokenize line.
3. Handle global commands (`help`, `?`, `..`, `/`, `exit`, `quit`, `q`).
4. Resolve command in the current context.
5. If inside a module, try entity-enter by name/title/tag.
6. Call handler with `(args, state)`.
7. Auto-show entity card after successful entity entry.
8. Print response.
9. Save contacts and notes on exit.

### SI-02 Core Infrastructure

**Package:** `personal_assistant/core/`

**Description:** Provides shared infrastructure: context-aware command registry, error decorator, base field type, application state, local paths, and pickle storage.

**Related use cases:**

- All command use cases.
- UC-PERS-SAVE
- UC-PERS-LOAD

**Flow responsibility:**

- `registry.py`: stores commands registered by context (`root`, `contacts`, `contacts/*`, `notes`, `notes/*`, `tags`, `tags/*`).
- `decorators.py`: converts common exceptions into user-facing strings.
- `storage.py`: saves and loads pickle files.
- `paths.py`: resolves `~/.personal-assistant/` paths.
- `state.py`: holds contacts and notes books, current module, current entity key, prompt derivation, and remembered sort settings.

### SI-03 Contacts Module

**Package:** `personal_assistant/contacts/`

**Description:** Owns contact data fields, contact records, contacts book operations, and contact commands.

**Related use cases:**

- UC-CONT-ADD
- UC-CONT-EDIT
- UC-CONT-DELETE
- UC-CONT-FIND
- UC-CONT-LIST
- UC-BDAY-ADD
- UC-BDAY-LIST

**Flow responsibility:**

- Validate contact fields.
- Store records in `ContactsBook`.
- Search, sort, and list contacts.
- Calculate upcoming birthdays.
- Store note links as UUIDs.
- Provide module and entity-context handlers.

### SI-04 Notes Module

**Package:** `personal_assistant/notes/`

**Description:** Owns note data model, notes collection keyed by normalized title, note commands, tag extraction, phone extraction, and contact suggestions.

**Related use cases:**

- UC-NOTE-ADD
- UC-NOTE-EDIT
- UC-NOTE-DELETE
- UC-NOTE-FIND
- UC-NOTE-LIST
- UC-LINK-ADD
- UC-LINK-REMOVE
- UC-TAG-AUTO

**Flow responsibility:**

- Create title-based, UUID-backed notes.
- Enforce title uniqueness and support note rename.
- Search note title, text, tags, and linked contacts.
- Suggest contacts mentioned in note text.
- Link notes to contacts.
- Provide multi-line note creation and edit flows.

### SI-05 Tags Module

**Package:** `personal_assistant/tags/`

**Description:** Implements tags as a virtual module over contact and note tag lists. It has no separate persistence file.

**Related use cases:**

- UC-TAG-LIST
- UC-TAG-FIND
- UC-TAG-SORT
- UC-TAG-RENAME
- UC-TAG-MERGE

**Flow responsibility:**

- Aggregate tag counts across contacts and notes.
- Find contacts and notes by tag.
- Rename, merge, and delete tags across both books.
- Deduplicate tags per entity after bulk updates.
- Provide tag entity views with related contacts and notes.

### SI-06 UI Helpers

**Package:** `personal_assistant/ui/`

**Description:** Provides input tokenization, context-aware completion, fuzzy suggestions, context help, and Rich table/card rendering.

**Related use cases:**

- UC-UX-HELP
- UC-UX-COMPLETE
- UC-UX-FUZZY
- UC-UX-PARSE
- UC-CONT-LIST
- UC-NOTE-LIST
- UC-TAG-LIST

**Flow responsibility:**

- Parse input with quote-aware tokenization.
- Render command help from the registry.
- Render contacts, notes, and tags as tables and single-entity views.
- Suggest likely commands for typos.
- Offer entity name completion in module contexts.

### SI-07 Demo Seed Loader

**Package:** `personal_assistant/seed.py`

**Description:** Creates a repeatable demonstration dataset for manual review.

**Related use cases:**

- UC-DOC-SMOKE
- UC-PERS-LOAD

**Flow responsibility:**

- Create 15 contacts and 15 notes.
- Add shared tags and note-contact links.
- Write demo data to the same local pickle files used by the runtime app.
- Warn that existing local data is overwritten when seeding with `--force`.

### Feature Allocation Matrix

| Feature | REPL | Core | Contacts | Notes | Tags | UI |
| :---- | :--: | :--: | :--: | :--: | :--: | :--: |
| Contact CRUD |  |  | X |  |  | X |
| Birthday lookup |  |  | X |  |  | X |
| Note CRUD |  |  |  | X |  | X |
| Note-contact linking |  | X | X | X |  |  |
| Tag operations |  |  |  |  | X | X |
| Context navigation | X | X |  |  |  | X |
| Command dispatch | X | X |  |  |  |  |
| Help, parser, completion |  |  |  |  |  | X |
| Persistence | X | X | X | X |  |  |
| Demo seed data |  | X | X | X | X |  |

## Data Requirements

### Logical Data Model

```text
ContactsBook
  key: contact name
  value: Record

Record
  name: Name
  phones: list[Phone]
  email: Email | None
  address: Address | None
  birthday: Birthday | None
  tags: list[Tag]
  linked_note_ids: list[UUID]
  created_at: datetime

NotesBook
  key: normalized note title
  value: Note

Note
  id: UUID
  title: str
  text: str
  tags: list[Tag]
  linked_contact_names: list[str]
  created_at: datetime
  updated_at: datetime

Tag
  value: str

TagInfo
  name: str
  contact_count: int
  note_count: int
  total: int
```

### Relationships

```text
Record 0..* -------- M:N -------- 0..* Note
   |                                 |
   | linked_note_ids: UUID           | linked_contact_names: str
   v                                 v
Note.id                          Record.name.value

Record 0..* ---- uses ----> Tag
Note   0..* ---- uses ----> Tag

Tags module = aggregation over Record.tags + Note.tags
```

### Data Dictionary

| Data Element | Type | Format / Rules |
| :---- | :---- | :---- |
| Contact name | `Name` | Non-empty trimmed string |
| Phone | `Phone` | Canonical 10 digits; accepts separators and `+380` / `380` prefix |
| Email | `Email` | Simple email regex validation |
| Address | `Address` | Trimmed string, at least 3 characters |
| Birthday | `Birthday` | `DD.MM.YYYY` |
| Contact tags | `list[Tag]` | Normalized lowercase slugs |
| Linked note IDs | `list[UUID]` | UUIDs of linked notes |
| Note ID | `UUID` | Generated by UUID4 |
| Note title | `str` | Non-empty, unique case-insensitive title |
| Note text | `str` | Free-form user text |
| Note tags | `list[Tag]` | Normalized lowercase slugs |
| Linked contact names | `list[str]` | Contact display names |
| Created / updated timestamps | `datetime` | Python datetime |
| TagInfo counts | `int` | Contact count, note count, total |

### Reports

The system produces console reports only:

- Contacts table.
- Contact card.
- Upcoming birthdays table.
- Notes table.
- Note card.
- Tags table.
- Find-by-tag combined result.
- Grouped help output.
- Root/module/entity prompts.
- Error and validation messages.

### Data Integrity and Retention

- Contacts and notes are saved to local pickle files on exit.
- Pickle save uses an atomic write approach to reduce corruption risk.
- The data directory is created automatically if missing.
- Pickle files are ignored by git and must not be committed.
- Tags are not stored separately; they are retained only as part of contacts and notes.
- Delete commands remove records from the in-memory books and the change is persisted on exit.

## External Interface Requirements

### User Interfaces

The user interface is a terminal REPL with hierarchical context navigation.

Key UI behaviors:

- Root prompt is `>`.
- Module prompts are `contacts>`, `notes>`, and `tags>`.
- Entity prompts include the active object, for example `contacts/Alice Johnson>`.
- `help` lists commands available in the current context.
- `?` acts as help alias.
- `..` moves one level up and `/` returns to root.
- Typing an entity name/title/tag inside the matching module enters that entity.
- Entity cards are shown automatically after successful entity entry.
- Tab completion suggests commands and entity names.
- Unknown commands trigger fuzzy suggestions when a close match exists.
- List commands render readable tables.
- Handlers return strings; the REPL owns printing.

### Software Interfaces

| Interface | Direction | Data / Message |
| :---- | :---- | :---- |
| `tokenize(line)` | REPL -> UI parser | Raw line to tokens |
| `REGISTRY[state.context]` | REPL -> handlers | Context-specific command lookup |
| `AppState.context` | REPL -> registry | Derived root/module/entity context |
| `handler(args, state)` | REPL -> domain module | Args and mutable app state |
| `PickleStorage.load/save` | Core -> filesystem | Python objects serialized as pickle |
| `render_*` functions | Handlers -> UI | Domain objects to plain string output |
| `suggest_command` | REPL -> UI fuzzy helper | Unknown token and candidate commands |
| `fuzzy_match_all` | REPL -> UI fuzzy helper | Entity-enter matching |

Runtime third-party libraries:

- `prompt_toolkit`: interactive input, history, completion.
- `rich`: table rendering.
- `rapidfuzz`: fuzzy suggestions.

### Communications Interfaces

The runtime application has no network communications interface. It does not send email, call APIs, open web browsers, or connect to a database server.

Project workflow communications are outside runtime scope:

- GitHub for code review and PR links.
- Trello for card tracking.

## Non-functional Requirements

### Usability

- The system shall provide `help` output with command names and format hints.
- The system shall support tab completion for commands and current-context entity names.
- The system shall suggest likely commands after typos.
- The system shall preserve argument case while normalizing command names.
- The system shall display validation failures as friendly messages, not tracebacks.
- The system shall expose clear prompts so users know their current context.

### Performance

- The system targets personal-scale data.
- Linear scans for contacts, notes, and tags are acceptable for a few hundred records.
- Common REPL commands should feel immediate on a local machine.

### Security and Privacy

- User data shall remain local to the user's machine.
- The runtime application shall not transmit contacts or notes over a network.
- Pickle files shall be excluded from source control.
- The application is single-user and does not implement authentication or authorization.

### Safety

- Invalid user input shall not crash the REPL.
- Malformed quoted input shall fall back to simple splitting.
- Unknown commands shall not mutate data.
- Delete operations shall be explicit commands.
- Seed overwrite requires an explicit seed command and README warning.
- Save operations shall use atomic write behavior where possible.

### Internationalization

- User-facing implementation and project documentation use English.
- Original assignment materials may be Ukrainian, but localized runtime UI is out of scope.
- Dates for birthdays use `DD.MM.YYYY`.

## Architecture Models

### Package Model

```text
personal_assistant/
  __main__.py
  app.py
  seed.py
  core/
  contacts/
  notes/
  tags/
  ui/
personal-assistance.sh
personal-assistance.bat
```

### Command Dispatch Model

```text
User input
  |
  v
ui.parser.tokenize
  |
  v
(first token, args)
  |
  v
global command? -- yes --> navigation/help/exit
  |
  no
  |
  v
core.registry.REGISTRY[state.context]
  | command found                 | no
  v                              v
handler(args, state)             ui.fuzzy.suggest_command
  |                              |
  |                              v
  |                         entity-enter check
  |                              |
  v                              v
response string                  unknown-command response
  |
  v
app.py prints response
```

### Data Flow Model

```text
Application start
  |
  v
PickleStorage.load contacts + notes
  |
  v
AppState
  |-- contacts
  |-- notes
  |-- module
  |-- entity_key
  |
  v
REPL command handlers mutate state
  |
  v
Application exit
  |
  v
PickleStorage.save contacts + notes
```

### Feature Tree

```text
Personal Assistant
  |-- Contacts
  |   |-- add/edit/delete
  |   |-- search/list
  |   |-- birthdays
  |   |-- validation
  |
  |-- Notes
  |   |-- add/edit/delete
  |   |-- search/list
  |   |-- tags
  |   |-- links to contacts
  |
  |-- Tags
  |   |-- aggregate
  |   |-- find/sort
  |   |-- rename/merge
  |
  |-- UI
  |   |-- parser
  |   |-- help
  |   |-- completion
  |   |-- rich tables/cards
  |   |-- fuzzy suggestions
  |
  |-- Demo
  |   |-- seed loader
  |   |-- launcher scripts
  |
  |-- Persistence
      |-- contacts.pkl
      |-- notes.pkl
```

### State Transition Model

```text
Not running
  |
  | python -m personal_assistant
  v
Running / waiting for command
  |
  | contacts / notes / tags
  v
Module context
  |
  | entity name/title/tag
  v
Entity context
  |
  | .. or /
  v
Running / waiting for command
  |
  | valid command
  v
Executing handler
  |
  | response returned
  v
Running / waiting for command
  |
  | exit / quit / q
  v
Saving state
  |
  v
Not running
```
