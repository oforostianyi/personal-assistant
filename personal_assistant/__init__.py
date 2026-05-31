"""Personal Assistant — hierarchical contextual REPL.

Importing this package as a side-effect registers every module's command
handlers via the @command decorator.
"""

from personal_assistant.contacts import handlers as _ch  # noqa: F401
from personal_assistant.notes import handlers as _nh  # noqa: F401
from personal_assistant.tags import handlers as _th  # noqa: F401
