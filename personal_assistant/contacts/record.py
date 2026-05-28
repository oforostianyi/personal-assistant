"""Contact record.

Stage 3 adds email/address/tags/linked_note_ids/created_at. Note links use
UUIDs instead of titles because renaming a note must not break the link.

__setstate__ applies reasonable defaults in case an older pickle is ever
loaded. This is not a backward-compatibility workaround for hw-08, which the
plans forbid; it is only startup protection.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from personal_assistant.contacts.fields import (
    Address, Birthday, Email, Name, Phone, Tag,
)


class Record:
    """A single record in the contacts book."""

    def __init__(self, name: str) -> None:
        self.name = Name(name)
        self.phones: list[Phone] = []
        self.birthday: Birthday | None = None
        self.email: Email | None = None
        self.address: Address | None = None
        self.tags: list[Tag] = []
        self.linked_note_ids: list[UUID] = []
        self.created_at: datetime = datetime.now()

    def __setstate__(self, state):
        self.__dict__.update(state)
        for attr, default in (
            ("email", None),
            ("address", None),
            ("tags", []),
            ("linked_note_ids", []),
            ("created_at", datetime.now()),
        ):
            if not hasattr(self, attr):
                setattr(self, attr, default)

    # --- phones -------------------------------------------------------------

    def add_phone(self, phone: str) -> None:
        new = Phone(phone)
        if new not in self.phones:
            self.phones.append(new)

    def remove_phone(self, phone: str) -> None:
        target = Phone(phone)
        try:
            self.phones.remove(target)
        except ValueError:
            raise ValueError(f"Phone '{phone}' not found in record '{self.name}'.")

    def edit_phone(self, old_phone: str, new_phone: str) -> None:
        target = Phone(old_phone)
        replacement = Phone(new_phone)
        for index, phone in enumerate(self.phones):
            if phone == target:
                self.phones[index] = replacement
                return
        raise ValueError(f"Phone '{old_phone}' not found in record '{self.name}'.")

    def find_phone(self, phone: str) -> Phone:
        target = Phone(phone)
        for p in self.phones:
            if p == target:
                return p
        raise ValueError(f"Phone '{phone}' not found in record '{self.name}'.")

    # --- birthday -----------------------------------------------------------

    def add_birthday(self, birthday: str) -> None:
        self.birthday = Birthday(birthday)

    # --- email --------------------------------------------------------------

    def set_email(self, email: str) -> None:
        self.email = Email(email)

    def clear_email(self) -> None:
        self.email = None

    # --- address ------------------------------------------------------------

    def set_address(self, address: str) -> None:
        self.address = Address(address)

    def clear_address(self) -> None:
        self.address = None

    # --- tags ---------------------------------------------------------------

    def add_tag(self, tag: str) -> None:
        new = Tag(tag)
        if new not in self.tags:
            self.tags.append(new)

    def remove_tag(self, tag: str) -> None:
        target = Tag(tag)
        try:
            self.tags.remove(target)
        except ValueError:
            raise ValueError(
                f"Tag '{tag}' not found on contact '{self.name.value}'."
            )

    # --- linked notes -------------------------------------------------------

    def link_note(self, uid: UUID) -> None:
        if uid not in self.linked_note_ids:
            self.linked_note_ids.append(uid)

    def unlink_note(self, uid: UUID) -> None:
        if uid in self.linked_note_ids:
            self.linked_note_ids.remove(uid)

    # --- representation -----------------------------------------------------

    def __str__(self) -> str:
        phones_str = "; ".join(p.value for p in self.phones) or "no phones"
        bday_str = f", birthday: {self.birthday}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {phones_str}{bday_str}"
