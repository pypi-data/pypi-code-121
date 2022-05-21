import re


def notify(status, msg):
    return {
        "data": {},
        "errmsg": f"{status}: {msg}",
        "ok": False,
    }


def verify_email(email):
    """Verify email's format.

    Args:
        email: email address.

    Raises:
        ValueError: If `email` is not a string.
        ValueError: If `email` format is invalid.

    Returns:
        bool: True
    """
    regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    if type(email) is not str:
        raise ValueError("Email is not a string.")
    if not re.fullmatch(regex, email):
        raise ValueError("Invalid email.")
    return True
