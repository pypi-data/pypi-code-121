def remove_prefix(x: str, y: str) -> str:
    """ to be replaced with str.removeprefix when python >= 3.9 """
    if x.startswith(y):
        x = x[len(y):]
    return x


def remove_suffix(x: str, y: str) -> str:
    """ to be replaced with str.removesuffix when python >= 3.9 """
    assert len(y) > 0
    if x.endswith(y):
        x = x[:-len(y)]
    return x
