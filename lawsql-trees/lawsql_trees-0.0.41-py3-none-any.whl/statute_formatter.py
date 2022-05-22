import re

from markdown import markdown
from treeish import fetch_values_from_key


def trim_text(raw: str, max_length: int) -> str:
    """Given a max length for a text, limit text to the same if it exceeds the length"""
    return raw[:max_length] if len(raw) > max_length else raw


def get_first_short_title_from_units(data_with_units: dict) -> str | None:
    if not "units" in data_with_units:
        return None
    l = list(fetch_values_from_key(data_with_units, "short_title"))
    return l[0] if l else None


def can_extract_short(node, content):
    return has_title_caption(node) or has_title_content(content)


def extract_quoted_pattern(text: str):
    if match_found := re.compile(r'".*"').search(text):
        return match_found.group().strip('".')
    return "Short title indicators but no quoted pattern found."


def has_title_content(text: str):
    patterns = [
        r"""(
            ^
            (This|The)
            \s*
            (Act|Code)
            \s*
            (may|shall)
            \s*
            be
            \s*
            (cited|known)
        )""",
        r"""(
            ^
            The
            \s*
            short
            \s*
            title
            \s*
            of
            \s*
            this
            \s*
            (Act|Code)
            \s*
            shall
            \s*
            be
        )""",
    ]
    return re.compile("|".join(patterns), re.X | re.I).search(text.strip())


def has_title_caption(node: dict):
    return (x := node.get("caption", None)) and is_short_title_caption(x)


def is_short_title_caption(text: str):
    return re.compile(r"short\s*title", re.I).search(text)


def short_title_found(node: dict) -> bool:
    if not (content := node.get("content", None)):
        return False
    if not can_extract_short(node, content):
        return False
    return True


def make_uniform_section(raw: str):
    """Replace the SECTION | SEC. | Sec. format with the word Section, if applicable."""
    regex = r"""
        ^\s*
        S
        (
            ECTION|
            EC|
            ec
        )
        [\s.,]+
    """
    pattern = re.compile(regex, re.X)
    if pattern.search(raw):
        text = pattern.sub("Section ", raw)
        text = text.strip("., ")
        return text
    return raw


def format_units(nodes: list[dict]) -> None:
    """
    1. Recursive function for nested item-caption-content units;
    2. Creates `short_title` key if found in a particular node.
    3. Applicable to Statute / Codification containers.
    """
    MAX_ITEM = 500  # creation of unit item labels
    MAX_CAPTION = 1000  # creation of unit caption labels

    for node in nodes:
        # Trims text to max number of character
        # If a "section", make sure it's converted into the full word
        if item := node.get("item", None):
            casted_item = str(item)  # in case, it's in int
            cleaned_item = make_uniform_section(casted_item)
            node["item"] = trim_text(cleaned_item, MAX_ITEM)

        if caption := node.get("caption", None):
            caption = str(caption)  # in case, it's in int
            node["caption"] = trim_text(caption, MAX_CAPTION)

        # Trims text to max number of character
        # Creates a special `short_title` key, if found
        # Converts markdown to html
        if content := node.get("content", None):
            if short_title_found(node):
                node["short_title"] = extract_quoted_pattern(node["content"])
            node["content"] = markdown(content.strip(), extensions=["tables"])

        # Add a default in case the action key is empty
        if histories := node.get("history", None):
            if isinstance(histories, list):
                for h in histories:
                    if isinstance(h, dict):
                        if not "action" in h:
                            if "locator" in h and "statute" in h:
                                h["action"] = "Originated"  # for statutes
                            if "citation" in h:
                                h["action"] = "Interpreted"  # for decisions

        # Recursive call
        if node.get("units", None):
            format_units(node["units"])  # call self
