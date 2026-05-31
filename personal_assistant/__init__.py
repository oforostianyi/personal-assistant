"""Personal Assistant — hierarchical contextual REPL.

Importing this package as a side-effect registers every module's command
handlers via the @command decorator. Handler imports are added back by the
module cards (20/22/23) and finalized in Card 24.
"""

# Handler imports are re-enabled per module card:
from personal_assistant.contacts import handlers as _ch  # noqa: F401  # card-20
# from personal_assistant.notes import handlers as _nh  # noqa: F401     # card-22
# from personal_assistant.tags import handlers as _th  # noqa: F401      # card-23
