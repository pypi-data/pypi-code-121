class InvalidPathException(Exception):
    """No such file or directory."""


class NotebookDoesNotExist(Exception):
    """Notebook file does not exist."""


class SessionExists(Exception):
    """Session name already in use."""


class NBFormatModuleNotFound(Exception):
    """NBFormat module not found."""
