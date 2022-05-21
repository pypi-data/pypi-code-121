from __future__ import annotations

from typing import Union

from pydantic import BaseModel, Field

__all__ = [
    'Type',
    'Update',
    'WebhookInfo',
    'User',
    'Chat',
    'Message',
    'MessageId',
    'MessageEntity',
    'PhotoSize',
    'Animation',
    'Audio',
    'Document',
    'Video',
    'VideoNote',
    'Voice',
    'Contact',
    'Dice',
    'PollOption',
    'PollAnswer',
    'Poll',
    'Location',
    'Venue',
    'WebAppData',
    'ProximityAlertTriggered',
    'MessageAutoDeleteTimerChanged',
    'VideoChatScheduled',
    'VideoChatStarted',
    'VideoChatEnded',
    'VideoChatParticipantsInvited',
    'UserProfilePhotos',
    'File',
    'WebAppInfo',
    'ReplyKeyboardMarkup',
    'KeyboardButton',
    'KeyboardButtonPollType',
    'ReplyKeyboardRemove',
    'InlineKeyboardMarkup',
    'InlineKeyboardButton',
    'LoginUrl',
    'CallbackQuery',
    'ForceReply',
    'ChatPhoto',
    'ChatInviteLink',
    'ChatAdministratorRights',
    'ChatMember',
    'ChatMemberOwner',
    'ChatMemberAdministrator',
    'ChatMemberMember',
    'ChatMemberRestricted',
    'ChatMemberLeft',
    'ChatMemberBanned',
    'ChatMemberUpdated',
    'ChatJoinRequest',
    'ChatPermissions',
    'ChatLocation',
    'BotCommand',
    'BotCommandScope',
    'BotCommandScopeDefault',
    'BotCommandScopeAllPrivateChats',
    'BotCommandScopeAllGroupChats',
    'BotCommandScopeAllChatAdministrators',
    'BotCommandScopeChat',
    'BotCommandScopeChatAdministrators',
    'BotCommandScopeChatMember',
    'MenuButton',
    'MenuButtonCommands',
    'MenuButtonWebApp',
    'MenuButtonDefault',
    'ResponseParameters',
    'InputMedia',
    'InputMediaPhoto',
    'InputMediaVideo',
    'InputMediaAnimation',
    'InputMediaAudio',
    'InputMediaDocument',
    'InputFile',
    'Sticker',
    'StickerSet',
    'MaskPosition',
    'InlineQuery',
    'InlineQueryResult',
    'InlineQueryResultArticle',
    'InlineQueryResultPhoto',
    'InlineQueryResultGif',
    'InlineQueryResultMpeg4Gif',
    'InlineQueryResultVideo',
    'InlineQueryResultAudio',
    'InlineQueryResultVoice',
    'InlineQueryResultDocument',
    'InlineQueryResultLocation',
    'InlineQueryResultVenue',
    'InlineQueryResultContact',
    'InlineQueryResultGame',
    'InlineQueryResultCachedPhoto',
    'InlineQueryResultCachedGif',
    'InlineQueryResultCachedMpeg4Gif',
    'InlineQueryResultCachedSticker',
    'InlineQueryResultCachedDocument',
    'InlineQueryResultCachedVideo',
    'InlineQueryResultCachedVoice',
    'InlineQueryResultCachedAudio',
    'InputMessageContent',
    'InputTextMessageContent',
    'InputLocationMessageContent',
    'InputVenueMessageContent',
    'InputContactMessageContent',
    'InputInvoiceMessageContent',
    'ChosenInlineResult',
    'SentWebAppMessage',
    'LabeledPrice',
    'Invoice',
    'ShippingAddress',
    'OrderInfo',
    'ShippingOption',
    'SuccessfulPayment',
    'ShippingQuery',
    'PreCheckoutQuery',
    'PassportData',
    'PassportFile',
    'EncryptedPassportElement',
    'EncryptedCredentials',
    'PassportElementError',
    'PassportElementErrorDataField',
    'PassportElementErrorFrontSide',
    'PassportElementErrorReverseSide',
    'PassportElementErrorSelfie',
    'PassportElementErrorFile',
    'PassportElementErrorFiles',
    'PassportElementErrorTranslationFile',
    'PassportElementErrorTranslationFiles',
    'PassportElementErrorUnspecified',
    'Game',
    'CallbackGame',
    'GameHighScore',
]


class Type(BaseModel):
    pass


# === Getting updates


class Update(Type):
    update_id: int
    message: Message = None
    edited_message: Message = None
    channel_post: Message = None
    edited_channel_post: Message = None
    inline_query: InlineQuery = None
    chosen_inline_result: ChosenInlineResult = None
    callback_query: CallbackQuery = None
    shipping_query: ShippingQuery = None
    pre_checkout_query: PreCheckoutQuery = None
    poll: Poll = None
    poll_answer: PollAnswer = None
    my_chat_member: ChatMemberUpdated = None
    chat_member: ChatMemberUpdated = None
    chat_join_request: ChatJoinRequest = None


class WebhookInfo(Type):
    url: str
    has_custom_certificate: bool
    pending_update_count: int
    ip_address: str = None
    last_error_date: int = None
    last_error_message: str = None
    last_synchronization_error_date: int = None
    max_connections: int = None
    allowed_updates: list[str] = None


# === Available types

class User(Type):
    id: int
    is_bot: bool
    first_name: str
    last_name: str = None
    username: str = None
    language_code: str = None
    can_join_groups: bool = None
    can_read_all_group_messages: bool = None
    supports_inline_queries: bool = None


class Chat(Type):
    id: int
    type: str
    title: str = None
    username: str = None
    first_name: str = None
    last_name: str = None
    photo: ChatPhoto = None
    bio: str = None
    has_private_forwards: bool = None
    description: str = None
    invite_link: str = None
    pinned_message: Message = None
    permissions: ChatPermissions = None
    slow_mode_delay: int = None
    message_auto_delete_time: int = None
    has_protected_content: bool = None
    sticker_set_name: str = None
    can_set_sticker_set: bool = None
    linked_chat_id: int = None
    location: ChatLocation = None


class Message(Type):
    message_id: int
    from_user: User = Field(default=None, alias='from')
    sender_chat: Chat = None
    date: int
    chat: Chat
    forward_from: User = None
    forward_from_chat: Chat = None
    forward_from_message_id: int = None
    forward_signature: str = None
    forward_sender_name: str = None
    forward_date: int = None
    is_automatic_forward: bool = None
    reply_to_message: Message = None
    via_bot: User = None
    edit_date: int = None
    has_protected_content: bool = None
    media_group_id: str = None
    author_signature: str = None
    text: str = None
    entities: list[MessageEntity] = None
    animation: Animation = None
    audio: Audio = None
    document: Document = None
    photo: list[PhotoSize] = None
    sticker: Sticker = None
    video: Video = None
    video_note: VideoNote = None
    voice: Voice = None
    caption: str = None
    caption_entities: list[MessageEntity] = None
    contact: Contact = None
    dice: Dice = None
    game: Game = None
    poll: Poll = None
    venue: Venue = None
    location: Location = None
    new_chat_members: list[User] = None
    left_chat_member: User = None
    new_chat_title: str = None
    new_chat_photo: list[PhotoSize] = None
    delete_chat_photo: bool = None
    group_chat_created: bool = None
    supergroup_chat_created: bool = None
    channel_chat_created: bool = None
    message_auto_delete_timer_changed: MessageAutoDeleteTimerChanged = None
    migrate_to_chat_id: int = None
    migrate_from_chat_id: int = None
    pinned_message: Message = None
    invoice: Invoice = None
    successful_payment: SuccessfulPayment = None
    connected_website: str = None
    passport_data: PassportData = None
    proximity_alert_triggered: ProximityAlertTriggered = None
    video_chat_scheduled: VideoChatScheduled = None
    video_chat_started: VideoChatStarted = None
    video_chat_ended: VideoChatEnded = None
    video_chat_participants_invited: VideoChatParticipantsInvited = None
    web_app_data: WebAppData = None
    reply_markup: InlineKeyboardMarkup = None


class MessageId(Type):
    message_id: int


class MessageEntity(Type):
    type: str
    offset: int
    length: int
    url: str = None
    user: User = None
    language: str = None


class PhotoSize(Type):
    file_id: str
    file_unique_id: str
    width: int
    height: int
    file_size: int = None


class Animation(Type):
    file_id: str
    file_unique_id: str
    width: int
    height: int
    duration: int
    thumb: PhotoSize = None
    file_name: str = None
    mime_type: str = None
    file_size: int = None


class Audio(Type):
    file_id: str
    file_unique_id: str
    duration: int
    performer: str = None
    title: str = None
    file_name: str = None
    mime_type: str = None
    file_size: int = None
    thumb: PhotoSize = None


class Document(Type):
    file_id: str
    file_unique_id: str
    thumb: PhotoSize = None
    file_name: str = None
    mime_type: str = None
    file_size: int = None


class Video(Type):
    file_id: str
    file_unique_id: str
    width: int
    height: int
    duration: int
    thumb: PhotoSize = None
    file_name: str = None
    mime_type: str = None
    file_size: int = None


class VideoNote(Type):
    file_id: str
    file_unique_id: str
    length: int
    duration: int
    thumb: PhotoSize = None
    file_size: int = None


class Voice(Type):
    file_id: str
    file_unique_id: str
    duration: int
    mime_type: str = None
    file_size: int = None


class Contact(Type):
    phone_number: str
    first_name: str
    last_name: str = None
    user_id: int = None
    vcard: str = None


class Dice(Type):
    emoji: str
    value: int


class PollOption(Type):
    text: str
    voter_count: int


class PollAnswer(Type):
    poll_id: str
    user: User
    option_ids: list[int]


class Poll(Type):
    id: str
    question: str
    options: list[PollOption]
    total_voter_count: int
    is_closed: bool
    is_anonymous: bool
    type: str
    allows_multiple_answers: bool
    correct_option_id: int = None
    explanation: str = None
    explanation_entities: list[MessageEntity] = None
    open_period: int = None
    close_date: int = None


class Location(Type):
    longitude: float
    latitude: float
    horizontal_accuracy: float = None
    live_period: int = None
    heading: int = None
    proximity_alert_radius: int = None


class Venue(Type):
    location: Location
    title: str
    address: str
    foursquare_id: str = None
    foursquare_type: str = None
    google_place_id: str = None
    google_place_type: str = None


class WebAppData(Type):
    data: str
    button_text: str


class ProximityAlertTriggered(Type):
    traveler: User
    watcher: User
    distance: int


class MessageAutoDeleteTimerChanged(Type):
    message_auto_delete_time: int


class VideoChatScheduled(Type):
    start_date: int


class VideoChatStarted(Type):
    pass


class VideoChatEnded(Type):
    duration: int


class VideoChatParticipantsInvited(Type):
    users: list[User]


class UserProfilePhotos(Type):
    total_count: int
    photos: list[list[PhotoSize]]


class File(Type):
    file_id: str
    file_unique_id: str
    file_size: int = None
    file_path: str = None


class WebAppInfo(Type):
    url: str


class ReplyKeyboardMarkup(Type):
    keyboard: list[list[KeyboardButton]]
    resize_keyboard: bool = None
    one_time_keyboard: bool = None
    input_field_placeholder: str = None
    selective: bool = None


class KeyboardButton(Type):
    text: str
    request_contact: bool = None
    request_location: bool = None
    request_poll: KeyboardButtonPollType = None
    web_app: WebAppInfo = None


class KeyboardButtonPollType(Type):
    type: str = None


class ReplyKeyboardRemove(Type):
    remove_keyboard: bool
    selective: bool = None


class InlineKeyboardMarkup(Type):
    inline_keyboard: list[list[InlineKeyboardButton]]


class InlineKeyboardButton(Type):
    text: str
    url: str = None
    callback_data: str = None
    web_app: WebAppInfo = None
    login_url: LoginUrl = None
    switch_inline_query: str = None
    switch_inline_query_current_chat: str = None
    callback_game: CallbackGame = None
    pay: bool = None


class LoginUrl(Type):
    url: str
    forward_text: str = None
    bot_username: str = None
    request_write_access: bool = None


class CallbackQuery(Type):
    id: str
    from_user: User = Field(alias='from')
    message: Message = None
    inline_message_id: str = None
    chat_instance: str
    data: str = None
    game_short_name: str = None


class ForceReply(Type):
    force_reply: bool
    input_field_placeholder: str = None
    selective: bool = None


class ChatPhoto(Type):
    small_file_id: str
    small_file_unique_id: str
    big_file_id: str
    big_file_unique_id: str


class ChatInviteLink(Type):
    invite_link: str
    creator: User
    creates_join_request: bool
    is_primary: bool
    is_revoked: bool
    name: str = None
    expire_date: int = None
    member_limit: int = None
    pending_join_request_count: int = None


class ChatAdministratorRights(Type):
    is_anonymous: bool
    can_manage_chat: bool
    can_delete_messages: bool
    can_manage_video_chats: bool
    can_restrict_members: bool
    can_promote_members: bool
    can_change_info: bool
    can_invite_users: bool
    can_post_messages: bool = None
    can_edit_messages: bool = None
    can_pin_messages: bool = None


class ChatMember(Type):
    status: str
    user: User


class ChatMemberOwner(ChatMember):
    status: str = 'creator'
    user: User
    is_anonymous: bool
    custom_title: str = None


class ChatMemberAdministrator(ChatMember):
    status: str = 'administrator'
    user: User
    can_be_edited: bool
    is_anonymous: bool
    can_manage_chat: bool
    can_delete_messages: bool
    can_manage_video_chats: bool
    can_restrict_members: bool
    can_promote_members: bool
    can_change_info: bool
    can_invite_users: bool
    can_post_messages: bool = None
    can_edit_messages: bool = None
    can_pin_messages: bool = None
    custom_title: str = None


class ChatMemberMember(ChatMember):
    status: str = 'member'
    user: User


class ChatMemberRestricted(ChatMember):
    status: str = 'restricted'
    user: User
    is_member: bool
    can_change_info: bool
    can_invite_users: bool
    can_pin_messages: bool
    can_send_messages: bool
    can_send_media_messages: bool
    can_send_polls: bool
    can_send_other_messages: bool
    can_add_web_page_previews: bool
    until_date: int


class ChatMemberLeft(ChatMember):
    status: str = 'left'
    user: User


class ChatMemberBanned(ChatMember):
    status: str = 'kicked'
    user: User
    until_date: int


class ChatMemberUpdated(Type):
    chat: Chat
    from_user: User = Field(alias='from')
    date: int
    old_chat_member: ChatMember
    new_chat_member: ChatMember
    invite_link: ChatInviteLink = None


class ChatJoinRequest(Type):
    chat: Chat
    from_user: User = Field(alias='from')
    date: int
    bio: str = None
    invite_link: ChatInviteLink = None


class ChatPermissions(Type):
    can_send_messages: bool = None
    can_send_media_messages: bool = None
    can_send_polls: bool = None
    can_send_other_messages: bool = None
    can_add_web_page_previews: bool = None
    can_change_info: bool = None
    can_invite_users: bool = None
    can_pin_messages: bool = None


class ChatLocation(Type):
    location: Location
    address: str


class BotCommand(Type):
    command: str
    description: str


class BotCommandScope(Type):
    type: str


class BotCommandScopeDefault(BotCommandScope):
    type: str = 'default'


class BotCommandScopeAllPrivateChats(BotCommandScope):
    type: str = 'all_private_chats'


class BotCommandScopeAllGroupChats(BotCommandScope):
    type: str = 'all_group_chats'


class BotCommandScopeAllChatAdministrators(BotCommandScope):
    type: str = 'all_chat_administrators'


class BotCommandScopeChat(BotCommandScope):
    chat_id: Union[int, str]
    type: str = 'chat'


class BotCommandScopeChatAdministrators(BotCommandScope):
    type: str = 'chat_administrators'
    chat_id: Union[int, str]


class BotCommandScopeChatMember(BotCommandScope):
    type: str = 'chat_member'
    chat_id: Union[int, str]
    user_id: int


class MenuButton(Type):
    pass


class MenuButtonCommands(MenuButton):
    type: str


class MenuButtonWebApp(MenuButton):
    type: str
    text: str
    web_app: WebAppInfo


class MenuButtonDefault(MenuButton):
    type: str


class ResponseParameters(Type):
    migrate_to_chat_id: int = None
    retry_after: int = None


class InputMedia(Type):
    pass


class InputMediaPhoto(InputMedia):
    type: str
    media: str
    caption: str = None
    parse_mode: str = None
    caption_entities: list[MessageEntity] = None


class InputMediaVideo(InputMedia):
    type: str
    media: str
    thumb: InputFile or str = None
    caption: str = None
    parse_mode: str = None
    caption_entities: list[MessageEntity] = None
    width: int = None
    height: int = None
    duration: int = None
    supports_streaming: bool = None


class InputMediaAnimation(InputMedia):
    type: str
    media: str
    thumb: InputFile or str = None
    caption: str = None
    parse_mode: str = None
    caption_entities: list[MessageEntity] = None
    width: int = None
    height: int = None
    duration: int = None


class InputMediaAudio(InputMedia):
    type: str
    media: str
    thumb: InputFile or str = None
    caption: str = None
    parse_mode: str = None
    caption_entities: list[MessageEntity] = None
    duration: int = None
    performer: str = None
    title: str = None


class InputMediaDocument(InputMedia):
    type: str
    media: str
    thumb: InputFile or str = None
    caption: str = None
    parse_mode: str = None
    caption_entities: list[MessageEntity] = None
    disable_content_type_detection: bool = None


class InputFile(Type):
    pass


# === Stickers


class Sticker(Type):
    file_id: str
    file_unique_id: str
    width: int
    height: int
    is_animated: bool
    is_video: bool
    thumb: PhotoSize = None
    emoji: str = None
    set_name: str = None
    mask_position: MaskPosition = None
    file_size: int = None


class StickerSet(Type):
    name: str
    title: str
    is_animated: bool
    is_video: bool
    contains_masks: bool
    stickers: list[Sticker]
    thumb: PhotoSize = None


class MaskPosition(Type):
    point: str
    x_shift: float
    y_shift: float
    scale: float


# === Inline mode

class InlineQuery(Type):
    id: str
    from_user: User = Field(alias='from')
    query: str
    offset: str
    chat_type: str = None
    location: Location = None


class InlineQueryResult(Type):
    pass


class InlineQueryResultArticle(InlineQueryResult):
    type: str
    id: str
    title: str
    input_message_content: InputMessageContent
    reply_markup: InlineKeyboardMarkup = None
    url: str = None
    hide_url: bool = None
    description: str = None
    thumb_url: str = None
    thumb_width: int = None
    thumb_height: int = None


class InlineQueryResultPhoto(InlineQueryResult):
    type: str
    id: str
    photo_url: str
    thumb_url: str
    photo_width: int = None
    photo_height: int = None
    title: str = None
    description: str = None
    caption: str = None
    parse_mode: str = None
    caption_entities: list[MessageEntity] = None
    reply_markup: InlineKeyboardMarkup = None
    input_message_content: InputMessageContent = None


class InlineQueryResultGif(InlineQueryResult):
    type: str
    id: str
    gif_url: str
    gif_width: int = None
    gif_height: int = None
    gif_duration: int = None
    thumb_url: str
    thumb_mime_type: str = None
    title: str = None
    caption: str = None
    parse_mode: str = None
    caption_entities: list[MessageEntity] = None
    reply_markup: InlineKeyboardMarkup = None
    input_message_content: InputMessageContent = None


class InlineQueryResultMpeg4Gif(InlineQueryResult):
    type: str
    id: str
    mpeg4_url: str
    mpeg4_width: int = None
    mpeg4_height: int = None
    mpeg4_duration: int = None
    thumb_url: str
    thumb_mime_type: str = None
    title: str = None
    caption: str = None
    parse_mode: str = None
    caption_entities: list[MessageEntity] = None
    reply_markup: InlineKeyboardMarkup = None
    input_message_content: InputMessageContent = None


class InlineQueryResultVideo(InlineQueryResult):
    type: str
    id: str
    video_url: str
    mime_type: str
    thumb_url: str
    title: str
    caption: str = None
    parse_mode: str = None
    caption_entities: list[MessageEntity] = None
    video_width: int = None
    video_height: int = None
    video_duration: int = None
    description: str = None
    reply_markup: InlineKeyboardMarkup = None
    input_message_content: InputMessageContent = None


class InlineQueryResultAudio(InlineQueryResult):
    type: str
    id: str
    audio_url: str
    title: str
    caption: str = None
    parse_mode: str = None
    caption_entities: list[MessageEntity] = None
    performer: str = None
    audio_duration: int = None
    reply_markup: InlineKeyboardMarkup = None
    input_message_content: InputMessageContent = None


class InlineQueryResultVoice(InlineQueryResult):
    type: str
    id: str
    voice_url: str
    title: str
    caption: str = None
    parse_mode: str = None
    caption_entities: list[MessageEntity] = None
    voice_duration: int = None
    reply_markup: InlineKeyboardMarkup = None
    input_message_content: InputMessageContent = None


class InlineQueryResultDocument(InlineQueryResult):
    type: str
    id: str
    title: str
    caption: str = None
    parse_mode: str = None
    caption_entities: list[MessageEntity] = None
    document_url: str
    mime_type: str
    description: str = None
    reply_markup: InlineKeyboardMarkup = None
    input_message_content: InputMessageContent = None
    thumb_url: str = None
    thumb_width: int = None
    thumb_height: int = None


class InlineQueryResultLocation(InlineQueryResult):
    type: str
    id: str
    latitude: float
    longitude: float
    title: str
    horizontal_accuracy: float = None
    live_period: int = None
    heading: int = None
    proximity_alert_radius: int = None
    reply_markup: InlineKeyboardMarkup = None
    input_message_content: InputMessageContent = None
    thumb_url: str = None
    thumb_width: int = None
    thumb_height: int = None


class InlineQueryResultVenue(InlineQueryResult):
    type: str
    id: str
    latitude: float
    longitude: float
    title: str
    address: str
    foursquare_id: str = None
    foursquare_type: str = None
    google_place_id: str = None
    google_place_type: str = None
    reply_markup: InlineKeyboardMarkup = None
    input_message_content: InputMessageContent = None
    thumb_url: str = None
    thumb_width: int = None
    thumb_height: int = None


class InlineQueryResultContact(InlineQueryResult):
    type: str
    id: str
    phone_number: str
    first_name: str
    last_name: str = None
    vcard: str = None
    reply_markup: InlineKeyboardMarkup = None
    input_message_content: InputMessageContent = None
    thumb_url: str = None
    thumb_width: int = None
    thumb_height: int = None


class InlineQueryResultGame(InlineQueryResult):
    type: str
    id: str
    game_short_name: str
    reply_markup: InlineKeyboardMarkup = None


class InlineQueryResultCachedPhoto(InlineQueryResult):
    type: str
    id: str
    photo_file_id: str
    title: str = None
    description: str = None
    caption: str = None
    parse_mode: str = None
    caption_entities: list[MessageEntity] = None
    reply_markup: InlineKeyboardMarkup = None
    input_message_content: InputMessageContent = None


class InlineQueryResultCachedGif(InlineQueryResult):
    type: str
    id: str
    gif_file_id: str
    title: str = None
    caption: str = None
    parse_mode: str = None
    caption_entities: list[MessageEntity] = None
    reply_markup: InlineKeyboardMarkup = None
    input_message_content: InputMessageContent = None


class InlineQueryResultCachedMpeg4Gif(InlineQueryResult):
    type: str
    id: str
    mpeg4_file_id: str
    title: str = None
    caption: str = None
    parse_mode: str = None
    caption_entities: list[MessageEntity] = None
    reply_markup: InlineKeyboardMarkup = None
    input_message_content: InputMessageContent = None


class InlineQueryResultCachedSticker(InlineQueryResult):
    type: str
    id: str
    sticker_file_id: str
    reply_markup: InlineKeyboardMarkup = None
    input_message_content: InputMessageContent = None


class InlineQueryResultCachedDocument(InlineQueryResult):
    type: str
    id: str
    title: str
    document_file_id: str
    description: str = None
    caption: str = None
    parse_mode: str = None
    caption_entities: list[MessageEntity] = None
    reply_markup: InlineKeyboardMarkup = None
    input_message_content: InputMessageContent = None


class InlineQueryResultCachedVideo(InlineQueryResult):
    type: str
    id: str
    video_file_id: str
    title: str
    description: str = None
    caption: str = None
    parse_mode: str = None
    caption_entities: list[MessageEntity] = None
    reply_markup: InlineKeyboardMarkup = None
    input_message_content: InputMessageContent = None


class InlineQueryResultCachedVoice(InlineQueryResult):
    type: str
    id: str
    voice_file_id: str
    title: str
    caption: str = None
    parse_mode: str = None
    caption_entities: list[MessageEntity] = None
    reply_markup: InlineKeyboardMarkup = None
    input_message_content: InputMessageContent = None


class InlineQueryResultCachedAudio(InlineQueryResult):
    type: str
    id: str
    audio_file_id: str
    caption: str = None
    parse_mode: str = None
    caption_entities: list[MessageEntity] = None
    reply_markup: InlineKeyboardMarkup = None
    input_message_content: InputMessageContent = None


class InputMessageContent(Type):
    pass


class InputTextMessageContent(InputMessageContent):
    message_text: str
    parse_mode: str = None
    entities: list[MessageEntity] = None
    disable_web_page_preview: bool = None


class InputLocationMessageContent(InputMessageContent):
    latitude: float
    longitude: float
    horizontal_accuracy: float = None
    live_period: int = None
    heading: int = None
    proximity_alert_radius: int = None


class InputVenueMessageContent(InputMessageContent):
    latitude: float
    longitude: float
    title: str
    address: str
    foursquare_id: str = None
    foursquare_InputMessageContent: str = None
    google_place_id: str = None
    google_place_InputMessageContent: str = None


class InputContactMessageContent(InputMessageContent):
    phone_number: str
    first_name: str
    last_name: str = None
    vcard: str = None


class InputInvoiceMessageContent(InputMessageContent):
    title: str
    description: str
    payload: str
    provider_token: str
    currency: str
    prices: list[LabeledPrice]
    max_tip_amount: int = None
    suggested_tip_amounts: list[int] = None
    provider_data: str = None
    photo_url: str = None
    photo_size: int = None
    photo_width: int = None
    photo_height: int = None
    need_name: bool = None
    need_phone_number: bool = None
    need_email: bool = None
    need_shipping_address: bool = None
    send_phone_number_to_provider: bool = None
    send_email_to_provider: bool = None
    is_flexible: bool = None


class ChosenInlineResult(Type):
    result_id: str
    from_user: User = Field(alias='from')
    location: Location = None
    inline_message_id: str = None
    query: str


class SentWebAppMessage(Type):
    inline_message_id: str = None


# === Payments


class LabeledPrice(Type):
    label: str
    amount: int


class Invoice(Type):
    title: str
    description: str
    start_parameter: str
    currency: str
    total_amount: int


class ShippingAddress(Type):
    country_code: str
    state: str
    city: str
    street_line1: str
    street_line2: str
    post_code: str


class OrderInfo(Type):
    name: str = None
    phone_number: str = None
    email: str = None
    shipping_address: ShippingAddress = None


class ShippingOption(Type):
    id: str
    title: str
    prices: list[LabeledPrice]


class SuccessfulPayment(Type):
    currency: str
    total_amount: int
    invoice_payload: str
    shipping_option_id: str = None
    order_info: OrderInfo = None
    telegram_payment_charge_id: str
    provider_payment_charge_id: str


class ShippingQuery(Type):
    id: str
    from_user: User = Field(alias='from')
    invoice_payload: str
    shipping_address: ShippingAddress


class PreCheckoutQuery(Type):
    id: str
    from_user: User = Field(alias='from')
    currency: str
    total_amount: int
    invoice_payload: str
    shipping_option_id: str = None
    order_info: OrderInfo = None


# === Telegram Passport

class PassportData(Type):
    data: list[EncryptedPassportElement]
    credentials: EncryptedCredentials


class PassportFile(Type):
    file_id: str
    file_unique_id: str
    file_size: int
    file_date: int


class EncryptedPassportElement(Type):
    type: str
    data: str = None
    phone_number: str = None
    email: str = None
    files: list[PassportFile] = None
    front_side: PassportFile = None
    reverse_side: PassportFile = None
    selfie: PassportFile = None
    translation: list[PassportFile] = None
    hash: str


class EncryptedCredentials(Type):
    data: str
    hash: str
    secret: str


class PassportElementError(Type):
    pass


class PassportElementErrorDataField(PassportElementError):
    source: str
    type: str
    field_name: str
    data_hash: str
    message: str


class PassportElementErrorFrontSide(PassportElementError):
    source: str
    type: str
    file_hash: str
    message: str


class PassportElementErrorReverseSide(PassportElementError):
    source: str
    type: str
    file_hash: str
    message: str


class PassportElementErrorSelfie(PassportElementError):
    source: str
    type: str
    file_hash: str
    message: str


class PassportElementErrorFile(PassportElementError):
    source: str
    type: str
    file_hash: str
    message: str


class PassportElementErrorFiles(PassportElementError):
    source: str
    type: str
    file_hashes: list[str]
    message: str


class PassportElementErrorTranslationFile(PassportElementError):
    source: str
    type: str
    file_hash: str
    message: str


class PassportElementErrorTranslationFiles(PassportElementError):
    source: str
    type: str
    file_hashes: list[str]
    message: str


class PassportElementErrorUnspecified(PassportElementError):
    source: str
    type: str
    element_hash: str
    message: str


# === Games

class Game(Type):
    title: str
    description: str
    photo: list[PhotoSize]
    text: str = None
    text_entities: list[MessageEntity] = None
    animation: Animation = None


class CallbackGame(Type):
    user_id: int
    score: int
    force: bool = None
    disable_edit_message: bool = None
    chat_id: int = None
    message_id: int = None
    inline_message_id: str = None


class GameHighScore(Type):
    position: int
    user: User
    score: int


# fix pydantic errors
for i in __all__:
    _type: Type = locals()[i]
    _type.update_forward_refs()
