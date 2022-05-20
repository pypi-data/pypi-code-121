from trame_client.widgets.core import AbstractElement
from trame_markdown import module


class Markdown(AbstractElement):
    """
    Create a markdown viewer element

    >>> component = Markdown("**Bold**")
    >>> component.update(another_md_content)

    >>> content = \"\"\"
    ...
    ... # My document
    ... 1. First
    ... 2. Second
    ... 3. Third
    ...
    ... Hello "trame"
    ... \"\"\"
    >>> component = Markdown(content=("document2", content))
    """
    _next_md_id = 0

    def __init__(self, _md_content="**Some Mardown content**", **kwargs):
        super().__init__("markdown-it-vue", **kwargs)
        if self.server:
            self.server.enable_module(module)

        self._attr_names += ["content"]

        if "content" not in kwargs:
            Markdown._next_md_id += 1
            self._key = f"trame__markdown_{Markdown._next_md_id}"
            self.server.state[self._key] = _md_content
            self._attributes["content"] = f':content="{self._key}"'

    @property
    def key(self):
        """Return the name of the state variable used internally"""
        return self._key

    @property
    def md_content(self):
        """Return the markdown content currently used for that widget"""
        return self.server.state[self._key]

    def update(self, _md_content, **kwargs):
        """
        Update the Markdown content to show.

        :param _md_content: Markdown syntax as string
        """
        self.server.state[self._key] = _md_content


__all__ = [
    "Markdown",
]
