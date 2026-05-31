# UI Module

## Responsibility

The UI module owns terminal input helpers, context help, command/entity completion, fuzzy suggestions, and Rich-based table/card rendering.

## Main Files

- `personal_assistant/ui/parser.py` — tokenization for user input.
- `personal_assistant/ui/completer.py` — context-aware completion for commands and entity names.
- `personal_assistant/ui/fuzzy.py` — command suggestions and entity matching.
- `personal_assistant/ui/help.py` — context help from the command registry.
- `personal_assistant/ui/tables.py` and `personal_assistant/ui/views.py` — Rich table and card rendering.

## UI Rules

- Prompts must make context visible: `>`, `contacts>`, `notes>`, `tags>`, and entity prompts.
- `help` and `?` must show commands for the current context.
- Tab completion must include current-context commands and relevant entity names.
- Fuzzy suggestions must help with mistyped commands without mutating data.
- Tables and cards must remain readable in monochrome terminals.

## Acceptance

- Root, module, and entity help output is accurate.
- Contacts, notes, tags, birthdays, and search results render as readable tables.
- Single contact, note, and tag views render as readable cards.
- Empty states are clear and include the next useful action.
- Validation and lookup errors are friendly and do not show tracebacks.
