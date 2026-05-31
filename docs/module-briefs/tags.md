# Tags Module

## Responsibility

The tags module is virtual: tags live on contacts and notes, while tag views and operations are calculated by walking both books.

## Main Files

- `personal_assistant/tags/aggregator.py` — collects tag usage across contacts and notes.
- `personal_assistant/tags/handlers.py` — context commands for tags module and tag entity views.

## User Contexts

| Context | Prompt | Main Behavior |
|---|---|---|
| Tags module | `tags>` | `list`, `sort`, `find` |
| Tag entity | `tags/TAG>` | `show`, `contacts`, `notes`, `rename`, `merge`, `delete` |

## Acceptance

- Tags list shows contact count, note count, and total usage.
- Tags can be searched and sorted by name, usage, contacts, or notes.
- Opening a tag entity shows usage and allows related contact/note lists.
- Rename, merge, and delete operations update contacts and notes consistently.
- Tag mutations persist because they update the contact and note books.
