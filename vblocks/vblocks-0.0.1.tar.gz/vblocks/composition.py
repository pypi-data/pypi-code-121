import json
from dataclasses import dataclass, asdict, field
from typing import Optional, List

from .component import Component
from .enums import StyleType, TextType, TriggerActions, Include


@dataclass
class Composition(Component):
    def render(self) -> dict:
        return asdict(
            self, dict_factory=lambda x: {k: v for (k, v) in x if v is not None}
        )

    def json(self) -> json:
        return json.dumps(self.render(), indent=4)


@dataclass
class Text(Composition):
    """_
    An object containing some text, formatted either as plain_text or using mrkdwn, our proprietary contribution to the much beloved Markdown standard.
    """

    type: str
    text: str
    emoji: Optional[bool] = None
    verbatim: Optional[bool] = None

    def __post_init__(self):
        if self.type not in TextType.list():
            raise ValueError(
                f"{self.type} is not a valid type argument. Please use one of the following {TextType.list()}"
            )
        if len(self.text) > 3000:
            raise ValueError(f"Text is too long. Character limit is 3000.")
        if self.emoji and self.type == TextType.MARKDOWN.value:
            raise ValueError(
                f"Emoji attribute only available if type='{TextType.PLAINTEXT.value}'"
            )
        if self.emoji and not isinstance(self.emoji, bool):
            raise ValueError(
                f"{self.emoji} is not a valid emoji argument. Should be of type bool."
            )
        if self.verbatim and self.type == TextType.PLAINTEXT.value:
            raise ValueError(
                f"Verbatim attribute only available if type='{TextType.MARKDOWN.value}'"
            )
        if self.verbatim and not isinstance(self.verbatim, bool):
            raise ValueError(
                f"{self.verbatim} is not a valid verbatim argument. Should be of type bool."
            )


@dataclass
class Confirmation(Composition):
    """
    An object that defines a dialog that provides a confirmation step to any interactive element. This dialog will ask the user to confirm their action by offering a confirm and deny buttons.
    """

    title: Text
    text: Text
    confirm: Text
    deny: Text
    style: Optional[str] = None

    def __post_init__(self):
        if len(self.title.text) > 100:
            raise ValueError(f"Confirmation title can only be 100 characters long.")
        elif self.title.type != TextType.PLAINTEXT.value:
            raise ValueError(
                f"Confirmation title can only be {TextType.PLAINTEXT.value}"
            )

        if len(self.text.text) > 300:
            raise ValueError(f"Confirmation text can only be 300 characters long.")

        if len(self.confirm.text) > 30:
            raise ValueError(
                f"Confirmation confirm object's text can only be 30 characters long."
            )
        elif self.confirm.type != TextType().PLAINTEXT.value:
            raise ValueError(
                f"Confirmation confirm object type can only be {TextType.PLAINTEXT.value}"
            )

        if len(self.deny.text) > 30:
            raise ValueError(
                f"Confirmation deny object's text can only be 30 characters long."
            )
        elif self.deny.type != TextType().PLAINTEXT.value:
            raise ValueError(
                f"Confirmation deny object type can only be {TextType.PLAINTEXT.value}"
            )

        if self.style and self.style not in StyleType.list():
            raise ValueError(
                f"Confirmation style must be one of the following types {StyleType.list()}"
            )


@dataclass
class Option(Composition):
    """
    An object that represents a single selectable item in a select menu, multi-select menu, checkbox group, radio button group, or overflow menu.
    """

    text: Text
    value: str
    description: Optional[Text] = None
    url: Optional[str] = None

    def __post_init__(self):
        if len(self.text.text) > 75:
            raise ValueError(f"Option text can only be 75 characters long.")

        if len(self.value) > 75:
            raise ValueError(f"Option value can only be 75 characters long.")

        if self.description and len(self.description) > 75:
            raise ValueError(f"Option description can only be 75 characters long.")
        elif self.description:
            self.description = Text(type="plain_text", text=self.description)

        if self.url and len(self.url) > 3000:
            raise ValueError(f"Option url can only be 3000 characters long.")


@dataclass
class OptionGroup(Composition):
    """
    Provides a way to group options in a select menu or multi-select menu.
    """

    label: Text
    options: List[Option]

    def __post_init__(self):
        if len(self.label.text) > 75:
            raise ValueError(f"Option Group label can only be 75 characters long.")
        elif self.label.type != TextType.PLAINTEXT.value:
            raise ValueError(
                f"Option Group label type can only be {TextType.PLAINTEXT.value}"
            )

        if len(options) > 100:
            raise ValueError(f"Option Group options can only be 100 items long.")


@dataclass
class DispatchAction(Composition):
    """
    Determines when a plain-text input element will return a block_actions interaction payload.
    """

    trigger_actions_on: Optional[List[str]] = None

    def __post_init__(self):
        if (
            self.trigger_actions_on
            and self.trigger_actions_on not in TriggerActions.list()
        ):
            raise ValueError(
                f"Dispatch Action trigger_actions_on must be one of the following types {TriggerActions.list()}"
            )


@dataclass
class Filter(Composition):
    """
    Provides a way to filter the list of options in a conversations select menu or conversations multi-select menu.
    """

    include: Optional[List[str]] = None
    exclude_external_shared_channels: Optional[bool] = None
    exclude_bot_users: Optional[bool] = None

    def __post_init__(self):
        if self.include and self.include not in Include.list():
            raise ValueError(
                f"Filter include must be one of the following types {TriggerActions.list()}"
            )

        if self.exclude_external_shared_channels and isinstance(
            self.exclude_external_shared_channels, bool
        ):
            raise ValueError(
                f"Filter exclude_external_shared_channels must be of type bool"
            )

        if self.exclude_bot_users and isinstance(self.exclude_bot_users, bool):
            raise ValueError(f"Filter exclude_bot_users must be of type bool")
