__all__ = (
    'PandakeeperError',
    'LoopedGraphError'
)


class PandakeeperError(Exception):
    """Base class for library-specific exceptions."""
    __slots__ = ()


class LoopedGraphError(PandakeeperError):
    """Throws when the logic of the algorithms can be violated by the presence of loops in graphs."""
    __slots__ = ()
