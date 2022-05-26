import json
from dataclasses import dataclass, asdict, field
from typing import Optional, List, Union

from .component import Component
from .composition import Text, Composition
from .element import Element, Image


@dataclass
class Block(Component):
    def render(self) -> dict:
        return asdict(
            self, dict_factory=lambda x: {k: v for (k, v) in x if v is not None}
        )

    def json(self) -> json:
        return json.dumps(self.render(), indent=4)


@dataclass
class ActionBlock(Block):
    """
    Available in surfaces: Modals, Messages, Home tabs
    A block that is used to hold interactive elements.
    """

    elements: List[object]
    block_id: Optional[str] = None
    type: str = field(default="actions", init=False)

    def __post_init__(self):
        if len(self.elements) > 25:
            raise ValueError(f"ActionBlock can only have 25 elements.")

        if self.block_id and len(self.block_id) > 255:
            raise ValueError(f"ActionBlock block_id can only be 255 characters long.")


@dataclass
class ContextBlock(Block):
    """
    Available in surfaces: Modals, Messages, Home tabs
    Displays message context, which can include both images and text.
    """

    elements: List[Union[Image, Text]]
    block_id: Optional[str] = None
    type: str = field(default="context", init=False)

    def __post_init__(self):
        if len(self.elements) > 10:
            raise ValueError(f"ContextBlock can only have 10 elements.")

        if self.block_id and len(self.block_id) > 255:
            raise ValueError(f"ContextBlock block_id can only be 255 characters long.")


@dataclass
class DividerBlock(Block):
    """
    Available in surfaces: Modals, Messages, Home tabs
    A content divider, like an <hr>, to split up different blocks inside of a message. The divider block is nice and neat, requiring only a type.
    """

    block_id: Optional[str] = None
    type: str = field(default="divider", init=False)

    def __post_init__(self):
        if self.block_id and len(self.block_id) > 255:
            raise ValueError(f"DividerBlock block_id can only be 255 characters long.")


@dataclass
class FileBlock(Block):
    """
    Appears in surfaces: Messages
    Displays a remote file. You can't add this block to app surfaces directly, but it will show up when retrieving messages that contain remote files
    """

    external_id: str
    source: str
    block_id: Optional[str] = None
    type: str = field(default="file", init=False)

    def __post_init__(self):
        if self.block_id and len(self.block_id) > 255:
            raise ValueError(f"FileBlock block_id can only be 255 characters long.")


@dataclass
class HeaderBlock(Block):
    """
    Available in surfaces: Modals, Messages, Home tabs
    A header is a plain-text block that displays in a larger, bold font. Use it to delineate between different groups of content in your app's surfaces.
    """

    text: Text
    block_id: Optional[str] = None
    type: str = field(default="header", init=False)

    def __post_init__(self):
        if len(self.text.text) > 150:
            raise ValueError(f"HeaderBlock text can only be 150 characters long.")
        if self.block_id and len(self.block_id) > 255:
            raise ValueError(f"HeaderBlock block_id can only be 255 characters long.")


@dataclass
class ImageBlock(Block):
    """
    Available in surfaces: Modals, Messages, Home tabs
    A simple image block, designed to make those cat photos really pop.
    """

    image_url: str
    alt_text: str
    title: Optional[Text] = None
    block_id: Optional[str] = None
    type: str = field(default="image", init=False)

    def __post_init__(self):
        if len(self.image_url) > 3000:
            raise ValueError(f"ImageBlock image_url can only be 3000 characters long.")
        if len(self.alt_text) > 2000:
            raise ValueError(f"ImageBlock alt_text can only be 2000 characters long.")
        if self.title and len(self.title.text) > 2000:
            raise ValueError(f"ImageBlock title can only be 2000 characters long.")
        if self.block_id and len(self.block_id) > 255:
            raise ValueError(f"HeaderBlock block_id can only be 255 characters long.")


@dataclass
class InputBlock(Block):
    """
    Available in surfaces: Modals, Messages, Home tabs
    A block that collects information from users - it can hold a plain-text input element, a checkbox element, a radio button element, a select menu element, a multi-select menu element, or a datepicker.
    """

    label: Text
    element: Union[Composition, Element]
    dispatch_action: Optional[bool] = None
    block_id: Optional[str] = None
    hint: Optional[Text] = None
    optional: Optional[bool] = None
    type: str = field(default="input", init=False)

    def __post_init__(self):
        if len(self.label.text) > 2000:
            raise ValueError(f"InputBlock label can only be 2000 characters long.")
        if self.block_id and len(self.block_id) > 255:
            raise ValueError(f"InputBlock block_id can only be 255 characters long.")
        if self.hint and len(self.hint.text) > 2000:
            raise ValueError(f"InputBlock hint can only be 2000 characters long.")


@dataclass
class SectionBlock(Block):
    """
    Available in surfaces: Modals, Messages, Home tabs
    A section is one of the most flexible blocks available - it can be used as a simple text block, in combination with text fields, or side-by-side with any of the available block elements.
    """

    text: Optional[Text] = None
    block_id: Optional[str] = None
    fields: Optional[List[Text]] = None
    accessory: Optional[Element] = None
    type: str = field(default="section", init=False)

    def __post_init__(self):
        if self.text and len(self.text.text) > 3000:
            raise ValueError(f"SectionBlock label can only be 3000 characters long.")
        if self.block_id and len(self.block_id) > 255:
            raise ValueError(f"SectionBlock block_id can only be 255 characters long.")
        if self.fields and len(self.fields) > 10:
            raise ValueError(f"SectionBlock hint can only be 10 items long.")
