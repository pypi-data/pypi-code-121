_invalid_uri_chars = '<>" {}|\\^`'


def is_valid_uri(uri):
    for c in _invalid_uri_chars:
        if c in uri:
            return False
    return True