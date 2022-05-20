import json
import logging
import os
import re
from configparser import ConfigParser
from typing import List

import requests as req
import yaml
from digitalguide.pattern import (EMOJI_PATTERN, JA_PATTERN, JAHRESZAHL_PATTERN, KOMMAZAHL_PATTERN, NEIN_PATTERN,
                                  WEITER_PATTERN, WOHIN_PATTERN, ZURUECK_PATTERN)
from digitalguide.whatsapp.WhatsAppUpdate import WhatsAppUpdate
from requests.exceptions import Timeout


def read_state_yml(filename, actions={}, prechecks: List = []):
    with open(filename) as file:
        yaml_dict = yaml.load(file, Loader=yaml.FullLoader)

    return read_state(yaml_dict, actions=actions, prechecks=prechecks)

def read_state(yaml_dict, actions={}, prechecks: List = []):
    states_dict = {}

    for state, handlers in yaml_dict.items():
        handler_list = prechecks[:]
        for handler in handlers:
            if handler["handler"] == "PollAnswerHandler":
                newHandler = MessageHandler(RegexFilter(
                    "^(.)+"), actions[handler["action"]])
            elif handler["handler"] == "MessageHandler":
                if handler["filter"] == "regex":
                    if handler["regex"] == "EMOJI_PATTERN":
                        newHandler = MessageHandler(RegexFilter(
                            re.compile(EMOJI_PATTERN,re.IGNORECASE)), actions[handler["action"]])
                    elif handler["regex"] == "WEITER_PATTERN":
                        newHandler = MessageHandler(RegexFilter(
                            re.compile(WEITER_PATTERN,re.IGNORECASE)), actions[handler["action"]])
                    elif handler["regex"] == "WOHIN_PATTERN":
                        newHandler = MessageHandler(RegexFilter(
                            re.compile(WOHIN_PATTERN,re.IGNORECASE)), actions[handler["action"]])
                    elif handler["regex"] == "JA_PATTERN":
                        newHandler = MessageHandler(RegexFilter(
                            re.compile(JA_PATTERN,re.IGNORECASE)), actions[handler["action"]])
                    elif handler["regex"] == "NEIN_PATTERN":
                        newHandler = MessageHandler(RegexFilter(
                            re.compile(NEIN_PATTERN,re.IGNORECASE)), actions[handler["action"]])
                    elif handler["regex"] == "ZURUECK_PATTERN":
                        newHandler = MessageHandler(RegexFilter(
                            re.compile(ZURUECK_PATTERN,re.IGNORECASE)), actions[handler["action"]])
                    elif handler["regex"] == "JAHRESZAHL_PATTERN":
                        newHandler = MessageHandler(RegexFilter(
                            re.compile(JAHRESZAHL_PATTERN,re.IGNORECASE)), actions[handler["action"]])
                    elif handler["regex"] == "KOMMAZAHL_PATTERN":
                        newHandler = MessageHandler(RegexFilter(
                            re.compile(KOMMAZAHL_PATTERN,re.IGNORECASE)), actions[handler["action"]])
                    else:
                        newHandler = MessageHandler(RegexFilter(
                            re.compile(handler["regex"],re.IGNORECASE)), actions[handler["action"]])
                elif handler["filter"] == "text":
                    newHandler = MessageHandler(
                        TextFilter(), actions[handler["action"]])
                elif handler["filter"] == "photo":
                    newHandler = MessageHandler(
                        PhotoFilter(), actions[handler["action"]])
                elif handler["filter"] == "voice":
                    newHandler = MessageHandler(
                        VoiceFilter(), actions[handler["action"]])
                elif handler["filter"] == "rasa":
                    newHandler = MessageHandler(FilterRasa(
                        handler["intent"]), actions[handler["action"]])
                else:
                    raise NotImplementedError(
                        "This Filter is not implemented: {}".format(handler["filter"]))
            elif handler["handler"] == "CommandHandler":
                newHandler = CommandHandler(
                    handler["command"], actions[handler["action"]])
            elif handler["handler"] == "TypeHandler":
                if handler["type"] == "Update":
                    type_ = WhatsAppUpdate
                else:
                    raise NotImplementedError(
                    "This Updatetype is not implemented: {}".format(handler["type"]))
                newHandler = TypeHandler(type_, actions[handler["action"]])
            else:
                raise NotImplementedError(
                    "This Handler is not implemented: {}".format(handler["handler"]))

            handler_list.append(newHandler)

        states_dict[state] = handler_list

    return states_dict


class MessageHandler:
    def __init__(self, filters, callback):
        self.filters = filters
        self.callback = callback

    def check_update(self, update: WhatsAppUpdate):
        return self.filters(update)


class CommandHandler:
    def __init__(self, command, callback):
        self.command = command
        self.callback = callback

    def check_update(self, update: WhatsAppUpdate):
        if update.Body.strip("/").lower() == self.command.lower():
            return True


class TypeHandler:
    def __init__(self, type_, callback):
        self.type_ = type_
        self.callback = callback

    def check_update(self, update: WhatsAppUpdate):
        return type(update) is self.type_


class RegexFilter:
    def __init__(self, regex) -> None:
        self.regex = regex

    def __call__(self, update: WhatsAppUpdate) -> bool:
        return re.search(self.regex, update.Body)


class TextFilter:
    def __call__(self, update: WhatsAppUpdate) -> bool:
        return update.Body != ""


class PhotoFilter:
    def __call__(self, update: WhatsAppUpdate) -> bool:
        return update.MediaContentType0 and update.MediaContentType0.startswith("image")


class VoiceFilter:
    def __call__(self, update: WhatsAppUpdate) -> bool:
        return update.MediaContentType0 and update.MediaContentType0.startswith("audio")


config = ConfigParser()
config.read('config.ini')

logger = logging.getLogger(__name__)


class FilterRasa:
    def __init__(self, intent, confidence=0.8):
        self.intent = intent
        self.confidence = confidence

    def __call__(self, update: WhatsAppUpdate):
        try:
            payload = json.dumps({
                "username": os.getenv('RASA_USER'),
                "password": os.getenv('RASA_PASSWORD')
            })

            token_response = req.post(
                config["rasa"]["url"] + "/api/auth", data=payload, timeout=1)
            logger.debug(token_response.json())

            RASA_TOKEN = token_response.json()["access_token"]
            response = req.post(config["rasa"]["url"] + "/api/projects/default/logs", params={
                                "q": update.Body}, headers={'Authorization': 'Bearer {}'.format(RASA_TOKEN)},  timeout=(3, 8))
            logger.debug(response.json())
        except Exception as e:
            logger.debug(e)
            return False
        else:
            if not response.ok:
                return False
            return response.json()["user_input"]["intent"]["name"] == self.intent and response.json()["user_input"]["intent"]["confidence"] >= self.confidence
