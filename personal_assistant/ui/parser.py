"""Tokenize the user's line.

`shlex.split` handles quotes (`"two words"` becomes one argument). If
shlex trips on an unbalanced quote, fall back to a trivial `split()` so
the REPL never crashes.
"""

import shlex


def tokenize(s: str) -> list[str]:
    s = s.strip()
    if not s:
        return []
    try:
        return shlex.split(s)
    except ValueError:
        return s.split()
