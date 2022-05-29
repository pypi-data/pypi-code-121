"""Hashx."""
import hashlib


def md5(s):
    """Compute MD5 Hash."""
    _md5 = hashlib.md5()
    _md5.update(s.encode())
    return _md5.hexdigest()
