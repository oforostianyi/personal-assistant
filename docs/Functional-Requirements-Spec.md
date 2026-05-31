# Personal Assistant

# Functional Requirements Specification

## Product Perspective

Personal Assistant is an entirely new offline console application built as a final Python team project. It is not a replacement for an existing production system and is not part of a commercial product line.

The product relates to the larger project workflow through GitHub, Trello, and final defense documentation, but the runtime system itself is standalone. The application runs locally, stores data in the user's home directory, and does not integrate with external services.

### Context Diagram

```text
User
  |
  | commands via terminal
  v
Personal Assistant REPL
  |
  | tracks root/module/entity context
  | dispatches context commands
  v
Domain modules
  |-- Contacts
  |-- Notes
  |-- Tags
  |-- UI helpers
  |
  | save/load
  v
Local files under ~/.personal-assistant/
  |-- contacts.pkl
  |-- notes.pkl
```

Primary runtime interfaces:

- **Command-line REPL:** user enters commands and receives text/table output.
- **Local persistence:** contacts and notes are saved as pickle files.
- **Context-aware command registry:** handlers are registered for root, module, or entity contexts.
- **Demo seed loader:** optional local command creates sample review data.

Out-of-runtime project interfaces:

- **GitHub:** source control and PR evidence.
- **Trello:** task tracking.
- **Documentation artifacts:** README, requirements documents, screenshots, smoke results.

## User Roles and Characteristics

### UR-01 End User

The end user runs the CLI locally and uses it to manage contacts, birthdays, notes, and tags. The user is comfortable typing commands, reading help output, and running Python from a terminal.

Important characteristics:

- Wants quick lookup and editing of personal data.
- Benefits from context prompts such as `contacts>` and `notes/Project kickoff>`.
- Needs data to survive application restarts.
- Benefits from command suggestions and help because command syntax may be unfamiliar.

### UR-02 Course Curator / Evaluator

The evaluator reviews the final project against the original assignment checklist and defense materials.

Important characteristics:

- Needs a reproducible demo.
- Needs clear documentation and visible evidence of team collaboration.
- Reviews feature completeness, not commercial scalability.

### UR-03 Team Lead

The team lead owns integration, module wiring, and current behavior alignment between README, code, and requirements.

Important characteristics:

- Needs modular feature branches that can be reviewed independently.
- Needs handlers to register commands in the correct root/module/entity contexts.
- Needs final smoke evidence after integration.

### UR-04 Module Owner

Module owners implement Contacts, Notes, Tags, and UI features.

Important characteristics:

- Work in separate feature branches.
- Need clear module boundaries.
- Must not edit TL-only integration files unless explicitly assigned.

## System Features

### SF-01 Contact Management

**Priority:** High
**Business trace:** BRD F-01 Contact Management [MVP]

The system shall allow users to create, read, search, edit, and delete contacts. Contacts shall support name, phone, email, address, birthday, tags, and linked note IDs.

#### Functional Requirements

- **FR-CONT-001:** The system shall allow adding a contact with a name and phone number.
- **FR-CONT-002:** The system shall validate phone numbers and reject invalid formats with a user-friendly message.
- **FR-CONT-003:** The system shall allow editing phone, email, address, birthday, and tag fields.
- **FR-CONT-004:** The system shall validate email addresses when they are added or edited.
- **FR-CONT-005:** The system shall allow deleting a contact by name.
- **FR-CONT-006:** The system shall allow searching contacts by name, phone, email, address, and tags.
- **FR-CONT-007:** The system shall allow listing all contacts in a readable table.
- **FR-CONT-008:** The system shall allow sorting contacts by supported contact sort fields.
- **FR-CONT-009:** The system shall allow filtering contacts by tag.
- **FR-CONT-010:** The system shall show a contact card inside a contact entity context.

#### Use Cases

| Use Case | Primary Actor | Reference |
| :---- | :---- | :---- |
| Add contact | End User | UC-CONT-ADD |
| Edit contact | End User | UC-CONT-EDIT |
| Delete contact | End User | UC-CONT-DELETE |
| Find/filter/sort contact | End User | UC-CONT-FIND |
| List contacts | End User | UC-CONT-LIST |
| Open contact entity | End User | UC-CONT-OPEN |

### SF-02 Birthday Lookup

**Priority:** High
**Business trace:** BRD F-02 Birthday Lookup [MVP]

The system shall show contacts whose birthdays occur within a user-specified number of days.

#### Functional Requirements

- **FR-BDAY-001:** The system shall allow storing a contact birthday in `DD.MM.YYYY` format.
- **FR-BDAY-002:** The system shall allow the user to request upcoming birthdays for a specified number of days.
- **FR-BDAY-003:** The system shall return a user-readable result when no birthdays are found.
- **FR-BDAY-004:** The system shall calculate upcoming birthdays relative to the current date.

#### Use Cases

| Use Case | Primary Actor | Reference |
| :---- | :---- | :---- |
| Add birthday | End User | UC-BDAY-ADD |
| Show upcoming birthdays | End User | UC-BDAY-LIST |

### SF-03 Note Management

**Priority:** High
**Business trace:** BRD F-03 Note Management [MVP]

The system shall allow users to create, edit, search, list, rename, and delete notes. In the user interface, notes are opened by title from the `notes>` module. Internally, notes still keep stable UUID identifiers for links and persistence.

#### Functional Requirements

- **FR-NOTE-001:** The system shall create a note with a title and multi-line body text.
- **FR-NOTE-002:** The system shall assign each note a stable UUID.
- **FR-NOTE-003:** The system shall enforce case-insensitive note-title uniqueness.
- **FR-NOTE-004:** The system shall allow replacing note body text.
- **FR-NOTE-005:** The system shall allow deleting a note.
- **FR-NOTE-006:** The system shall allow searching notes by title and body text.
- **FR-NOTE-007:** The system shall allow listing notes in a readable table.
- **FR-NOTE-008:** The system shall preserve note timestamps for creation and updates.
- **FR-NOTE-009:** The system shall allow renaming a note title.
- **FR-NOTE-010:** The system shall allow sorting notes by supported note sort fields.
- **FR-NOTE-011:** The system shall allow filtering notes by tag or linked contact.
- **FR-NOTE-012:** The system shall show a note card inside a note entity context.

#### Use Cases

| Use Case | Primary Actor | Reference |
| :---- | :---- | :---- |
| Add note | End User | UC-NOTE-ADD |
| Edit note | End User | UC-NOTE-EDIT |
| Delete note | End User | UC-NOTE-DELETE |
| Find note | End User | UC-NOTE-FIND |
| List notes | End User | UC-NOTE-LIST |
| Rename note | End User | UC-NOTE-RENAME |
| Open note entity | End User | UC-NOTE-OPEN |

### SF-04 Note-Contact Linking

**Priority:** Medium
**Business trace:** BRD F-04 Note-Contact Linking

The system shall support many-to-many links between notes and contacts.

#### Functional Requirements

- **FR-LINK-001:** The system shall allow linking an existing note to an existing contact.
- **FR-LINK-002:** The system shall allow unlinking a note from a contact.
- **FR-LINK-003:** The system shall keep contact-side note IDs and note-side contact names synchronized.
- **FR-LINK-004:** The system shall remove dangling links when a linked note is deleted.

#### Use Cases

| Use Case | Primary Actor | Reference |
| :---- | :---- | :---- |
| Link note to contact | End User | UC-LINK-ADD |
| Unlink note from contact | End User | UC-LINK-REMOVE |

### SF-05 Tag Management

**Priority:** Medium
**Business trace:** BRD F-05 Tag Management [DIFFERENTIATOR]

The system shall support tags as normalized keywords attached to contacts and notes.

#### Functional Requirements

- **FR-TAG-001:** The system shall extract explicit hashtags from note text.
- **FR-TAG-002:** The system shall infer known tags from note text when the word already exists as a tag.
- **FR-TAG-003:** The system shall list tags with contact count, note count, and total count.
- **FR-TAG-004:** The system shall find contacts and notes by tag.
- **FR-TAG-005:** The system shall sort tags by usage.
- **FR-TAG-006:** The system shall rename a tag across contacts and notes.
- **FR-TAG-007:** The system shall merge one tag into another across contacts and notes.
- **FR-TAG-008:** The system shall deduplicate tags per entity after rename or merge.
- **FR-TAG-009:** The system shall allow deleting a tag from all contacts and notes.
- **FR-TAG-010:** The system shall show a tag card inside a tag entity context.
- **FR-TAG-011:** The system shall list contacts and notes for the current tag entity.

#### Use Cases

| Use Case | Primary Actor | Reference |
| :---- | :---- | :---- |
| Auto-tag note | End User | UC-TAG-AUTO |
| List tags | End User | UC-TAG-LIST |
| Find by tag | End User | UC-TAG-FIND |
| Sort by tag | End User | UC-TAG-SORT |
| Rename tag | End User | UC-TAG-RENAME |
| Merge tags | End User | UC-TAG-MERGE |
| Delete tag | End User | UC-TAG-DELETE |
| Open tag entity | End User | UC-TAG-OPEN |

### SF-06 Console UX

**Priority:** Medium
**Business trace:** BRD F-06 Console UX [DIFFERENTIATOR]

The system shall provide a usable command-line interface with command discovery and readable output.

#### Functional Requirements

- **FR-UX-001:** The system shall provide a `help` command with context-specific command information.
- **FR-UX-002:** The system shall support `?` as an alias for `help`.
- **FR-UX-003:** The system shall provide tab completion for command names and available entity names in the current context.
- **FR-UX-004:** The system shall suggest a likely command when the user types an unknown command close to a known command.
- **FR-UX-005:** The system shall parse quoted arguments as single arguments.
- **FR-UX-006:** The system shall normalize command names to lower case while preserving argument case.
- **FR-UX-007:** The system shall render list outputs and entity views as readable text or Rich tables/cards.
- **FR-UX-008:** The system shall return friendly validation and lookup errors instead of tracebacks.
- **FR-UX-009:** The system shall support context navigation from root to `contacts`, `notes`, and `tags`.
- **FR-UX-010:** The system shall support `..` for one level up and `/` for root navigation.
- **FR-UX-011:** The system shall allow entering an entity by typing its contact name, note title, or tag name inside the corresponding module.
- **FR-UX-012:** The system shall auto-show an entity card after successful entity entry.

#### Use Cases

| Use Case | Primary Actor | Reference |
| :---- | :---- | :---- |
| Show help | End User | UC-UX-HELP |
| Use command completion | End User | UC-UX-COMPLETE |
| Recover from typo | End User | UC-UX-FUZZY |
| Enter quoted note text | End User | UC-UX-PARSE |
| Navigate context tree | End User | UC-UX-NAVIGATE |

### SF-07 Persistence

**Priority:** High
**Business trace:** BRD F-07 Persistence [MVP]

The system shall store user data locally and reload it on subsequent launches.

#### Functional Requirements

- **FR-PERS-001:** The system shall save contacts to `~/.personal-assistant/contacts.pkl`.
- **FR-PERS-002:** The system shall save notes to `~/.personal-assistant/notes.pkl`.
- **FR-PERS-003:** The system shall load existing contacts and notes when the application starts.
- **FR-PERS-004:** The system shall create the data directory if it does not exist.
- **FR-PERS-005:** The system shall not commit user pickle files to source control.

#### Use Cases

| Use Case | Primary Actor | Reference |
| :---- | :---- | :---- |
| Exit and save | End User | UC-PERS-SAVE |
| Relaunch and load data | End User | UC-PERS-LOAD |

### SF-08 Project Documentation and Defense Evidence

**Priority:** Medium
**Business trace:** defense readiness and final review evidence

The project shall provide documentation and evidence required for final review.

#### Functional Requirements

- **FR-DOC-001:** The project shall include a README with features, quick start, architecture link, scope, and credits.
- **FR-DOC-002:** The project shall include business and functional requirements documents.
- **FR-DOC-003:** The project shall include smoke-test results after final integration.
- **FR-DOC-004:** The project shall include screenshots or other evidence for final defense where required.
- **FR-DOC-005:** The project shall include a git history artifact showing collaboration evidence where required.
- **FR-DOC-006:** The README shall include launcher commands, seed-data instructions, and a manual walkthrough that matches the current REPL behavior.

### SF-09 Demo Seed and Easy Run Support

**Priority:** Medium
**Business trace:** BRD F-08 Demo and Easy Run Support [MVP]

The project shall provide local utilities that make review and demonstration repeatable.

#### Functional Requirements

- **FR-DEMO-001:** The system shall provide `python -m personal_assistant.seed --force` to create demo contacts and notes.
- **FR-DEMO-002:** The seed command shall clearly indicate that it overwrites existing local pickle data.
- **FR-DEMO-003:** The demo dataset shall include linked contacts and notes, shared tags, and birthdays suitable for the README walkthrough.
- **FR-DEMO-004:** The project shall include a POSIX launcher script for macOS/Linux.
- **FR-DEMO-005:** The project shall include a Windows batch launcher.
- **FR-DEMO-006:** Launcher scripts shall prefer the local virtual environment when present and start the app from the project root.

#### Use Cases

| Use Case | Primary Actor | Reference |
| :---- | :---- | :---- |
| Review README | Course Curator / Evaluator | UC-DOC-README |
| Review smoke results | Course Curator / Evaluator | UC-DOC-SMOKE |
| Review team evidence | Course Curator / Evaluator | UC-DOC-HISTORY |

## Error Handling and Alternative Flows

### EF-01 Empty or Missing Arguments

If a user enters a command without required arguments, the system shall return a usage message for that command instead of raising a traceback.

Examples:

- `filter tag` -> `Usage: filter tag TAG`
- `rename` inside a note entity -> `Usage: rename NEW_TITLE`
- `new` inside notes -> `Usage: new [title]`

### EF-02 Invalid Field Values

If a user enters invalid contact or tag data, the system shall return the validator's human-readable message.

Examples:

- Invalid phone number -> message explaining the accepted phone format.
- Invalid email -> message explaining that the email is invalid.
- Invalid tag -> message explaining allowed tag characters.

### EF-03 Missing Records

If a user refers to a missing contact, note, or tag, the system shall return a friendly not-found message. The application shall continue running.

Examples:

- Missing note title -> `Not found: TITLE.`
- Missing contact name -> `Not found: NAME.`
- Missing tag -> `Nothing tagged TAG.`

### EF-04 Ambiguous Entity Entry

If a module-level entity entry matches multiple contacts, notes, or tags, the system shall return a numbered ambiguity message and require the user to type the exact name or refine the query. The system shall not choose an entity automatically.

### EF-05 Malformed Quoted Input

If the parser receives a line with an unmatched quote, it shall fall back to whitespace splitting and shall not crash the REPL.

### EF-06 Duplicate or Idempotent Operations

If a user repeats an operation that is already satisfied, the system shall avoid duplicate data and return a stable response.

Examples:

- Adding an existing tag to the same entity shall not duplicate the tag.
- Linking an already linked note and contact shall keep one link.
- Renaming an entity to its existing name shall return a stable no-op response where applicable.
- Merging a tag into itself shall return a friendly self-merge error.

## Quality Attributes

### QA-01 Usability

The system shall provide discoverable commands through context-specific `help`, command format hints, entity-enter hints, and tab completion. Unknown commands close to a registered command shall produce a fuzzy suggestion.

Verification:

- Manual REPL demo with `help` in root, module, and entity contexts.
- Manual typo demo such as `contatcs`.
- Parser edge-case assertions for whitespace and quoted arguments.

### QA-02 Reliability and Persistence

The system shall save contacts and notes on exit and load them on the next launch. Data shall be stored in the user's home directory under `~/.personal-assistant/`.

Verification:

- README walkthrough: seed data, edit data, exit, relaunch, and confirm saved changes.
- File inspection for `contacts.pkl` and `notes.pkl`.

### QA-03 Data Validation

The system shall validate phone, email, birthday, and tag inputs before accepting them into the domain model.

Verification:

- Manual invalid-input checks.
- Validator construction checks for `Phone`, `Email`, `Birthday`, and `Tag`.

### QA-04 Performance

The system is intended for personal-scale data, not enterprise-scale datasets. Linear scans for notes, contacts, and tags are acceptable for the expected number of records.

Target:

- Common list, search, and tag operations should feel immediate for a few hundred personal records on a local machine.

### QA-05 Security and Privacy

The system shall not transmit user data to external services. User data remains local to the user's machine. Pickle files shall not be committed to source control.

Verification:

- No network integration exists in runtime features.
- `.gitignore` excludes pickle files.

### QA-06 Localization

The implementation and user-facing project documentation shall use English. Localization into other languages is out of scope for Phase 1.
