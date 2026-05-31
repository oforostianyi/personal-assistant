"""Demo-data loader.

Run `python -m personal_assistant.seed` to populate the data files with a
realistic demonstration set: 15 contacts and 15 notes, cross-linked, with
tags shared across both books and a few birthdays inside the next week.

This OVERWRITES the existing contacts.pkl / notes.pkl, so it asks for
confirmation first. Pass `--force` (or `-f`) to skip the prompt.
"""

from __future__ import annotations

import sys
from datetime import date, timedelta

from personal_assistant.contacts.book import ContactsBook
from personal_assistant.contacts.record import Record
from personal_assistant.core.paths import contacts_path, notes_path
from personal_assistant.core.storage import PickleStorage
from personal_assistant.notes.book import NotesBook
from personal_assistant.notes.note import Note


def _bday(days_from_today: int, year: int) -> str:
    """A DD.MM.YYYY string whose day/month is `days_from_today` from today.

    The year is set in the past (birthdays are historical); upcoming-birthday
    logic only uses day/month, so this reliably lands inside the window.
    """
    d = date.today() + timedelta(days=days_from_today)
    return f"{d.day:02d}.{d.month:02d}.{year}"


# (name, phone, email|"", address|"", birthday|"", [tags])
CONTACTS: list[tuple] = [
    (
        "Alice Johnson",
        "0631000001",
        "alice@example.com",
        "12 Oak Street, Kyiv",
        _bday(2, 1990),
        ["work", "vip"],
    ),
    ("Bohdan Tkachenko", "0631000002", "", "", _bday(5, 1988), ["family", "робота"]),
    ("Carlos Mendez", "0631000003", "carlos@example.com", "", "", ["work", "project"]),
    (
        "Diana Prince",
        "0631000004",
        "",
        "5 Maple Ave, Lviv",
        _bday(20, 1992),
        ["friends", "vip"],
    ),
    (
        "Erik Sundqvist",
        "0631000005",
        "erik@example.com",
        "9 Pine Rd, Odesa",
        "",
        ["dev", "project"],
    ),
    ("Farida Hassan", "0631000006", "", "", "", ["finance"]),
    (
        "George Miller",
        "0631000007",
        "george@example.com",
        "",
        _bday(3, 1985),
        ["work", "meeting"],
    ),
    ("Hanna Koval", "0631000008", "", "", "", ["family", "health"]),
    ("Ivan Petrov", "0631000009", "ivan@example.com", "", "", ["dev", "books"]),
    ("Julia Roberts", "0631000010", "", "", _bday(45, 1979), ["friends", "music"]),
    (
        "Kemal Yilmaz",
        "0631000011",
        "",
        "3 Cedar St, Kharkiv",
        "",
        ["travel", "project"],
    ),
    (
        "Lena Schmidt",
        "0631000012",
        "lena@example.com",
        "",
        _bday(6, 1991),
        ["work", "finance"],
    ),
    ("Mark Brown", "0631000013", "", "", "", ["ideas", "dev"]),
    ("Nina Sokolova", "0631000014", "nina@example.com", "", "", ["family", "personal"]),
    ("Omar Farouk", "0631000015", "", "", _bday(12, 1987), ["work", "travel"]),
]

# (title, body, [tags], [linked contact names])
NOTES: list[tuple] = [
    (
        "Project kickoff",
        "Kickoff with Carlos and Erik. Scope the #project, align on work streams.",
        ["project", "work"],
        ["Carlos Mendez", "Erik Sundqvist"],
    ),
    (
        "Weekly standup",
        "#meeting notes. George to share the roadmap.",
        ["meeting", "work"],
        ["George Miller"],
    ),
    (
        "Birthday gift for Diana",
        "Diana is #vip among friends — pick a thoughtful gift.",
        ["vip", "friends"],
        ["Diana Prince"],
    ),
    (
        "Finance review Q2",
        "#finance sync with Farida and Lena. Close the quarter.",
        ["finance"],
        ["Farida Hassan", "Lena Schmidt"],
    ),
    (
        "Dev onboarding",
        "#dev setup for Ivan and Mark. Erik mentors.",
        ["dev"],
        ["Ivan Petrov", "Mark Brown", "Erik Sundqvist"],
    ),
    (
        "Travel plan Istanbul",
        "#travel itinerary with Kemal and Omar.",
        ["travel", "project"],
        ["Kemal Yilmaz", "Omar Farouk"],
    ),
    (
        "Family dinner",
        "#family evening — Bohdan, Hanna and Nina.",
        ["family"],
        ["Bohdan Tkachenko", "Hanna Koval", "Nina Sokolova"],
    ),
    (
        "Book recommendations",
        "#books to lend Ivan next month.",
        ["books"],
        ["Ivan Petrov"],
    ),
    (
        "Music playlist",
        "#music picks shared with Julia.",
        ["music", "friends"],
        ["Julia Roberts"],
    ),
    (
        "Health checkup",
        "#health reminder. Call Hanna to schedule.",
        ["health", "family"],
        ["Hanna Koval"],
    ),
    (
        "Ideas backlog",
        "Raw #ideas from Mark — triage later.",
        ["ideas", "dev"],
        ["Mark Brown"],
    ),
    (
        "VIP client call",
        "Call Alice on 0631000001 about the #vip account at work.",
        ["vip", "work"],
        ["Alice Johnson"],
    ),
    (
        "Personal goals",
        "#personal quarterly goals with Nina.",
        ["personal"],
        ["Nina Sokolova"],
    ),
    (
        "Meeting notes with Alice",
        "#work #meeting recap. Alice owns follow-ups.",
        ["work", "meeting"],
        ["Alice Johnson"],
    ),
    ("Untitled thoughts", "Loose scratch notes with no tags and no links yet.", [], []),
]


def build() -> tuple[ContactsBook, NotesBook]:
    contacts = ContactsBook()
    for name, phone, email, address, birthday, tags in CONTACTS:
        record = Record(name)
        if phone:
            record.add_phone(phone)
        if email:
            record.set_email(email)
        if address:
            record.set_address(address)
        if birthday:
            record.add_birthday(birthday)
        for tag in tags:
            record.add_tag(tag)
        contacts.add_record(record)

    notes = NotesBook()
    for title, body, tags, linked in NOTES:
        note = Note(title=title, text=body)
        for tag in tags:
            note.add_tag(tag)
        notes.add_note(note)
        # Cross-link both sides by name (notes) and UUID (contacts).
        for contact_name in linked:
            record = contacts.find(contact_name)
            if record is not None:
                note.link_contact(record.name.value)
                record.link_note(note.id)

    return contacts, notes


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    force = "--force" in argv or "-f" in argv

    c_path, n_path = contacts_path(), notes_path()
    if not force:
        print("This will OVERWRITE your demo data:")
        print(f"  {c_path}")
        print(f"  {n_path}")
        try:
            ans = input("Proceed? (y/N): ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            ans = ""
        if ans not in ("y", "yes"):
            print("Aborted. No files were changed.")
            return 1

    contacts, notes = build()
    storage = PickleStorage()
    storage.save(contacts, c_path)
    storage.save(notes, n_path)

    links = sum(len(r.linked_note_ids) for r in contacts.data.values())
    print(
        f"Seeded {len(contacts.data)} contacts and {len(notes.data)} notes "
        f"({links} contact↔note links)."
    )
    print("Launch with:  python -m personal_assistant")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
