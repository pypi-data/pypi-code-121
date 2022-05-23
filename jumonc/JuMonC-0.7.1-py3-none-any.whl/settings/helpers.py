import logging
logger = logging.getLogger(__name__)


def parse_boolean(s: str) -> bool:
    """Takes a string and returns the equivalent as a boolean value."""
    s = s.strip().lower()
    if s in ("yes", "true", "on", "1"):
        return True
    if s in ("no", "false", "off", "0", "none"):
        return False
    raise ValueError(f'Invalid boolean value {s}')
