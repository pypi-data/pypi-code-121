from . import filters
from .loader import bot


def on_text(
        value: str = None,
        user_id: int | list[int] = None,
        chat_type: str | list[str] = None,
        state: str = None,
):
    fs = []

    if value:
        fs.append(filters.Text(value))

    if user_id:
        fs.append(filters.UserId(user_id))

    if chat_type:
        fs.append(filters.ChatType(chat_type))

    fs.append(filters.State(state))

    def _(func):
        bot.add_handler(func, fs)
        return func

    return _


def on_command(
        value: str = None,
        user_id: int | list[int] = None,
        chat_type: str | list[str] = None,
        state: str = None,
):
    fs = []

    if value:
        fs.append(filters.Command(value))

    if user_id:
        fs.append(filters.UserId(user_id))

    if chat_type:
        fs.append(filters.ChatType(chat_type))

    fs.append(filters.State(state))

    def _(func):
        bot.add_handler(func, fs)
        return func

    return _


def on_data(
        value: str = None,
        user_id: int | list[int] = None,
        chat_type: str | list[str] = None,
        state: str = None,
):
    fs = []

    if value:
        fs.append(filters.Data(value))

    if user_id:
        fs.append(filters.UserId(user_id))

    if chat_type:
        fs.append(filters.ChatType(chat_type))

    fs.append(filters.State(state))

    def _(func):
        bot.add_handler(func, fs)
        return func

    return _


def on_message(
        user_id: int | list[int] = None,
        chat_type: str | list[str] = None,
        state: str = None,
):
    fs = [filters.Message()]

    if user_id:
        fs.append(filters.UserId(user_id))

    if chat_type:
        fs.append(filters.ChatType(chat_type))

    fs.append(filters.State(state))

    def _(func):
        bot.add_handler(func, fs)
        return func

    return _

# def on_button(value: str = None):
#     ...
