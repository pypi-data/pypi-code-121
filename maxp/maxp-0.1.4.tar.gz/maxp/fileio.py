import inspect
import os


def relative(filename: str) -> str:
    """Find a file from a relative file path and name. Uses '..' to define leaves.

    Usage::
    ```
    relative('..\\\\..\\\\test.txt')
    ```

    Args:
        filename (str): The relative filename, as well as any leaves to go up.

    Returns:
        str: The constructed filename.
    """
    leaves = filename.split("\\")
    count = leaves.count("..") + 1

    calledFrom = inspect.stack()[1].filename
    commonLeaves = calledFrom.split("\\")
    commonRoot = "\\".join(commonLeaves[: (len(commonLeaves) - count)])

    end = [leaf for leaf in leaves if leaf != ".."]
    return os.path.join(commonRoot, "\\".join(end))
