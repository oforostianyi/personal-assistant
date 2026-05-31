"""Tags module commands.

CTX_ROOT : `tags` — enter the module.
CTX_TAGS : list / sort / find.
CTX_TAG  : show (auto-show) / contacts / notes / rename / merge / delete.

All rename/merge/delete are bulk operations across both books via
`tags/aggregator.py`. There is no separate pickle for tags.
"""

from __future__ import annotations

from personal_assistant.contacts.fields import Tag
from personal_assistant.core.decorators import input_error
from personal_assistant.core.registry import (
    CTX_ROOT,
    CTX_TAG,
    CTX_TAGS,
    command,
)
from personal_assistant.tags.aggregator import (
    TagInfo,
    collect_tags,
    delete_tag,
    find_tag,
    merge_tag,
    rename_tag,
)
from personal_assistant.ui.views import (
    render_contacts_table,
    render_notes_table,
    render_tag_card,
    render_tags_table,
)

_VALID_TAG_SORT_FIELDS = ("name", "usage", "contacts", "notes")


# --- root: enter ----------------------------------------------------------

@command(
    "tags",
    context=CTX_ROOT,
    help_text="Enter the tags module.",
)
@input_error
def enter_tags(_args, state):
    state.enter_module("tags")
    return ""


# --- sort helper ----------------------------------------------------------

def _sort_tags(infos: list[TagInfo], field: str, reverse: bool) -> list[TagInfo]:
    keys = {
        "name": lambda t: t.name,
        "usage": lambda t: t.total,
        "contacts": lambda t: t.contact_count,
        "notes": lambda t: t.note_count,
    }
    if field not in keys:
        raise ValueError(
            f"Cannot sort by '{field}'. Available: {', '.join(_VALID_TAG_SORT_FIELDS)}."
        )
    return sorted(infos, key=keys[field], reverse=reverse)


# --- CTX_TAGS -------------------------------------------------------------

@command(
    "list",
    context=CTX_TAGS,
    help_text="List all tags with usage counts.",
)
@input_error
def list_tags_cmd(_args, state):
    infos = collect_tags(state)
    if not infos:
        return "No tags yet."
    field, reverse = state.tags_sort
    return render_tags_table(_sort_tags(infos, field, reverse))


@command(
    "sort",
    context=CTX_TAGS,
    format="<field> [asc|desc]",
    help_text="Set the sort key for `list`.",
)
@input_error
def sort_tags_cmd(args, state):
    if not args:
        raise ValueError(
            f"Usage: sort <field> [asc|desc]. Fields: "
            f"{', '.join(_VALID_TAG_SORT_FIELDS)}."
        )
    field = args[0].lower()
    if field not in _VALID_TAG_SORT_FIELDS:
        raise ValueError(
            f"Unknown sort field '{field}'. Try: "
            f"{', '.join(_VALID_TAG_SORT_FIELDS)}."
        )
    direction = args[1].lower() if len(args) > 1 else "asc"
    if direction not in ("asc", "desc"):
        raise ValueError("Direction must be 'asc' or 'desc'.")
    state.tags_sort = (field, direction == "desc")
    return f"Sort: {field} {direction}"


@command(
    "find",
    context=CTX_TAGS,
    format="<query>",
    help_text="Substring match on tag names.",
)
@input_error
def find_tags_cmd(args, state):
    if not args:
        raise ValueError("Usage: find <query>")
    q = " ".join(args).strip().lstrip("#").lower()
    matches = [t for t in collect_tags(state) if q in t.name]
    if not matches:
        return f"No tags matching '{q}'."
    field, reverse = state.tags_sort
    return render_tags_table(_sort_tags(matches, field, reverse))


# --- CTX_TAG: show / contacts / notes / rename / merge / delete ----------

@command(
    "show",
    context=CTX_TAG,
    help_text="Show this tag's counts.",
)
@input_error
def show_tag_cmd(_args, state):
    info = find_tag(state, state.entity_key)
    if info is None:
        # Possibly renamed/deleted in this session.
        return f"Tag '{state.entity_key}' no longer exists."
    return render_tag_card(info)


@command(
    "contacts",
    context=CTX_TAG,
    help_text="List contacts with this tag.",
)
@input_error
def tag_contacts_cmd(_args, state):
    results = state.contacts.search_by_tag(state.entity_key)
    if not results:
        return f"No contacts tagged '{state.entity_key}'."
    return render_contacts_table(results)


@command(
    "notes",
    context=CTX_TAG,
    help_text="List notes with this tag.",
)
@input_error
def tag_notes_cmd(_args, state):
    results = state.notes.find_by_tag(state.entity_key)
    if not results:
        return f"No notes tagged '{state.entity_key}'."
    return render_notes_table(results)


def _pluralise(n: int) -> str:
    return "entity" if n == 1 else "entities"


@command(
    "rename",
    context=CTX_TAG,
    format="<new>",
    help_text="Rename this tag everywhere (bulk update across both books).",
)
@input_error
def rename_tag_cmd(args, state):
    if not args:
        raise ValueError("Usage: rename <new>")
    new = args[0]
    affected = rename_tag(state, state.entity_key, new)
    state.entity_key = Tag(new).value
    return f"Updated {affected} {_pluralise(affected)}."


@command(
    "merge",
    context=CTX_TAG,
    format="<other>",
    help_text="Merge this tag into <other> (bulk update).",
)
@input_error
def merge_tag_cmd(args, state):
    if not args:
        raise ValueError("Usage: merge <other>")
    other = args[0]
    current = state.entity_key
    prompt = (
        f"Merge '{current}' into '{Tag(other).value}'? "
        f"All entities tagged '{current}' will be tagged "
        f"'{Tag(other).value}'. (y/N): "
    )
    try:
        ans = input(prompt).strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return "Cancelled."
    if ans not in ("y", "yes"):
        return "Cancelled."
    affected = merge_tag(state, current, other)
    state.go_up()
    return f"Updated {affected} {_pluralise(affected)}."


@command(
    "delete",
    context=CTX_TAG,
    help_text="Delete this tag from all entities.",
)
@input_error
def delete_tag_cmd(_args, state):
    name = state.entity_key
    try:
        ans = input(
            f"Delete tag '{name}' from all entities? (y/N): "
        ).strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return "Cancelled."
    if ans not in ("y", "yes"):
        return "Cancelled."
    affected = delete_tag(state, name)
    state.go_up()
    return f"Removed from {affected} {_pluralise(affected)}."