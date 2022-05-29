from enum import IntEnum

class InjectableScopeType(IntEnum):
    """Defines the valid types of an injectable's lifetime scope."""

    TRANSIENT = 0
    """Marks the injectable as transient,
    meaning a new instance is created for each dependency.
    """

    SINGLETON = 1
    """Marks the injectable as a singleton,
    meaning the same single instance is returned for
    each request from a lifetime scope and
    all of its child lifetime scopes.
    """

    SCOPED = 2
    """Marks the injectable as scoped,
    meaning a new instance is created for each lifetime scope,
    even the children of a parent lifetime scope (contrary to singletons).
    """
