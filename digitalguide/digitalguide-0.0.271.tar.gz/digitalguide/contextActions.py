from telegram import (Update)
from telegram.ext import (CallbackContext)

from digitalguide.whatsapp.WhatsAppUpdate import WhatsAppUpdate


def telegram_default_name(update: Update, context: CallbackContext):
    context.user_data["name"] = update.message.from_user.first_name


def whatsapp_default_name(client, update: WhatsAppUpdate, context):
    context["name"] = update.ProfileName


def telegram_save_text_to_context(update: Update, context: CallbackContext, key):
    context.user_data[key] = update.message.text


def whatsapp_save_text_to_context(client, update: WhatsAppUpdate, context, key):
    context[key] = update.Body


def telegram_save_value_to_context(update: Update, context: CallbackContext, key, value):
    context.user_data[key] = value


def whatsapp_save_value_to_context(client, update: WhatsAppUpdate, context, key, value):
    context[key] = value


telegram_action_functions = {"default_name": telegram_default_name,
                             "save_text_to_context": telegram_save_text_to_context,
                             "save_value_to_context": telegram_save_value_to_context
                             }

whatsapp_action_functions = {"default_name": whatsapp_default_name,
                             "save_text_to_context": whatsapp_save_text_to_context,
                             "save_value_to_context": whatsapp_save_value_to_context
                             }
