def is_empty(value):
    if value is None:
        return True
    elif len(value.strip()) == 0:
        return True
    return False
