def Tag(tag: str):
    """
    Decorator that adds the given tag to the decorated function.

    :param tag:     The tag to add to the function.
    """
    def apply_tag(method):
        if not hasattr(method, '__tags'):
            method.__tags = set()
        method.__tags.add(tag)
        return method

    return apply_tag


def has_tag(method, tag: str) -> bool:
    """
    Checks if the given method has the given tag.

    :param method:  The method to check.
    :param tag:     The tag to check for.
    :return:        True if the tag exists on the method,
                    False if not.
    """
    return hasattr(method, '__tags') and tag in method.__tags
