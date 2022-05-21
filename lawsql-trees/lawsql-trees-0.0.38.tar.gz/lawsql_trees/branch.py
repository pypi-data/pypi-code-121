import re
from copy import deepcopy
from dataclasses import dataclass, field

from bs4 import BeautifulSoup
from treeish import fetch_values_from_key, get_node_id


@dataclass
class Branch:
    """Create a subtree of the `tree` (list of dicts) based on the `path` (str).

    Assumes previous configuration through `treeish.set_node_ids()` to generate paths.

    The properties of this structure that can be used in lawsql are:

    1. `@units` - for structured data
    2. `@shorthand` - for the truncated headline from joined citation_texts
    3. `@citation` - for the complete headline from joined citation_texts
    4. `@content` - for the complete content from joined content_texts
    5. `@statutes_from_branch` - for mapping statutes, if applicable
    6. `@decisions_from_citations` - for mapping decisions, if applicable
    7. `@is_container` - can serve as a flag to determine whether to populate additional content
    """

    path: str
    tree: list[dict] = field(default_factory=list)
    citation_texts: list[str] = field(default_factory=list)
    content_texts: list[str] = field(default_factory=list)
    content_path: str = None  # the first content node path found

    def __post_init__(self):
        # finalize the list of ids for hierarchy setup
        self.ids: str = self.partial_paths  # use given path
        self.ids.reverse()  # start with the lowest node ("e.g. 1.1.5.4") vs. the highest one ("1")
        self.ids.pop()  # remove "1"

        # create hierarchical branch units
        self.units: list[dict] = [self.set_hierarchy(self.ids)]

        # recursively function that populates the citation_texts and content_texts
        self.set_citation_and_context_texts(self.units)

        # finalize main outputs
        self.leaf: dict = get_node_id(self.tree, self.path)
        self.citation: str = str(self)
        self.content: str = self.textify("".join(self.content_texts))
        self.shorthand: str = self.truncate(self.citation, 25)

    def __repr__(self) -> str:
        return str(self.units)

    def __str__(self) -> str:
        return ", ".join(self.citation_texts[::-1])  # reorder from lowest node

    @property
    def is_container(self) -> bool:
        """The target path node may be a container, e.g. 1.1.1 is a container of 1.1.1.1."""
        target_path_nodes = self.path.split(".")
        if self.content_path:  # This is set
            content_nodes = self.content_path.split(".")
            if len(content_nodes) > len(target_path_nodes):
                return True
        return False

    @property
    def queries(self) -> list[str] | None:
        def get_texts():
            for text_list in fetch_values_from_key(self.units[0], "queries"):
                for text in text_list:
                    yield text

        return list(get_texts())

    @property
    def statutes_from_branch(self) -> list[str]:
        """Get all strings of Statutes found in the "statute" key in the nested dictionary"""
        if not (
            blocks := set(fetch_values_from_key(self.units[0], "statute"))
        ):
            return []
        return list(blocks)

    @property
    def decisions_from_citations(self) -> list[str]:
        return list(set(fetch_values_from_key(self.units[0], "citation")))

    @property
    def partial_paths(self) -> list[str]:
        """With a string delimited by `.` e.g. "1.1.2.6", get a list of partial paths, excluding the first path: ["1.1", "1.1.2", "1.1.2.6"]"""
        points = self.path.split(".")
        paths = []
        for counter, point in enumerate(points):
            if counter == 0:  # set the first '1'
                paths.append(str(point))
                continue
            next_path = f"{paths[-1]}.{str(point)}"
            paths.append(next_path)  # attach most recent to next
        return paths

    def set_hierarchy(self, ids: list[str]) -> dict:
        """Based on the text identifier, extract the relevant parts of the tree to form a path to the leaf node."""
        origin = None
        for id in ids:
            latest_node = deepcopy(get_node_id(self.tree, id))
            if not origin:  # the lowest node becomes the target node
                origin = latest_node
            else:  # the origin node is replaced, it becomes a child of the latest node
                latest_node["units"] = [origin]
                origin = latest_node  # move the latest node as new origin
        return origin

    def textify(self, html_markup: str):
        soup = BeautifulSoup(html_markup, "html5lib")
        text = soup.get_text(strip=True, separator=" ")
        return text

    def truncate(self, text: str, max_char: int) -> str:
        return f"{text[:max_char]} {'...' if len(text) >= max_char else ''}".strip()

    def set_citation_and_context_texts(self, nodes: list[dict]):
        """Recursive function to set the citation_texts and content_texts from the hierarhical nodes"""

        def shorten(text: str):
            """Replace the item's long form keyword with its shorthand format, if possible."""
            if "Paragraph" in text:
                return re.sub(r"Paragraph", "Par.", text)
            if "Article" in text:
                return re.sub(r"Article", "Art.", text)
            if "Section" in text:
                return re.sub(r"Section", "Sec.", text)
            if "Book" in text:
                return re.sub(r"Book", "Bk.", text)
            if "Chapter" in text:
                return re.sub(r"Chapter", "Ch.", text)
            return text

        def can_ignore(text: str = None):
            keywords = ["Paragraph", "Proviso", "Clause"]
            return any(i in text for i in keywords) if text else None

        for node in nodes:
            if "item" in node and "caption" in node:
                l = f"{shorten(node['item'])} ({node['caption'].removesuffix(' (n)')})".strip()
            elif "item" in node:
                l = f"{shorten(node['item'])}"
            elif "caption" in node:
                l = f"{node['caption'].removesuffix(' (n)')}"

            # limit citation texts to the path
            if node["id"] == self.path or self.path.startswith(node["id"]):
                self.citation_texts.append(f"{l.removesuffix('.')}")

            # extract all content
            if content := node.get("content", None):
                if not self.content_path:
                    self.content_path = node.get("id", None)
                item = node.get("item", None)
                partial = content if can_ignore(item) else f"{l} {content}"
                self.content_texts.append(partial)

            if node.get("units", None):
                self.set_citation_and_context_texts(node["units"])
