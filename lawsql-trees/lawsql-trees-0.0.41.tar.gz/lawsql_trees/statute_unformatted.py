import re
from typing import Iterator


def fix_absent_signer_problem(data: dict):
    if signer_found := data.get("signers_of_law", None):
        return data
    if not (units_found := data.get("units", None)):
        return data
    if not (text := units_found[-1].get("content", None)):
        return data
    if not (idx := text.find("Approved,")):
        return data
    data["signers_of_law"] = text[idx:]
    data["units"][-1]["content"] = text[:idx]
    return data


def only_one_mark(text: str, num: int):
    mark = rf"SEC\. {num}"
    matches = re.finditer(mark, text)
    counts = len(list(matches))
    return counts == 1 or counts == 0


def get_content(index: int, text: str, num: int):
    raw = text[:index]
    cleaned = raw.removeprefix(f"SEC. {num - 1}.")
    content = cleaned.strip()
    return content


def slices(text: str, index: int) -> Iterator[dict]:
    """Presumes that the first section has already been processed. The while loop recurs until either (1) an error is found due there being no marks / more than one marks -- a mark here means an indicator of a slice; or (2) there is no subsequent mark to be found with the slice.

    Args:
        text (str): [description]
        index (int): [description]

    Yields:
        Iterator[dict]: Sections 2 and up in dict format
    """
    num = 2
    while True:
        text = text[index:]
        num += 1
        index = text.find(f"SEC. {num}.")
        item = f"Section {num - 1}"

        if not only_one_mark(text, num):
            yield {
                "item": item,
                "content": text,
                "error": "More than one mark found.",
            }
            break

        yield {"item": item, "content": get_content(index, text, num)}
        if index == -1:
            break


def fix_sections(text: str, red_flag: str) -> Iterator[dict]:
    """Presumes that the first section contains multiple sections as indicated by

    Args:
        text (str): The erroneous text

    Yields:
        Iterator[dict]: The first item yielded is the fixed text, the subsequent items are sliced from the original text.
    """
    index = text.find(red_flag)
    yield {"item": "Section 1", "content": text[:index]}
    yield from slices(text, index)  # repeat until exhausted


def fix_multiple_sections_in_first(data: dict) -> dict:
    """Make fix if the the first section contains several sections

    Args:
        data (dict): The source dictionary which should contain a populated "units" key

    Returns:
        dict: The original dictionary or the fixed dictionary
    """

    if not (units := data.get("units", None)):
        return data
    if not (unit := units[0]):
        return data
    if not (content := unit.get("content", None)):
        return data

    red_flag = "SEC. 2"
    if not red_flag in content:
        return data

    # extract sections from the first section
    fixed_sections = list(fix_sections(content, red_flag))

    # remove the first section which contains problems
    data["units"].pop(0)

    # reinsert extracted sections and add the remaining original sections
    data["units"] = fixed_sections + data["units"]
    return data
