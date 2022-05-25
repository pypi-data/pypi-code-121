def is_int(str):
    try:
        int(str)
        return True
    except ValueError:
        return False
