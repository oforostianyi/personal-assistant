"""Parse user input into `(command_name, args)`.

The REPL reads a single line at a time. Tokens are split with `shlex.split`,
so quoted strings collapse into a single argument:

    >>> parse_input('add-note "two words" tail')
    ('add-note', ['two words', 'tail'])

If the line ends with an unmatched quote, `shlex` raises `ValueError`; in that
case we fall back to plain `str.split()` so the REPL never crashes on malformed
input. The handler receives raw tokens and decides what to do with them.

Corner cases handled:
- leading/trailing whitespace is stripped;
- runs of internal whitespace are collapsed;
- empty or whitespace-only input returns `("", [])`;
- mixed single and double quotes are honored;
- tabs and embedded newlines are treated as whitespace;
- command names are normalized to lower case;
- argument case is preserved verbatim.
"""

import shlex


def tokenize(line: str) -> list[str]:
    """Return whitespace/quote-aware tokens for a user input line."""
    line = line.strip()
    if not line:
        return []
    try:
        return shlex.split(line)
    except ValueError:
        return line.split()


def parse_input(line: str) -> tuple[str, list[str]]:
    """Split a user line into `(command_name, args)`.

    The command name is the first token lower-cased. Remaining tokens are
    returned as arguments with their original case preserved. Empty input
    yields `("", [])`, which the dispatcher treats as a no-op.
    """
    tokens = tokenize(line)
    if not tokens:
        return "", []
    return tokens[0].lower(), tokens[1:]
