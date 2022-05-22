import re


def extract_group(pattern: str, text: str, /) -> str:
    """Apply a regex with 1 capture group and check that there is exactly 1
    match, and then return it.
    """

    if re.compile(pattern).groups <= 1:
        (result,) = extract_groups(pattern, text)
        return result
    else:
        raise ValueError(f"Multiple capture groups: {pattern}")


def extract_groups(pattern: str, text: str, /) -> list[str]:
    """Apply a regex with a positive number of capture groups and check that
    there is exactly 1 match, and then return their contents as a single list.
    """

    compiled = re.compile(pattern)
    if (n_groups := compiled.groups) == 0:
        raise ValueError(f"No capture groups: {pattern}")
    else:
        results = compiled.findall(text)
        if (n_results := len(results)) == 0:
            raise ValueError(f"No matches: {text}")
        elif n_results == 1:
            if n_groups == 1:
                return results
            else:
                (result,) = results
                return list(result)
        else:
            raise ValueError(f"Multiple matches: {text}")
