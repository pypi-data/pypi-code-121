import re


def get_parts(val: str):
    """Splits a string into parts respecting double and single quotes

    Examples:
        >>> get_parts("mycol Random Timestamp \"2023-03-03 00:00:00\" '2026-12-12 23:59:59'")
        ["mycol", "Random", "Timestamp", "2023-03-03 00:00:00", "2026-12-12 23:59:59"]

    """
    groups = re.findall(r"[ ]?(?:(?!\"|')(\S+)|(?:\"|')(.+?)(?:\"|'))[ ]?",
                        val)

    # there are two matching groups for the two cases so get the first non empty val
    def first_non_empty(g):
        if g[0]:
            return g[0]
        else:
            return g[1]

    return [first_non_empty(group) for group in groups]


def split_gcs_path(path: str):
    """Splits a path into bucket and the object path parts."""

    pattern = "(?:gs://)?(?P<bucket>[^/]+)/(?P<obj>.+)"
    path = re.match(pattern, path)
    if not path:
        raise Exception(f"path [{path}] is invalid")
    return path