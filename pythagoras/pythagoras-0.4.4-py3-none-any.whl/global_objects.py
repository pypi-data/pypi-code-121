"""Global objects / variables / constants used by Pythagoras."""

import string

allowed_key_chars = set(string.ascii_letters + string.digits + "()_-~.=")
""" A set of URL/filename-safe characters.

 A set of characters allowed in Persistent Dict keys, 
 filenames / S3 object names, and hash addresses. """