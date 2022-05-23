class noDataError(ValueError):
    """Raised when input Data is None or empty."""


class columnError(ValueError):
    """Raised when columns passed to track_collev\
    are not present in data."""


class epsError(ValueError):
    """Raised if eps is smaller than 1."""


class minClSzError(ValueError):
    """Raised if minClSz is smaller than 1."""


class nPrevError(ValueError):
    """Raised if nPrev is smaller than 1."""
