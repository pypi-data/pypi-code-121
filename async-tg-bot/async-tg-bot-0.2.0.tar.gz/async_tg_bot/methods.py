from .loader import bot, ctx
from .types import *


def _get_param(value, default):
    if value is None:
        return default
    return value


def send_message(
        text: str,
        chat_id: int | str = None,
        parse_mode: str = None,
        entities: list[MessageEntity] = None,
        disable_web_page_preview: bool = None,
        disable_notification: bool = None,
        protect_content: bool = None,
        reply_to_message_id: int = None,
        allow_sending_without_reply: bool = None,
        reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardRemove | ForceReply = None,
) -> Message:
    chat_id = _get_param(chat_id, ctx.chat_id)
    parse_mode = _get_param(parse_mode, ctx.parse_mode)
    disable_web_page_preview = _get_param(disable_web_page_preview, ctx.disable_web_page_preview)
    disable_notification = _get_param(disable_notification, ctx.disable_notification)
    protect_content = _get_param(protect_content, ctx.protect_content)

    result: dict = bot.request('sendMessage', locals())
    return Message(**result)


def get_updates(
        offset: int = None,
        limit: int = None,
        timeout: int = None,
        allowed_updates: list[str] = None
) -> list[Update]:
    result = bot.request('GetUpdates', locals())
    return [Update(**i) for i in result]


def get_chat_member(
        chat_id: int | str,
        user_id: int,
) -> ChatMember:
    result: dict = bot.request('getChatMember', locals())

    def cast(chat_member: dict) -> ChatMember:
        _Type = {
            'creator': ChatMemberOwner,
            'administrator': ChatMemberAdministrator,
            'member': ChatMemberMember,
            'restricted': ChatMemberRestricted,
            'left': ChatMemberLeft,
            'kicked': ChatMemberBanned,
        }[chat_member['status']]
        return _Type(**chat_member)

    return cast(result)


def get_my_commands(
        scope: BotCommandScope = None,
        language_code: str = None
) -> list[BotCommand]:
    result: list = bot.request('getMyCommands', locals())
    return [BotCommand(**i) for (i) in result]


def set_my_commands(
        commands: list[BotCommand],
        scope: BotCommandScope = None,
        language_code: str = None,
) -> bool:
    result: bool = bot.request('setMyCommands', locals())
    return result


def answer_callback_query(
        text: str = None,
        callback_query_id: str = None,
        show_alert: bool = None,
        url: str = None,
        cache_time: int = None,
) -> bool:
    callback_query_id = _get_param(callback_query_id, ctx.callback_query_id)

    result: bool = bot.request('AnswerCallbackQuery', locals())
    return result


def create_chat_invite_link(
        chat_id: int | str = None,
        name: str = None,
        expire_date: int = None,
        member_limit: int = None,
        creates_join_request: bool = None,
) -> ChatInviteLink:
    chat_id = _get_param(chat_id, ctx.chat_id)

    result: dict = bot.request('CreateChatInviteLink', locals())
    return ChatInviteLink(**result)


def copy_message(
        chat_id: int | str,
        from_chat_id: int | str = None,
        message_id: int = None,
        caption: str = None,
        parse_mode: str = None,
        caption_entities: list[MessageEntity] = None,
        disable_notification: bool = None,
        protect_content: bool = None,
        reply_to_message_id: int = None,
        allow_sending_without_reply: bool = None,
        reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardRemove | ForceReply = None,
) -> MessageId:
    from_chat_id = _get_param(from_chat_id, ctx.chat_id)
    message_id = _get_param(message_id, ctx.message_id)
    parse_mode = _get_param(parse_mode, ctx.parse_mode)
    disable_notification = _get_param(disable_notification, ctx.disable_notification)
    protect_content = _get_param(protect_content, ctx.protect_content)

    result = bot.request('CopyMessage', locals())
    return MessageId(**result)
