"""Contacts book."""

from __future__ import annotations

from collections import UserDict
from datetime import date, timedelta

from personal_assistant.contacts.fields import Tag
from personal_assistant.contacts.record import Record


_VALID_SORT_FIELDS = ("name", "birthday", "tags_count", "created")


class ContactsBook(UserDict[str, "Record"]):
    """Contacts book. Key: name (string), value: Record."""

    def add_record(self, record: Record) -> None:
        self.data[record.name.value] = record

    def find(self, name: str) -> Record | None:
        return self.data.get(name)

    def delete(self, name: str) -> None:
        if name not in self.data:
            raise KeyError(f"Record '{name}' not found in address book.")
        del self.data[name]

    # --- search and sorting -------------------------------------------------

    def search(self, query: str) -> list[Record]:
        """Case-insensitive substring across name, phones, email, address, tags."""
        q = query.strip().lower()
        if not q:
            return []
        results: list[Record] = []
        for r in self.data.values():
            haystacks: list[str] = [r.name.value.lower()]
            haystacks.extend(p.value for p in r.phones)
            if r.email:
                haystacks.append(r.email.value.lower())
            if r.address:
                haystacks.append(r.address.value.lower())
            haystacks.extend(t.value for t in r.tags)
            if any(q in h for h in haystacks):
                results.append(r)
        return results

    def search_by_tag(self, tag: str) -> list[Record]:
        """Exact tag match. Tag(...) normalizes (lowercase, strip #)."""
        target = Tag(tag)
        return [r for r in self.data.values() if target in r.tags]

    def sorted_by(self, field: str, reverse: bool = False) -> list[Record]:
        """Sorting. Records without the field value always go at the end."""
        if field not in _VALID_SORT_FIELDS:
            raise ValueError(
                f"Cannot sort by '{field}'. Available: {', '.join(_VALID_SORT_FIELDS)}."
            )

        def has_value(r: Record) -> bool:
            if field == "name":
                return True
            if field == "birthday":
                return r.birthday is not None
            if field == "tags_count":
                return True
            if field == "created":
                return getattr(r, "created_at", None) is not None
            return False

        def key(r: Record):
            if field == "name":
                return r.name.value.lower()
            if field == "birthday":
                bd = r.birthday.value
                return (bd.month, bd.day)
            if field == "tags_count":
                return len(r.tags)
            if field == "created":
                return r.created_at

        present = [r for r in self.data.values() if has_value(r)]
        missing = [r for r in self.data.values() if not has_value(r)]
        present.sort(key=key, reverse=reverse)
        missing.sort(key=lambda r: r.name.value.lower())
        return present + missing

    # --- birthdays ----------------------------------------------------------

    def get_upcoming_birthdays(self, days: int = 7) -> list[dict[str, str]]:
        today = date.today()
        horizon = today + timedelta(days=days)
        upcoming: list[dict[str, str]] = []

        for record in self.data.values():
            if record.birthday is None:
                continue

            bday = record.birthday.value
            try:
                bday_this_year = bday.replace(year=today.year)
            except ValueError:
                bday_this_year = bday.replace(year=today.year, day=28)

            if bday_this_year < today:
                try:
                    bday_this_year = bday.replace(year=today.year + 1)
                except ValueError:
                    bday_this_year = bday.replace(year=today.year + 1, day=28)

            if today <= bday_this_year <= horizon:
                congrats = bday_this_year
                if congrats.weekday() == 5:
                    congrats += timedelta(days=2)
                elif congrats.weekday() == 6:
                    congrats += timedelta(days=1)

                upcoming.append(
                    {
                        "name": record.name.value,
                        "congratulation_date": congrats.strftime("%d.%m.%Y"),
                    }
                )

        return upcoming
