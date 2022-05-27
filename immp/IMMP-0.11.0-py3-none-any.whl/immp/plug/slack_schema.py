from dataclasses import field, fields
from typing import Any, Dict, List, Optional, Union
from typing_extensions import Literal

from immp import dict_dataclass


@dict_dataclass
class Config:

    token: str
    fallback_image: Optional[str] = None
    thread_broadcast: bool = False


@dict_dataclass
class Team:

    @dict_dataclass
    class Prefs:

        display_real_names: bool = False

    id: str
    name: str
    domain: str
    prefs: Prefs


@dict_dataclass
class _Images:

    image_original: Optional[str] = None
    image_512: Optional[str] = None
    image_192: Optional[str] = None
    image_72: Optional[str] = None
    image_48: Optional[str] = None
    image_32: Optional[str] = None
    image_24: Optional[str] = None

    @property
    def best_image(self):
        # Assuming dataclass fields are kept in order.
        for field_ in fields(self):
            if not field_.name.startswith("image_"):
                continue
            url = getattr(self, field_.name)
            if url:
                return url
        else:
            return None


@dict_dataclass
class User:

    @dict_dataclass
    class Profile(_Images):

        real_name: Optional[str] = None
        bot_id: Optional[str] = None

    id: str
    name: str
    profile: Profile


@dict_dataclass
class Bot:

    id: str
    name: str
    icons: _Images
    app_id: Optional[str] = None


@dict_dataclass
class Channel:

    id: str
    name: str


@dict_dataclass
class Direct:

    id: str
    user: str


@dict_dataclass
class FileTombstone:

    id: str
    mode: Literal["tombstone"]


@dict_dataclass
class File:

    @dict_dataclass
    class Shares:

        @dict_dataclass
        class Share:
            ts: str

        public: Optional[Dict[str, Share]] = field(default_factory=dict)
        private: Optional[Dict[str, Share]] = field(default_factory=dict)

    id: str
    pretty_type: str
    url_private: str
    name: Optional[str] = None
    mode: Optional[str] = None
    shares: Optional[Shares] = field(default_factory=Shares)


@dict_dataclass
class Attach:

    fallback: Optional[str] = None
    title: Optional[str] = None
    image_url: Optional[str] = None
    is_msg_unfurl: Optional[bool] = False


@dict_dataclass
class Unfurl(Attach):

    is_msg_unfurl: Literal[True]
    channel_id: str
    ts: str


@dict_dataclass
class BaseMsg:

    @dict_dataclass
    class Edited:
        user: Optional[str] = None

    ts: str
    type: Literal["message"]
    subtype: Optional[str] = None
    hidden: bool = False
    channel: Optional[str] = None
    edited: Optional[Edited] = None
    thread_ts: Optional[str] = None
    files: List[Union[FileTombstone, File]] = field(default_factory=list)
    attachments: List[Attach] = field(default_factory=list)
    is_ephemeral: bool = False


@dict_dataclass
class PlainMsg(BaseMsg):

    text: str
    user: Optional[str] = None
    bot_id: Optional[str] = None
    username: Optional[str] = None
    icons: Optional[Dict[str, str]] = field(default_factory=dict)


@dict_dataclass
class FileCommentMsg(BaseMsg):

    subtype: Literal["file_comment"]


@dict_dataclass
class EditedMsg(BaseMsg):

    subtype: Literal["message_changed"]
    message: PlainMsg
    previous_message: PlainMsg


@dict_dataclass
class DeletedMsg(BaseMsg):

    subtype: Literal["message_deleted"]
    deleted_ts: str


@dict_dataclass
class RenameMsg(PlainMsg):

    subtype: Literal["channel_name", "group_name"]
    name: str


Message = Union[FileCommentMsg, EditedMsg, DeletedMsg, RenameMsg, PlainMsg]


@dict_dataclass
class PrefChangeEvent:

    type: Literal["team_pref_change"]
    name: str
    value: Any


@dict_dataclass
class JoinEvent:

    type: Literal["team_join", "user_change"]
    user: User


@dict_dataclass
class ChannelEvent:

    type: Literal["channel_created", "channel_joined", "channel_rename",
                  "group_created", "group_joined", "group_rename"]
    channel: Channel


@dict_dataclass
class DirectEvent:

    type: Literal["im_created"]
    channel: Direct


@dict_dataclass
class MemberEvent:

    type: Literal["member_joined_channel", "member_left_channel"]
    user: str
    channel: str


Event = Union[Message, PrefChangeEvent, JoinEvent, ChannelEvent, DirectEvent, MemberEvent]
