#
#
# voice-skill-sdk
#
# (C) 2021, Deutsche Telekom AG
#
# This file is distributed under the terms of the MIT license.
# For details see the file LICENSE in the top directory.
#

"""Companion app (cApp) cards"""

from enum import Enum
from warnings import warn
from typing import List, Optional, Text, Union
from skill_sdk.utils.util import CamelModel

# Supported card version
CARD_VERSION = 3

# The only card type available: "GENERIC_DEFAULT"
GENERIC_DEFAULT = "GENERIC_DEFAULT"


class CardAction(Text, Enum):
    """
    Card action link can be either one of internal "deep links" (enumerated below)
        or any external "http/https" URL

    """

    # Present skill details view
    INTERNAL_SKILLS = "internal://deeplink/skills"

    # Present overview of all devices
    INTERNAL_OVERVIEW = "internal://deeplink/speakeroverview"

    # Present device details page of the one device that was spoken into to generate this card
    INTERNAL_DETAILS = "internal://deeplink/speakerdetails"

    # Present feedback page in the app
    INTERNAL_FEEDBACK = "internal://deeplink/feedback"

    # Link to the news section of the app
    INTERNAL_NEWS = "internal://deeplink/news"

    # Present full text of the response in an overlay
    INTERNAL_RESPONSE_TEXT = "internal://showResponseText"

    # Initiate a call to the given phone number.
    INTERNAL_CALL = "internal://deeplink/call/{number}"

    # Open a specified app or the App Store if the app is not installed
    INTERNAL_OPEN_APP = (
        "internal://deeplink/openapp?"
        "aos={aos_package_name}&"
        "iosScheme={ios_url_scheme}&"
        "iosAppStoreId={ios_app_store_id}"
    )


class ListItem(CamelModel):
    """
    List item in Card's list sections
    """

    # List item text
    item_text: Text

    # List item action
    item_action: Optional[Union[CardAction, Text]] = None

    # List item bullet point replacement
    item_icon_url: Optional[Text] = None

    @property
    def title(self):
        """**DEPRECATED**: Item title"""
        warn(
            "ListItem.title is deprecated. Use ListItem.item_text instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return None

    @property
    def icon_url(self):
        """**DEPRECATED**: Item icon URL"""
        warn(
            "ListItem.icon_url is deprecated. Use ListItem.item_icon_url instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return None


class ListSection(CamelModel):
    """
    List section in a Card
    """

    title: Optional[Text] = None
    items: List[ListItem] = []

    def __init__(self, title: Text = None, *, items: List[ListItem] = None):
        super().__init__(title=title, items=items or [])

    def with_list_item(
        self,
        item_text: Union[ListItem, Text],
        item_action: Text = None,
        item_icon_url: Text = None,
    ):
        list_item: ListItem = (
            item_text
            if isinstance(item_text, ListItem)
            else ListItem(
                item_text=item_text,
                item_action=item_action,
                item_icon_url=item_icon_url,
            )
        )
        return self.copy(update=dict(items=self.items + [list_item]))


class CardData(CamelModel):
    """Companion app card data"""

    # Card's icon URL
    icon_url: Optional[Text] = None

    # Card title
    title_text: Optional[Text] = None

    # Card subtitle
    type_description: Optional[Text] = None

    # Card's image URL
    image_url: Optional[Text] = None

    # Prominent text: increased font size, displayed below the image (1 line maximum)
    prominent_text: Optional[Text] = None

    # Prominent text action: uri/url action, triggered when tapping prominent text
    action_prominent_text: Optional[Text] = None

    # Actual card text
    text: Optional[Text] = None

    # Sub-text: decreased font size, displayed below the card text
    # the first 4 lines displayed, the rest is hidden under "Show More"
    sub_text: Optional[Text] = None

    # Optional audio media URL, displayed as media player progress bar
    media_url: Optional[Text] = None

    #
    # Card can have a bullet-like list:
    #   a list section contains items and an optional title
    #   an item has a title and optional iconUrl
    #
    list_sections: Optional[List[ListSection]] = None

    def with_list_section(
        self,
        title: Text,
        items: List[ListItem] = None,
    ):
        list_sections = self.list_sections or []
        return self.copy(
            update=dict(list_sections=list_sections + [ListSection(title, items=items)])
        )

    #
    # **DEPRECATED**: Properties from Card v2.0
    #

    @property
    def action(self):
        """**DEPRECATED**: Action URL linked to the action text"""
        warn(
            "Card.action is deprecated: use ListItem.item_action",
            DeprecationWarning,
            stacklevel=2,
        )
        return None

    @property
    def action_text(self):
        """**DEPRECATED**: Action text"""
        warn(
            "Card.action_text is deprecated: use ListItem.item_action",
            DeprecationWarning,
            stacklevel=2,
        )
        return None


class Card(CamelModel):
    """Card for the companion app"""

    type: Text = GENERIC_DEFAULT
    version: int = CARD_VERSION

    data: CardData

    def __init__(
        self,
        data: CardData = None,
        *,
        icon_url: Text = None,
        title_text: Text = None,
        type_description: Text = None,
        image_url: Text = None,
        prominent_text: Text = None,
        action_prominent_text: Text = None,
        text: Text = None,
        sub_text: Text = None,
        media_url: Text = None,
        list_sections: List[ListSection] = None,
        **kwargs,
    ) -> None:
        super().__init__(
            data=data
            or CardData(
                icon_url=icon_url,
                title_text=title_text,
                type_description=type_description,
                image_url=image_url,
                prominent_text=prominent_text,
                action_prominent_text=action_prominent_text,
                text=text,
                sub_text=sub_text,
                media_url=media_url,
                list_sections=list_sections,
            )
        )

    def __getattr__(self, attr):
        return getattr(self.data, attr)

    def with_list_section(
        self,
        title: Text,
        items: List[ListItem] = None,
    ):
        return self.copy(
            update=dict(data=self.data.with_list_section(title, items=items))
        )

    def with_action(
        self,
        item_text: Text,
        item_action: Union[CardAction, Text],
        item_icon_url: Text = None,
    ) -> "Card":
        """
        Add action to card. This function left for backward compatibility:
        in v3.0 the action item has been removed from cApp card,
        card actions must be defined as action list items within listSections

        This method creates and returns new card,
        replacing listSections field with a single section containing one list action item

        **WARNING**: this will replace existing list section items!

        @param item_text:
        @param item_action:
        @param item_icon_url:

        @return:
        """
        data = self.data.copy(
            update=dict(
                list_sections=[
                    ListSection().with_list_item(
                        item_text=item_text,
                        item_action=item_action,
                        item_icon_url=item_icon_url,
                    )
                ],
            )
        )
        return self.copy(update=dict(data=data))
