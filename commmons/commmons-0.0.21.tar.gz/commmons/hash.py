import hashlib

__all__ = [
    "md5"
]


def md5(org_str: str) -> str:
    m = hashlib.md5()
    m.update(org_str.encode("utf-8"))
    return m.hexdigest()
