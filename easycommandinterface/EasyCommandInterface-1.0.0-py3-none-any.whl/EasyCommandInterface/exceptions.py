class CommandInterfaceError(Exception):
    pass


class DuplicatedCommand(CommandInterfaceError):
    pass


class CommandInterfaceExists(CommandInterfaceError):
    pass


class CommandExecutionError(CommandInterfaceError):
    pass
