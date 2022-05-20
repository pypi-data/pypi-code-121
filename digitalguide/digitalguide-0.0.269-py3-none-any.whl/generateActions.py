import base64
import os
import re
from configparser import ConfigParser
from io import BytesIO

import yaml
from telegram import (CallbackQuery, InlineKeyboardButton,
                      InlineKeyboardMarkup, InputFile, InputMediaPhoto,
                      KeyboardButton, ParseMode, Poll, ReplyKeyboardMarkup,
                      ReplyKeyboardRemove, Update)
from telegram.ext import CallbackContext, ConversationHandler

config = ConfigParser()
config.read('config.ini')

import logging
logger = logging.getLogger()

class callback_query_handler():
    def __init__(self, actions_dict):
        self.actions_dict = actions_dict

    def __call__(self, update: Update, context: CallbackContext):
        query = update.callback_query

        query.answer()
        query.edit_message_reply_markup(InlineKeyboardMarkup([]))
        if query.data.split(":")[0] == "action":
            return self.actions_dict[query.data.split(":")[1]](query, context)
        raise ValueError(
            "This type of operation ({}) is not supported in a callback query handler".format(query.data))


def read_action_yaml(filename, action_functions={}, log_user=True, log_interaction=True):
    with open(filename) as file:
        yaml_dict = yaml.load(file, Loader=yaml.FullLoader)

    actions_dict = {}

    for key, value in yaml_dict.items():
        actions_dict[key] = Action(
            value, action_functions=action_functions, log_user=log_user, log_interaction=log_interaction)

    return actions_dict


class Action():
    def __init__(self, actions, action_functions={}, log_user=True, log_interaction=True):
        self.actions = actions
        self.action_functions = action_functions
        self.log_user = log_user
        self.log_interaction = log_interaction
        if log_user or log_interaction:
            import mongoengine
            dbname = config["bot"]["bot_name"]
            with open("ca-certificate.crt", "w") as text_file:
                text_file.write(os.getenv('DATABASE_CERT'))
            mongoengine.connect(alias=dbname, host="mongodb+srv://" + os.getenv("DATABASE_USERNAME")+":" + os.getenv("DATABASE_PASSWORD") +
                                "@" + os.getenv("DATABASE_HOST") + "/"+dbname+"?authSource=admin&tls=true&tlsCAFile=ca-certificate.crt")

    def __call__(self, update: Update, context: CallbackContext):
        if self.log_user and not ("user_id" in context.user_data.keys()):
            from digitalguide.db_objects import User
            db_user = User(user_id=str(update.effective_user.id),
                           first_name=update.effective_user.first_name,
                           last_name=update.effective_user.last_name,
                           username=update.effective_user.username,
                           language_code=update.effective_user.language_code)
            db_user.save()
            context.user_data["user_id"] = db_user

        if self.log_interaction:
            from digitalguide.db_objects import Interaction
            if type(update) == CallbackQuery:
                if update.message.text:
                    interaction_text = update.message.text
                else:
                    interaction_text = None

                Interaction(user=context.user_data["user_id"],
                            update_id=update.id,
                            first_name=update.from_user.first_name,
                            last_name=update.from_user.last_name,
                            username=update.from_user.username,
                            interaction_full=update.to_dict(),
                            interaction_text=interaction_text,
                            interaction_data=update.data,
                            interaction_id=update.id
                            ).save()
            elif update.poll_answer:
                Interaction(user=context.user_data["user_id"],
                            update_id=update.update_id,
                            interaction_full=update.poll_answer.to_dict(),
                            first_name=update.effective_user.first_name,
                            last_name=update.effective_user.last_name,
                            username=update.effective_user.username,
                            interaction_data=str(
                                update.poll_answer.option_ids),
                            interaction_id=update.poll_answer.poll_id
                            ).save()
            else:
                if update.effective_message.text:
                    message_text = update.effective_message.text
                else:
                    message_text = None

                Interaction(user=context.user_data["user_id"],
                            update_id=update.update_id,
                            interaction_full=update.effective_message.to_dict(),
                            first_name=update.effective_user.first_name,
                            last_name=update.effective_user.last_name,
                            username=update.effective_user.username,
                            interaction_text=message_text,
                            date=update.effective_message.date,
                            interaction_id=update.effective_message.message_id
                            ).save()

        for item in self.actions:
            if "InlineKeyboard" in item:
                keyboard = [[]]
                for button in item["InlineKeyboard"]:
                    if "data" in button:
                        callback_data = button["data"]
                    else:
                        callback_data = None

                    if "url" in button:
                        callback_url = button["url"]
                    else:
                        callback_url = None

                    keyboard[0].append(InlineKeyboardButton(
                        button["text"], callback_data=callback_data, url=callback_url))

                reply_markup = InlineKeyboardMarkup(keyboard)

            elif "ReplyKeyboardMarkup" in item:
                keyboard = [[]]
                for button in item["ReplyKeyboardMarkup"]:
                    if "request_location" in button:
                        request_location = button["request_location"]
                    else:
                        request_location = False

                    keyboard[0].append(KeyboardButton(
                        text=button["text"], request_location=request_location))

                reply_markup = ReplyKeyboardMarkup(
                    keyboard, one_time_keyboard=True)
            else:
                reply_markup = ReplyKeyboardRemove()

            if item["type"] == "message":
                parse_mode = None
                if "parse_mode" in item:
                    parse_mode = item["parse_mode"]
                disable_web_page_preview = None
                if "disable_web_page_preview" in item:
                    disable_web_page_preview = item["disable_web_page_preview"]

                text = item["text"]
                
                logger.debug("type: {}".format(type(update)))
                logger.debug("update: {}".format(str(update)))
                logger.debug("context: {}".format(str(context.user_data)))
                if type(update) == CallbackQuery:
                    update.from_user.send_message(text.format(
                        **context.user_data), reply_markup=reply_markup, parse_mode=parse_mode, disable_web_page_preview=disable_web_page_preview)
                elif update.callback_query:
                    update.callback_query.from_user.send_message(text.format(
                        **context.user_data), reply_markup=reply_markup, parse_mode=parse_mode, disable_web_page_preview=disable_web_page_preview)
                elif update.poll_answer:
                    update.poll_answer.user.send_message(text.format(
                        **context.user_data), reply_markup=reply_markup, parse_mode=parse_mode, disable_web_page_preview=disable_web_page_preview)
                else:
                    update.message.reply_text(text.format(
                        **context.user_data), reply_markup=reply_markup, parse_mode=parse_mode, disable_web_page_preview=disable_web_page_preview)
            elif item["type"] == "photo":
                if "caption" in item.keys():
                    caption = item["caption"]
                else:
                    caption = None

                if "file" in item.keys():
                    photo = open(item["file"], 'rb')
                else:
                    photo = item["url"]

                if type(update) != CallbackQuery and update.poll_answer:
                    update.poll_answer.user.send_photo(
                        photo, caption=caption, reply_markup=reply_markup)
                else:
                    update.message.reply_photo(
                        photo, caption=caption, reply_markup=reply_markup)

            elif item["type"] == "document":
                if "caption" in item.keys():
                    caption = item["caption"]
                else:
                    caption = None

                if "file" in item.keys():
                    document = open(item["file"], 'rb')
                else:
                    document = item["url"]

                if type(update) != CallbackQuery and update.poll_answer:
                    update.poll_answer.user.send_document(
                        document, caption=caption, reply_markup=reply_markup)
                else:
                    update.message.reply_document(
                        document, caption=caption, reply_markup=reply_markup)

            elif item["type"] == "audio":
                if "file" in item.keys():
                    audio = open(item["file"], 'rb')
                else:
                    audio = item["url"]

                update.message.reply_audio(audio, title=item["title"], performer=item["performer"], reply_markup=reply_markup)

            elif item["type"] == "voice":
                if "caption" in item.keys():
                    caption = item["caption"]
                else:
                    caption = None

                if "file" in item.keys():
                    voice = open(item["file"], 'rb')
                else:
                    voice = item["url"]

                update.message.reply_voice(voice, caption=caption, reply_markup=reply_markup)


            elif item["type"] == "contact":
                update.message.reply_contact(phone_number=item["phone_number"],
                                             first_name=item["first_name"],
                                             last_name=item["last_name"],
                                             reply_markup=reply_markup)
            elif item["type"] == "poll":
                if "poll_type" in item.keys():
                    poll_type = item["poll_type"]
                else:
                    poll_type = "quiz"
                if "correct_option_id" in item.keys():
                    correct_option_id = item["correct_option_id"]
                else:
                    correct_option_id = None
                update.message.reply_poll(question=item["question"],
                                          options=item["options"],
                                          type=poll_type,
                                          correct_option_id=correct_option_id,
                                          is_anonymous=False
                                          )

            elif item["type"] == "media_group":
                if "files" in item.keys():
                    photoGroup = [InputMediaPhoto(media=open(
                        photo, 'rb')) for photo in item["files"]]
                else:
                    photoGroup = [InputMediaPhoto(media=open(
                        photo, 'rb')) for photo in item["urls"]]
                update.message.reply_media_group(media=photoGroup)
            elif item["type"] == "sticker":
                if type(update) != CallbackQuery and update.poll_answer:
                    update.poll_answer.user.send_sticker(item["id"])
                else:
                    update.message.reply_sticker(item["id"])
            elif item["type"] == "video":
                if "caption" in item.keys():
                    caption = item["caption"]
                else:
                    caption=None
                if "file" in item.keys():
                    video = open(item["file"], 'rb')
                else:
                    video = item["url"]
                update.message.reply_video(video,caption=caption)

            ## type: venue
            # latitude: 52.4090401
            # longitude: 12.9724552
            # address: Bahnhof Golm
            # title: Start der Rallye

            elif item["type"] == "venue":
                if type(update) != CallbackQuery and update.poll_answer:
                    update.poll_answer.user.send_venue(
                        latitude=item["latitude"], longitude=item["longitude"], address=item["address"], title=item["title"])
                else:
                    update.message.reply_venue(
                        latitude=item["latitude"], longitude=item["longitude"], address=item["address"], title=item["title"])

            elif item["type"] == "return":
                if item["state"] == "END":
                    return ConversationHandler.END
                return item["state"]
            elif item["type"] == "callback":
                query = update.callback_query

                query.answer()
                query.edit_message_reply_markup(InlineKeyboardMarkup([]))
                for case in item["conditions"]:
                    if query.data == case["condition"]:
                        return Action(case["action"])(query, context)
            elif item["type"] == "function":
                arguments = {i: item[i]
                             for i in item if i != 'type' and i != 'func'}
                result_value = self.action_functions[item["func"]](
                    update, context, **arguments)
                if result_value:
                    return result_value
