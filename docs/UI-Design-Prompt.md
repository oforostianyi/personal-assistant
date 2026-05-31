# Personal Assistant - UI Design Specification

## Purpose

This document defines the terminal UI design for Personal Assistant. The product is an offline Python command-line REPL with contextual navigation, not a web or mobile application.

The UI must make the current location visible, keep commands discoverable, render data clearly, and help users recover from mistakes without reading source code.

## Product Identity

| Attribute | Value |
|---|---|
| Product Name | Personal Assistant |
| Product Type | Offline terminal REPL / command-line application |
| Primary Users | Course evaluator, project team, and local CLI users |
| Tone | Practical, clear, calm, reliable |
| Style | Console utility with context prompts, Rich tables/cards, concise confirmations, and actionable errors |

## Terminal Visual System

Colors are optional semantic accents. The UI must remain readable in monochrome terminals.

| Role | Terminal Treatment |
|---|---|
| Headings | Bold or primary accent where supported |
| Success | Text confirmation; green accent if supported |
| Warning | Text warning; amber accent if supported |
| Error | `Error:` or clear failure message; red accent if supported |
| Secondary text | Dim/gray hints where supported |
| Tables/cards | Rich borders and stable headers |

Typography uses the user's terminal monospace font. Spacing should stay compact: one blank line between multi-line outputs and the next prompt is enough.

## Navigation Model

The UI is organized by context:

| Context | Prompt Example | Purpose |
|---|---|---|
| Root | `>` | Global navigation, search, birthdays, exit |
| Contacts module | `contacts>` | Contact list, find, sort, filter, create |
| Contact entity | `contacts/Alice Johnson>` | Show/edit/delete one contact and view linked notes |
| Notes module | `notes>` | Note list, find, sort, filter, create |
| Note entity | `notes/Project kickoff>` | Show/edit/rename/tag/link/delete one note |
| Tags module | `tags>` | Tag list, find, sort |
| Tag entity | `tags/work>` | Show tag usage, related contacts/notes, rename/merge/delete |

Navigation commands:

- `contacts`, `notes`, `tags`: enter module.
- `..`: move one level up.
- `/`: return to root.
- `help` or `?`: show commands for the current context.
- `exit`, `quit`, `q`: save and close.

## Core UI Components

| Component | Behavior |
|---|---|
| Prompt | Always reflects current context. |
| Context help | Lists only commands valid in the current context. |
| Entity-enter | Typing an existing contact name, note title, or tag name opens that entity. |
| Auto-show | After entering an entity, the app displays its card automatically. |
| Tables | Used for lists: contacts, notes, tags, birthdays, search results. |
| Cards | Used for single contact, note, or tag views. |
| Confirmation prompts | Used for destructive actions and optional entity creation. |
| Error messages | State what failed and give the next useful action. |

## Key User Flows

| Flow | UI Path | Success Criteria |
|---|---|---|
| Discover commands | `>` -> `help`; module -> `help`; entity -> `help` | User sees relevant commands for current context. |
| Create contact | `contacts>` -> `new NAME` -> contact entity | Contact card appears and can be edited. |
| Inspect contacts | `contacts>` -> `list`, `find`, `sort`, `filter tag TAG` | Results appear in readable tables. |
| Create note | `notes>` -> `new TITLE` -> multi-line body | Note is created, auto-tags are shown, suggestions appear when detected. |
| Link note | note entity -> `link CONTACT_NAME` | Linked contact appears in note/contact views. |
| Manage tag | `tags>` -> tag entity -> `contacts`, `notes`, `rename`, `merge`, `delete` | Tag operations update contacts and notes consistently. |
| Recover from typo | Mistyped command -> suggestion | REPL stays running and suggests likely command. |
| Persist data | Any context -> `exit` -> relaunch | Contacts and notes remain available. |
| Demo setup | shell -> `python -m personal_assistant.seed --force` | 15 contacts and 15 notes are available for walkthrough. |

## Data Display Requirements

| View | Required Content |
|---|---|
| Contacts table | Name, phone summary, email, birthday, tags, linked note count where available |
| Contact card | Name, phones, email, address, birthday, tags, linked notes |
| Birthday table | Contact name, congratulation date, weekday |
| Notes table | Title, preview, tags, linked contacts, updated timestamp |
| Note card | Title, body, tags, linked contacts, created/updated timestamps |
| Tags table | Tag name, contact count, note count, total usage |
| Tag card | Tag name, usage counts, available related views |
| Search results | Grouped contacts and notes |

## Empty, Error, and Ambiguous States

| State | Required Treatment |
|---|---|
| Empty contacts | Say no contacts exist and suggest `new NAME` inside `contacts>`. |
| Empty notes | Say no notes exist and suggest `new TITLE` inside `notes>`. |
| Empty tag results | Say no entities use the tag and suggest `list` or broader search. |
| Missing entity | Say the contact, note, or tag was not found. |
| Ambiguous entity | Show numbered matches and ask for exact name or refined query. |
| Invalid field | Show validator message without traceback. |
| Mistyped command | Show closest command suggestion when available. |
| Seed overwrite | Clearly warn that local pickle files are overwritten. |

## Sample Content

| Element | Example |
|---|---|
| Root prompt | `>` |
| Module prompt | `contacts>` |
| Entity prompt | `notes/Project kickoff>` |
| Contact command | `contacts> new Anna Kowalska` |
| Birthday edit | `contacts/Anna Kowalska> edit birthday 14.05.1998` |
| Note command | `notes> new Project kickoff` |
| Note body | `Discuss project timeline with Alice Johnson. #work #planning` |
| Note link | `notes/Project kickoff> link Alice Johnson` |
| Tag command | `tags/work> rename job` |
| Error | `Unknown: 'contatcs'. Did you mean 'contacts'?` |
| Ambiguous | `Multiple matches: 1. Alice Johnson 2. Alicia Stone. Type the exact name to enter, or refine your query.` |

## Accessibility and Portability

- Do not rely on color alone.
- Keep messages short and readable when copied as plain text.
- Avoid decorative icons that may not render in all terminals.
- Keep table columns stable and labels explicit.
- Use `DD.MM.YYYY` for birthdays.
- Runtime command vocabulary is English.

## Requirements Coverage

| UI Area | FRS Source |
|---|---|
| Contacts table/card and contact command feedback | FR-CONT-001 through FR-CONT-010 |
| Birthday result view | FR-BDAY-001 through FR-BDAY-004 |
| Notes table/card and note command feedback | FR-NOTE-001 through FR-NOTE-012 |
| Note-contact link output | FR-LINK-001 through FR-LINK-004 |
| Tags table/card and tag command feedback | FR-TAG-001 through FR-TAG-011 |
| Help, parser behavior, completion, suggestions, navigation, and errors | FR-UX-001 through FR-UX-012 |
| Save/load/exit feedback | FR-PERS-001 through FR-PERS-005 |
| Demo seed and launcher support | FR-DEMO-001 through FR-DEMO-006 |

## Validation Checklist

- [x] Current context is visible in every prompt.
- [x] Commands are discoverable from `help` in root, module, and entity contexts.
- [x] List outputs use readable tables.
- [x] Single-entity outputs use readable cards.
- [x] Empty states include the next useful action.
- [x] Errors are friendly and do not expose tracebacks.
- [x] Color is optional and not required for meaning.
- [x] UI scope remains terminal-only: no web, mobile, desktop GUI, cloud UI, or AI chat.
