import re
import yaml
from telegram import Update
from telegram.ext import (CommandHandler, Filters, MessageHandler,
                          PollAnswerHandler, TypeHandler)

from digitalguide import rasa_filter, uhrzeit_filter
from digitalguide.pattern import (EMOJI_PATTERN, JA_PATTERN, JAHRESZAHL_PATTERN, KOMMAZAHL_PATTERN, NEIN_PATTERN,
                                  WEITER_PATTERN, WOHIN_PATTERN, ZURUECK_PATTERN)

def read_state_yml(filename, actions: dict = None, prechecks: list = None):
    with open(filename) as file:
        yaml_dict = yaml.load(file, Loader=yaml.FullLoader)

    return read_state(yaml_dict, actions=actions, prechecks=prechecks)

def read_state(yaml_dict, actions: dict = None, prechecks: list = None):
    if actions is None:
        actions = {}
    if prechecks is None:
        prechecks = []

    states_dict = {}

    for state, handlers in yaml_dict.items():
        handler_list = prechecks[:]
        for handler in handlers:
            if handler["handler"] == "MessageHandler":
                if handler["filter"] == "regex":
                    if handler["regex"] == "EMOJI_PATTERN":
                        newHandler = MessageHandler(Filters.regex(
                            re.compile(EMOJI_PATTERN,re.IGNORECASE)), actions[handler["action"]])
                    elif handler["regex"] == "WEITER_PATTERN":
                        newHandler = MessageHandler(Filters.regex(
                            re.compile(WEITER_PATTERN,re.IGNORECASE)), actions[handler["action"]])
                    elif handler["regex"] == "WOHIN_PATTERN":
                        newHandler = MessageHandler(Filters.regex(
                            re.compile(WOHIN_PATTERN,re.IGNORECASE)), actions[handler["action"]])
                    elif handler["regex"] == "JA_PATTERN":
                        newHandler = MessageHandler(Filters.regex(
                            re.compile(JA_PATTERN,re.IGNORECASE)), actions[handler["action"]])
                    elif handler["regex"] == "NEIN_PATTERN":
                        newHandler = MessageHandler(Filters.regex(
                            re.compile(NEIN_PATTERN,re.IGNORECASE)), actions[handler["action"]])
                    elif handler["regex"] == "ZURUECK_PATTERN":
                        newHandler = MessageHandler(Filters.regex(
                            re.compile(ZURUECK_PATTERN,re.IGNORECASE)), actions[handler["action"]])
                    elif handler["regex"] == "JAHRESZAHL_PATTERN":
                        newHandler = MessageHandler(Filters.regex(
                            re.compile(JAHRESZAHL_PATTERN,re.IGNORECASE)), actions[handler["action"]])
                    elif handler["regex"] == "KOMMAZAHL_PATTERN":
                        newHandler = MessageHandler(Filters.regex(
                            re.compile(KOMMAZAHL_PATTERN,re.IGNORECASE)), actions[handler["action"]])
                    else:
                        newHandler = MessageHandler(Filters.regex(
                            re.compile(handler["regex"],re.IGNORECASE)), actions[handler["action"]])
                elif handler["filter"] == "text":
                    newHandler = MessageHandler(
                        Filters.text, actions[handler["action"]])
                elif handler["filter"] == "photo":
                    newHandler = MessageHandler(
                        Filters.photo, actions[handler["action"]])
                elif handler["filter"] == "sticker":
                    newHandler = MessageHandler(
                        Filters.sticker, actions[handler["action"]])
                elif handler["filter"] == "voice":
                    newHandler = MessageHandler(
                        Filters.voice, actions[handler["action"]])
                elif handler["filter"] == "rasa":
                    newHandler = MessageHandler(
                        rasa_filter.FilterRasa(handler["intent"]), actions[handler["action"]])
                elif handler["filter"] == "uhrzeit":
                    newHandler = MessageHandler(
                        uhrzeit_filter.FilterUhrzeit(), actions[handler["action"]])
                else:
                    raise NotImplementedError(
                        "This filter is not implemented: {}".format(handler["filter"]))
            elif handler["handler"] == "CommandHandler":
                newHandler = CommandHandler(
                    handler["command"], actions[handler["action"]])
            elif handler["handler"] == "PollAnswerHandler":
                newHandler = PollAnswerHandler(actions[handler["action"]])
            elif handler["handler"] == "TypeHandler":
                if handler["type"] == "Update":
                    type_ = Update
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
