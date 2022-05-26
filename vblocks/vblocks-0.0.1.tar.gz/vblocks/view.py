import json
from dataclasses import dataclass, asdict, field
from typing import Optional, List

from .component import Component
from .block import Block
from .composition import Text, Composition
from .element import Element


@dataclass
class View(Component):
    def render(self) -> dict:
        return asdict(
            self, dict_factory=lambda x: {k: v for (k, v) in x if v is not None}
        )

    def json(self) -> json:
        return json.dumps(self.render(), indent=4)


@dataclass
class Modal(View):
    """
    Modals provide focused spaces ideal for requesting and collecting data from users, or temporarily displaying dynamic and interactive information.
    """

    title: Text
    blocks: List[Block]
    close: Optional[Text] = None
    submit: Optional[Text] = None
    private_metadata: Optional[str] = None
    callback_id: Optional[str] = None
    clear_on_close: Optional[bool] = None
    notify_on_close: Optional[bool] = None
    external_id: Optional[str] = None
    submit_disabled: Optional[bool] = None
    type: str = field(default="modal", init=False)

    def __post_init__(self):
        if len(self.title.text) > 24:
            raise ValueError(f"Modal title can only be 24 characters long.")
        if len(self.blocks) > 100:
            raise ValueError(f"Modal blocks can only be 100 items long.")
        if self.close and len(self.close.text) > 24:
            raise ValueError(f"Modal close can only be 24 characters long.")
        if self.submit and len(self.submit.text) > 24:
            raise ValueError(f"Modal submit can only be 24 characters long.")
        if self.private_metadata and len(self.private_metadata) > 3000:
            raise ValueError(
                f"Modal private_metadata can only be 3000 characters long."
            )
        if self.callback_id and len(self.callback_id) > 255:
            raise ValueError(f"Modal callback_id can only be 255 characters long.")


@dataclass
class Home(View):
    """
    The Home tab is a persistent, yet dynamic interface for apps.
    Present each of your users with a unique Home tab just for them, always found in the exact same place.
    """

    blocks: List[Block]
    private_metadata: Optional[str] = None
    callback_id: Optional[str] = None
    external_id: Optional[str] = None
    type: str = field(default="home", init=False)

    def __post_init__(self):
        if len(self.blocks) > 100:
            raise ValueError(f"Modal blocks can only be 100 items long.")
        if self.private_metadata and len(self.private_metadata) > 3000:
            raise ValueError(
                f"Modal private_metadata can only be 3000 characters long."
            )
        if self.callback_id and len(self.callback_id) > 255:
            raise ValueError(f"Modal callback_id can only be 255 characters long.")


@dataclass
class Message(View):
    """
    Messages are one of the basic ingredients of Slack apps.
    Compose them, send them, retrieve them, update them, delete them.
    """

    text: str
    blocks: Optional[List[Block]] = None
    attachments: Optional[List[Block]] = None
    channel: Optional[str] = None
    thread_ts: Optional[str] = None
    mrkdwn: Optional[bool] = None
