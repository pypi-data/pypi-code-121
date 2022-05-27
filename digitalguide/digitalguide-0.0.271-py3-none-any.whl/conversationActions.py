from telegram import (ReplyKeyboardRemove,InlineKeyboardButton, InlineKeyboardMarkup, Update)
from telegram.ext import (ConversationHandler, CallbackContext)

from digitalguide.contextActions import telegram_default_name, telegram_save_value_to_context

def telegram_return_end(update: Update, context: CallbackContext):
    return ConversationHandler.END

def telegram_entry_conversation(update: Update, context: CallbackContext):
    if context.args:
        telegram_default_name(update,context)
        telegram_save_value_to_context(update,context, "data", True)
        keyboard = [[InlineKeyboardButton(
            "🐾 Los", callback_data='action:' + context.args[0])]]

        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(
            'Hi, freut mich, dass du dabei bist! Mit einem klick auf "los" kannst du direkt an die richtige Position in der Route springen',
            reply_markup=reply_markup)
        return "NONE"

telegram_action_functions = {"return_end": telegram_return_end,
                    "entry_conversation": telegram_entry_conversation
                    }