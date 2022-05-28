import re


def readTriggers(format_inhalt_list, action):
    triggers = []
    for format, inhalt in format_inhalt_list:
        if format == "Liste":
            trigger_dict = {}
            trigger_dict["handler"] = "CommandHandler"
            trigger_dict["command"] = inhalt
            trigger_dict["action"] = action
            triggers.append(trigger_dict)
            trigger_dict = {}
            trigger_dict["handler"] = "MessageHandler"
            trigger_dict["filter"] = "regex"
            trigger_dict["action"] = action
            if inhalt == "Weiter":
                trigger_dict["regex"] = "WEITER_PATTERN"
            elif inhalt == "Ja":
                trigger_dict["regex"] = "JA_PATTERN"
            elif inhalt == "Wohin":
                trigger_dict["regex"] = "WOHIN_PATTERN"
            elif inhalt == "Nein":
                trigger_dict["regex"] = "NEIN_PATTERN"
            elif inhalt == "Zurueck":
                trigger_dict["regex"] = "ZURUECK_PATTERN"
            else:
                trigger_dict["regex"] = inhalt
                print("List {} ist nicht bekannt!".format(inhalt))
            triggers.append(trigger_dict)
        if format == "Rasa":
            trigger_dict = {}
            trigger_dict["handler"] = "MessageHandler"
            trigger_dict["filter"] = "rasa"
            trigger_dict["intent"] = inhalt
            trigger_dict["action"] = action
            triggers.append(trigger_dict)
        if format == "Freitext":
            trigger_dict = {}
            trigger_dict["handler"] = "MessageHandler"
            trigger_dict["filter"] = "text"
            trigger_dict["action"] = action
            triggers.append(trigger_dict)
        if format == "Foto":
            trigger_dict = {}
            trigger_dict["handler"] = "MessageHandler"
            trigger_dict["filter"] = "photo"
            trigger_dict["action"] = action
            triggers.append(trigger_dict)
        if format == "Regex":
            trigger_dict = {}
            trigger_dict["handler"] = "MessageHandler"
            trigger_dict["filter"] = "regex"
            trigger_dict["regex"] = inhalt
            trigger_dict["action"] = action
            triggers.append(trigger_dict)
    return triggers