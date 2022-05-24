import sys

from workspace import (
    command_build,
    command_cmake,
    command_help,
    command_install,
    command_pull,
    command_status,
    command_graph,
    command_cmd,
)

# Adding all imported commands to the commands list
commands = []
entries = locals().copy()
for name in entries:
    if name.startswith("command_"):
        commands.append(entries[name])
