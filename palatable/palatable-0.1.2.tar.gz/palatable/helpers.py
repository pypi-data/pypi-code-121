def read_file(path: str):
    """
    A helper function that opens a fiel for read-only and yeilds
    the lines one by one. It filters comments out.
    """
    for line in open(path, "r"):
        if line.startswith("#"):
            continue

        yield line


def calculate_distance(first: int, second: int) -> int:
    """
    This is the distance between two values, and defined by
    D = |S-F|
    """
    return abs(second - first)
