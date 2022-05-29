import os


def count_files(path: str, suffix: str) -> int:
    """
    find number of files in a certain path that have a certain suffix
    """
    count = 0
    for _root, _dir, files in os.walk(path):
        for file in files:
            if file.endswith(suffix):
                count += 1
    return count
