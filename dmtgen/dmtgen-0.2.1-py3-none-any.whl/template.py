def escape_string(value: str) -> str:
    """ Escape control characters"""
    if value:
        return value.replace("\n", "\\n").replace("\r", "").replace('"', "'")
    return ""
