import json
from dataclasses import dataclass, asdict, field
from typing import Optional, List, Union

from .composition import (
    Component,
    Text,
    Confirmation,
    Option,
    OptionGroup,
    DispatchAction,
    Filter,
)
from .enums import StyleType


@dataclass
class Element(Component):
    def render(self) -> dict:
        return asdict(
            self, dict_factory=lambda x: {k: v for (k, v) in x if v is not None}
        )

    def json(self) -> json:
        return json.dumps(self.render(), indent=4)


@dataclass
class Button(Element):
    """
    Works with block types: SectionBlock, ActionBlock
    An interactive component that inserts a button. The button can be a trigger for anything from opening a simple link to starting a complex workflow.
    """

    text: Text
    action_id: str
    url: Optional[str] = None
    value: Optional[str] = None
    style: Optional[StyleType] = None
    confirm: Optional[Confirmation] = None
    accessibility_level: Optional[str] = None
    type: str = field(default="button", init=False)

    def __post_init__(self):
        if len(self.text.text) > 75:
            raise ValueError(f"Button text can only be 75 characters long.")

        if len(self.action_id) > 255:
            raise ValueError(f"Button action_id can only be 255 characters long.")

        if self.url and len(self.url) > 3000:
            raise ValueError(f"Button url can only be 3000 characters long.")

        if self.value and len(self.value) > 2000:
            raise ValueError(f"Button value can only be 2000 characters long.")

        if self.style and self.style not in StyleType.list():
            raise ValueError(
                f"Button style must be one of the following types {StyleType.list()}"
            )

        if self.accessibility_level and len(self.accessibility_level) > 75:
            raise ValueError(
                f"Button accessibility level can only be 75 characters long."
            )


@dataclass
class CheckboxGroup(Element):
    """
    Works with block types: SectionBlock, ActionBlock, InputBlock
    A checkbox group that allows a user to choose multiple items from a list of possible options.
    Checkboxes are only supported in the following app surfaces: Home tabs, Modals Messages
    """

    action_id: str
    options: List[Option]
    initial_options: Optional[Option] = None
    confirm: Optional[Confirmation] = None
    focus_on_load: bool = None
    type: str = field(default="checkboxes", init=False)

    def __post_init__(self):
        if len(self.action_id) > 255:
            raise ValueError(
                f"CheckboxGroup action_id can only be 255 characters long."
            )

        if len(self.options) > 10:
            raise ValueError(f"CheckboxGroup options can only be 10 items long.")


@dataclass
class DatePicker(Element):
    """
    Works with block types: SectionBlock, ActionBlock, InputBlock
    An element which lets users easily select a date from a calendar style UI.
    """

    action_id: str
    placeholder: Optional[Text] = None
    initial_date: Optional[str] = None
    confirm: Optional[Confirmation] = None
    focus_on_load: Optional[bool] = None
    type: str = field(default="datepicker", init=False)

    def __post_init__(self):
        if len(self.action_id) > 255:
            raise ValueError(f"DatePicker action_id can only be 255 characters long.")

        if len(self.placeholder.text) > 150:
            raise ValueError(f"DatePicker placeholder can only be 150 characters long.")


@dataclass
class Image(Element):
    """
    Works with block types: SectionBlock, ContextBlock
    An element to insert an image as part of a larger block of content. If you want a block with only an image in it, you're looking for the ImageBlock.
    """

    image_url: str
    alt_text: str
    type: str = field(default="image", init=False)


@dataclass
class MultiStaticSelectMenu(Element):
    """
    Works with block types: SectionBlock, InputBlock
    This is the simplest form of select menu, with a static list of options passed in when defining the element.
    """

    placeholder: Text
    action_id: str
    options: List[Option]
    option_groups: List[OptionGroup] = None
    initial_options: List[Optional[Union[Option, OptionGroup]]] = None
    confirm: Optional[Confirmation] = None
    max_selected_items: Optional[int] = None
    focus_on_load: Optional[bool] = None
    type: str = field(default="multi_static_select", init=False)

    def __post_init__(self):
        if len(self.action_id) > 255:
            raise ValueError(
                f"MultiStaticSelectMenu action_id can only be 255 characters long."
            )

        if len(self.placeholder.text) > 150:
            raise ValueError(
                f"MultiStaticSelectMenu placeholder can only be 150 characters long."
            )

        if len(self.options) > 100:
            raise ValueError(
                f"MultiStaticSelectMenu options can only be 100 items long."
            )

        if self.option_groups and len(self.option_groups) > 100:
            raise ValueError(
                f"MultiStaticSelectMenu option_groups can only be 100 items long."
            )

        if self.max_selected_items and len(self.max_selected_items) < 1:
            raise ValueError(
                f"MultiStaticSelectMenu max_selected_items minimum number is 1."
            )


@dataclass
class MultiExternalSelectMenu(Element):
    """
    Works with block types: SectionBlock, InputBlock
    This menu will load its options from an external data source, allowing for a dynamic list of options.
    """

    placeholder: Text
    action_id: str
    min_query_length: Optional[int] = None
    initial_options: List[Optional[Union[Option, OptionGroup]]] = None
    confirm: Optional[Confirmation] = None
    max_selected_items: Optional[int] = None
    focus_on_load: Optional[bool] = None
    type: str = field(default="multi_external_select", init=False)

    def __post_init__(self):
        if len(self.action_id) > 255:
            raise ValueError(
                f"MultiExternalSelectMenu action_id can only be 255 characters long."
            )

        if len(self.placeholder.text) > 150:
            raise ValueError(
                f"MultiExternalSelectMenu placeholder can only be 150 characters long."
            )

        if self.max_selected_items and len(self.max_selected_items) < 1:
            raise ValueError(
                f"MultiExternalSelectMenu max_selected_items minimum number is 1."
            )


@dataclass
class MultiUserSelectMenu(Element):
    """
    Works with block types: SectionBlock, InputBlock
    This multi-select menu will populate its options with a list of Slack users visible to the current user in the active workspace.
    """

    placeholder: Text
    action_id: str
    initial_users: Optional[List[str]] = None
    confirm: Optional[Confirmation] = None
    max_selected_items: Optional[int] = None
    focus_on_load: Optional[bool] = None
    type: str = field(default="multi_users_select", init=False)

    def __post_init__(self):
        if len(self.action_id) > 255:
            raise ValueError(
                f"MultiUserSelectMenu action_id can only be 255 characters long."
            )

        if len(self.placeholder.text) > 150:
            raise ValueError(
                f"MultiUserSelectMenu placeholder can only be 150 characters long."
            )

        if self.max_selected_items and len(self.max_selected_items) < 1:
            raise ValueError(
                f"MultiUserSelectMenu max_selected_items minimum number is 1."
            )


@dataclass
class MultiConversationSelectMenu(Element):
    """
    Works with block types: SectionBlock, InputBlock
    This multi-select menu will populate its options with a list of public and private channels, DMs, and MPIMs visible to the current user in the active workspace.
    """

    placeholder: Text
    action_id: str
    initial_conversations: Optional[List[str]] = None
    default_to_current_conversation: Optional[bool] = None
    confirm: Optional[Confirmation] = None
    max_selected_items: Optional[int] = None
    filter: Optional[Filter] = None
    focus_on_load: Optional[bool] = None
    type: str = field(default="multi_conversations_select", init=False)

    def __post_init__(self):
        if len(self.action_id) > 255:
            raise ValueError(
                f"MultiConversationSelectMenu action_id can only be 255 characters long."
            )

        if len(self.placeholder.text) > 150:
            raise ValueError(
                f"MultiConversationSelectMenu placeholder can only be 150 characters long."
            )

        if self.max_selected_items and len(self.max_selected_items) < 1:
            raise ValueError(
                f"MultiConversationSelectMenu max_selected_items minimum number is 1."
            )


@dataclass
class MultiChannelSelectMenu(Element):
    """
    Works with block types: SectionBlock, InputBlock
    This multi-select menu will populate its options with a list of public channels visible to the current user in the active workspace.
    """

    placeholder: Text
    action_id: str
    initial_channels: Optional[List[str]] = None
    confirm: Optional[Confirmation] = None
    max_selected_items: Optional[int] = None
    focus_on_load: Optional[bool] = None
    type: str = field(default="multi_channels_select", init=False)

    def __post_init__(self):
        if len(self.action_id) > 255:
            raise ValueError(
                f"MultiConversationSelectMenu action_id can only be 255 characters long."
            )

        if len(self.placeholder.text) > 150:
            raise ValueError(
                f"MultiConversationSelectMenu placeholder can only be 150 characters long."
            )

        if self.max_selected_items and len(self.max_selected_items) < 1:
            raise ValueError(
                f"MultiConversationSelectMenu max_selected_items minimum number is 1."
            )


@dataclass
class OverflowMenu(Element):
    """
    Works with block types: SectionBlock, ActionBlock
    This is like a cross between a button and a select menu - when a user clicks on this overflow button, they will be presented with a list of options to choose from.
    Unlike the select menu, there is no typeahead field, and the button always appears with an ellipsis ("…") rather than customisable text.
    """

    action_id: str
    options: List[Option]
    confirm: Optional[Confirmation] = None
    type: str = field(default="overflow", init=False)

    def __post_init__(self):
        if len(self.action_id) > 255:
            raise ValueError(f"OverflowMenu action_id can only be 255 characters long.")

        if len(self.options) > 5 or len(self.options) < 2:
            raise ValueError(
                f"OverflowMenu options maximum number of options is 5, minimum is 2."
            )


@dataclass
class PlainTextInput(Element):
    """
    Works with block types: InputBlock
    A plain-text input, similar to the HTML <input> tag, creates a field where a user can enter freeform data. It can appear as a single-line field or a larger text area using the multiline flag.
    """

    action_id: str
    placeholder: Optional[Text] = None
    initial_value: Optional[str] = None
    multiline: Optional[bool] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    dispatch_action_config: Optional[DispatchAction] = None
    focus_on_load: Optional[bool] = None
    type: str = field(default="plain_text_input", init=False)

    def __post_init__(self):
        if len(self.action_id) > 255:
            raise ValueError(
                f"PlainTextInput action_id can only be 255 characters long."
            )

        if self.placeholder and len(self.placeholder.text) > 150:
            raise ValueError(
                f"PlainTextInput placeholder can only be 150 characters long."
            )

        if self.min_length and len(self.min_length) > 3000:
            raise ValueError(
                f"PlainTextInput min_length can only be 3000 characters long."
            )


@dataclass
class RadioButtonGroup(Element):
    """
    Works with block types: SectionBlock, ActionBlock, InputBlock
    A radio button group that allows a user to choose one item from a list of possible options.
    Radio buttons are supported in the following app surfaces: Home tabs, Modals, Messages
    """

    action_id: str
    options: List[Option]
    initial_option: Optional[Option] = None
    confirm: Optional[Confirmation] = None
    focus_on_load: Optional[bool] = None
    type: str = field(default="radio_buttons", init=False)

    def __post_init__(self):
        if len(self.action_id) > 255:
            raise ValueError(
                f"RadioButtonGroup action_id can only be 255 characters long."
            )

        if len(self.options) > 10:
            raise ValueError(f"RadioButtonGroup options can only be 10 items long.")


@dataclass
class StaticSelectMenu(Element):
    """
    Works with block types: SectionBlock, ActionBlock, InputBlock
    This is the simplest form of select menu, with a static list of options passed in when defining the element
    """

    placeholder: Text
    action_id: str
    options: List[Option]
    option_groups: Optional[List[OptionGroup]] = None
    initial_options: Optional[List[Optional[Union[Option, OptionGroup]]]] = None
    confirm: Optional[Confirmation] = None
    focus_on_load: Optional[bool] = None
    type: str = field(default="static_select", init=False)

    def __post_init__(self):
        if len(self.action_id) > 255:
            raise ValueError(
                f"StaticSelectMenu action_id can only be 255 characters long."
            )

        if len(self.placeholder.text) > 150:
            raise ValueError(
                f"StaticSelectMenu placeholder can only be 150 characters long."
            )

        if len(self.options) > 100:
            raise ValueError(f"StaticSelectMenu options can only be 100 items long.")

        if self.option_groups and len(self.option_groups) > 100:
            raise ValueError(
                f"StaticSelectMenu option_groups can only be 100 items long."
            )


@dataclass
class ExternalSelectMenu(Element):
    """
    Works with block types: SectionBlock, ActionBlock, InputBlock
    This select menu will load its options from an external data source, allowing for a dynamic list of options.
    """

    placeholder: Text
    action_id: str
    initial_options: Optional[List[Union[Option, OptionGroup]]] = None
    min_query_length: Optional[int] = None
    confirm: Optional[Confirmation] = None
    focus_on_load: Optional[bool] = None
    type: str = field(default="external_select", init=False)

    def __post_init__(self):
        if len(self.action_id) > 255:
            raise ValueError(
                f"ExternalSelectMenu action_id can only be 255 characters long."
            )

        if len(self.placeholder.text) > 150:
            raise ValueError(
                f"ExternalSelectMenu placeholder can only be 150 characters long."
            )


@dataclass
class UserSelectMenu(Element):
    """
    Works with block types: SectionBlock, ActionBlock, InputBlock
    This select menu will populate its options with a list of Slack users visible to the current user in the active workspace.
    """

    placeholder: Text
    action_id: str
    initial_users: Optional[str] = None
    confirm: Optional[Confirmation] = None
    focus_on_load: Optional[bool] = None
    type: str = field(default="users_select", init=False)

    def __post_init__(self):
        if len(self.action_id) > 255:
            raise ValueError(
                f"UserSelectMenu action_id can only be 255 characters long."
            )

        if len(self.placeholder.text) > 150:
            raise ValueError(
                f"UserSelectMenu placeholder can only be 150 characters long."
            )


@dataclass
class ConversationSelectMenu(Element):
    """
    Works with block types: SectionBlock, ActionBlock, InputBlock
    This select menu will populate its options with a list of public and private channels, DMs, and MPIMs visible to the current user in the active workspace.
    """

    placeholder: Text
    action_id: str
    initial_conversation: Optional[str] = None
    default_to_current_conversation: Optional[bool] = None
    confirm: Optional[Confirmation] = None
    response_url_enabled: Optional[bool] = None
    filter: Optional[Filter] = None
    focus_on_load: Optional[bool] = None
    type: str = field(default="conversations_select", init=False)

    def __post_init__(self):
        if len(self.action_id) > 255:
            raise ValueError(
                f"ConversationSelectMenu action_id can only be 255 characters long."
            )

        if len(self.placeholder.text) > 150:
            raise ValueError(
                f"ConversationSelectMenu placeholder can only be 150 characters long."
            )


@dataclass
class ChannelSelectMenu(Element):
    """
    Works with block types: SectionBlock, ActionBlock, InputBlock
    This select menu will populate its options with a list of public channels visible to the current user in the active workspace.
    """

    placeholder: Text
    action_id: str
    initial_channel: Optional[str] = None
    confirm: Optional[Confirmation] = None
    response_url_enabled: Optional[bool] = None
    focus_on_load: Optional[bool] = None
    type: str = field(default="channels_select", init=False)

    def __post_init__(self):
        if len(self.action_id) > 255:
            raise ValueError(
                f"ChannelSelectMenu action_id can only be 255 characters long."
            )

        if len(self.placeholder.text) > 150:
            raise ValueError(
                f"ChannelSelectMenu placeholder can only be 150 characters long."
            )


@dataclass
class TimePicker(Element):
    """
    Works with block types: SectionBlock, ActionBlock, InputBlock
    An element which allows selection of a time of day.
    On desktop clients, this time picker will take the form of a dropdown list with free-text entry for precise choices. On mobile clients, the time picker will use native time picker UIs.
    """

    action_id: str
    placeholder: Optional[Text] = None
    initial_time: Optional[str] = None
    confirm: Optional[Confirmation] = None
    focus_on_load: Optional[bool] = None
    type: str = field(default="timepicker", init=False)

    def __post_init__(self):
        if len(self.action_id) > 255:
            raise ValueError(f"TimePicker action_id can only be 255 characters long.")

        if self.placeholder and len(self.placeholder.text) > 150:
            raise ValueError(f"TimePicker placeholder can only be 150 characters long.")
