__all__ = (
    'VarutilsError',
    'IncompatibleTypeError'
)


class VarutilsError(Exception):
    """Base class for library-specific exceptions."""
    __slots__ = ()


class IncompatibleTypeError(TypeError, VarutilsError):
    """Throws when the type is incompatible with the expected logic."""
    __slots__ = ()
