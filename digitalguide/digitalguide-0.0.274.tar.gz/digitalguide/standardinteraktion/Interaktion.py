
from collections import defaultdict
from digitalguide.standardinteraktion.Action import readActions
from digitalguide.standardinteraktion.Trigger import readTriggers

from digitalguide.standardinteraktion.wegInteraktion import Weg


class Interaktion:
    def __init__(self, name, typ, states, actions, uebertrag_actions, next_interaktion, action_requirements):
        self.name = name
        self.typ = typ
        self.states = states
        self.actions = actions
        self.uebertrag_actions = uebertrag_actions
        self.next_interaktion = next_interaktion

        self.action_requirements = action_requirements

    @classmethod
    def from_excel_dict(cls, excel_dict_item, messanger="Telegram", asset_url=""):
        actions = defaultdict(list)
        states = defaultdict(list)
        action_requirements = []

        poi_interaction, interaktion_dict = excel_dict_item
        poi_name, interaction_typ = poi_interaction

        print(poi_name)

        if "Next" in interaktion_dict.keys():
            weiter_dict = dict((x, y) for x, y in interaktion_dict["Next"])
            next_interaktion = "{}_{}".format(
                weiter_dict["POI"], weiter_dict["Aktion"])
            action_requirements.append(next_interaktion)

        else:
            next_interaktion = None

        if interaction_typ == "Aktion":
            actions["{}".format(poi_name)] = readActions(
                interaktion_dict["Aktion"], messanger=messanger, asset_url=asset_url)

        elif interaction_typ == "Verzweigung":
            actions["{}_weg".format(poi_name)] = readActions(interaktion_dict["Weg"]
                                                             + [("Return", "{}_WEG".format(poi_name.upper()))], messanger=messanger, asset_url=asset_url)
            actions["{}_tipp".format(poi_name)] = readActions(
                interaktion_dict["Tipp"], messanger=messanger, asset_url=asset_url)

            for aktion, aktion_list in interaktion_dict.items():
                if aktion.startswith("trigger_"):
                    weiter_dict = dict(
                        (x, y) for x, y in interaktion_dict[aktion.replace("trigger_", "Next_")])
                    option_next_interaktion = "{}_{}".format(
                        weiter_dict["POI"], weiter_dict["Aktion"])
                    action_requirements.append(option_next_interaktion)

                    states["{}_WEG".format(poi_name.upper())] += readTriggers(
                        aktion_list, option_next_interaktion)

            states["{}_WEG".format(poi_name.upper())] += [{"handler": "TypeHandler", "type": "Update",
                    "action": "{}_tipp".format(poi_name)}]

        elif interaction_typ == "Datenabfrage":
            actions["{}_frage".format(poi_name)] = readActions(interaktion_dict["Frage"]
                                                               + [("Return", "{}_FRAGE".format(poi_name.upper()))], messanger=messanger, asset_url=asset_url)
            actions["{}_tipp".format(poi_name)] = readActions(
                interaktion_dict["Tipp"], messanger=messanger, asset_url=asset_url)

            states["{}_FRAGE".format(poi_name.upper())] = readTriggers(interaktion_dict["Typ"], next_interaktion) \
                + [{"handler": "TypeHandler", "type": "Update",
                    "action": "{}_tipp".format(poi_name)}]

        elif interaction_typ == "Weg":
            return Weg(poi_name, interaktion_dict, messanger=messanger, asset_url=asset_url)

        elif interaction_typ == "Quizfrage":
            actions["{}_frage".format(poi_name)] = readActions(
                interaktion_dict["Frage"] + [("Return", "{}_FRAGE".format(poi_name.upper()))], messanger=messanger, asset_url=asset_url)

            actions["{}_tipp".format(poi_name)] = readActions(
                interaktion_dict["Tipp"], messanger=messanger, asset_url=asset_url)

            actions["{}_aufloesung".format(poi_name)] = readActions(
                interaktion_dict["Aufloesung"], messanger=messanger, asset_url=asset_url)\
                + readActions([("Return", "{}_AUFLOESUNG".format(poi_name.upper()))], messanger=messanger, asset_url=asset_url)

            for aktion, aktion_list in interaktion_dict.items():
                if aktion.startswith("antwort_"):
                    actions["{}_{}".format(poi_name, aktion)] = readActions(aktion_list, messanger=messanger, asset_url=asset_url) \
                        + readActions(interaktion_dict["Aufloesung"], messanger=messanger, asset_url=asset_url) \
                        + readActions([("Return", "{}_AUFLOESUNG".format(poi_name.upper()))], messanger=messanger, asset_url=asset_url)

                elif aktion.startswith("trigger_"):
                    if aktion != "trigger_weiter":
                        states["{}_FRAGE".format(poi_name.upper())] += readTriggers(
                            aktion_list, "{}_{}".format(poi_name, aktion.replace("trigger_", "antwort_")))

            states["{}_FRAGE".format(poi_name.upper())] += readTriggers([("Liste", "Weiter")], "{}_aufloesung".format(poi_name)) \
                + [{"handler": "TypeHandler", "type": "Update",
                    "action": "{}_tipp".format(poi_name)}]

            # Trigger weiter
            if "trigger_weiter" in interaktion_dict.keys():
                trigger_weiter = interaktion_dict["trigger_weiter"]
            else:
                trigger_weiter = [("Liste", "Weiter")]
                print(
                    "Info: {} hat keinen Trigger weiter - der Standardwert wird benutzt.".format(poi_name))

            states["{}_AUFLOESUNG".format(poi_name.upper())] = readTriggers(trigger_weiter, next_interaktion) \
                + readTriggers([("Liste", "Zurueck")], "{}_frage".format(poi_name)) \
                + [{"handler": "TypeHandler", "type": "Update", "action": "weiter_tipp"}]

        elif interaction_typ == "Schätzfrage":
            actions["{}_frage".format(poi_name)] = readActions(
                interaktion_dict["Frage"] + [("Return", "{}_FRAGE".format(poi_name.upper()))], messanger=messanger, asset_url=asset_url)

            actions["{}_aufloesung".format(poi_name)] = readActions(interaktion_dict["Aufloesung"], messanger=messanger, asset_url=asset_url) \
                + readActions([("Return", "{}_AUFLOESUNG".format(poi_name.upper()))], messanger=messanger)

            actions["{}_tipp".format(poi_name)] = readActions(
                interaktion_dict["Tipp"], messanger=messanger, asset_url=asset_url)

            if interaktion_dict["Typ"][0][0] == "Jahreszahl":
                states["{}_FRAGE".format(poi_name.upper())] = (readTriggers([("Regex", "JAHRESZAHL_PATTERN")], "{}_aufloesung".format(poi_name))) \
                    + [{"handler": "TypeHandler", "type": "Update",
                        "action": "{}_tipp".format(poi_name)}]

            elif interaktion_dict["Typ"][0][0] == "Prozentzahl":
                states["{}_FRAGE".format(poi_name.upper())] = (readTriggers([("Regex", "KOMMAZAHL_PATTERN")], "{}_aufloesung".format(poi_name))) \
                    + readTriggers([("Liste", "Weiter")], "{}_aufloesung".format(poi_name)) \
                    + [{"handler": "TypeHandler", "type": "Update",
                        "action": "{}_tipp".format(poi_name)}]

            elif interaktion_dict["Typ"][0][0] == "Kommazahl":
                states["{}_FRAGE".format(poi_name.upper())] = (readTriggers([("Regex", "KOMMAZAHL_PATTERN")], "{}_aufloesung".format(poi_name))) \
                    + readTriggers([("Liste", "Weiter")], "{}_aufloesung".format(poi_name)) \
                    + [{"handler": "TypeHandler", "type": "Update",
                        "action": "{}_tipp".format(poi_name)}]

            elif interaktion_dict["Typ"][0][0] == "Länge":
                states["{}_FRAGE".format(poi_name.upper())] = (readTriggers([("Regex", "KOMMAZAHL_PATTERN")], "{}_aufloesung".format(poi_name))) \
                    + readTriggers([("Liste", "Weiter")], "{}_aufloesung".format(poi_name)) \
                    + [{"handler": "TypeHandler", "type": "Update",
                        "action": "{}_tipp".format(poi_name)}]

            elif interaktion_dict["Typ"][0][0] == "Römische Jahreszahl":
                states["{}_FRAGE".format(poi_name.upper())] = (readTriggers([("Regex", "^M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$")], "{}_aufloesung".format(poi_name))) \
                    + readTriggers([("Liste", "Weiter")], "{}_aufloesung".format(poi_name)) \
                    + [{"handler": "TypeHandler", "type": "Update",
                        "action": "{}_tipp".format(poi_name)}]

            else:
                print("Der Schätzfragentyp {} ist nicht bekannt!".format(
                    interaktion_dict["Typ"][0][0]))

            # Trigger weiter
            if "trigger_weiter" in interaktion_dict.keys():
                trigger_weiter = interaktion_dict["trigger_weiter"]
            else:
                trigger_weiter = [("Liste", "Weiter")]
                print(
                    "Info: {} hat keinen Trigger weiter - der Standardwert wird benutzt.".format(poi_name))

            states["{}_AUFLOESUNG".format(poi_name.upper())] = readTriggers(trigger_weiter, next_interaktion) \
                + [{"handler": "TypeHandler", "type": "Update", "action": "weiter_tipp"}]

        elif interaction_typ == "Listenfrage":
            actions["{}_frage".format(poi_name)] = readActions(
                interaktion_dict["Frage"] + [("Return", "{}_FRAGE".format(poi_name.upper()))], messanger=messanger, asset_url=asset_url)

            answer_id_name_list = []
            answer_id_list = []
            for aktion, aktion_list in interaktion_dict.items():
                if aktion.startswith("name_"):
                    answer_id_name_list.append(
                        [aktion.replace("name_", ""), aktion_list[0][1]])
                    answer_id_list.append(
                        aktion.replace("name_", ""))

            for aktion, aktion_list in interaktion_dict.items():
                if aktion.startswith("antwort_"):
                    actions["{}_{}".format(poi_name, aktion)] = [{"type": "function",
                                                                  "func": "loop_list",
                                                                  "key": poi_name,
                                                                  "value": aktion.replace("antwort_", ""),
                                                                  "doppelte_antwort": interaktion_dict["doppelte Antwort"][0][1]}]\
                        + readActions(aktion_list, messanger=messanger, asset_url=asset_url) \
                        + readActions(interaktion_dict["richtig Antwort"], messanger=messanger, asset_url=asset_url) \
                        + [{"type": "function",
                            "func": "loop_list_fertig",
                            "key": poi_name,
                            "answer_id_list": answer_id_list,
                            "fertig_antwort": interaktion_dict["fertig Antwort"][0][1]}]
                    
                    actions["{}_{}_re".format(poi_name, aktion)] = readActions(aktion_list, messanger=messanger, asset_url=asset_url) \
                                                                        + readActions(interaktion_dict["richtig Antwort"], messanger=messanger, asset_url=asset_url)

                elif aktion.startswith("trigger_"):
                    if aktion != "trigger_weiter":
                        states["{}_FRAGE".format(poi_name.upper())] += readTriggers(
                            aktion_list, "{}_{}".format(poi_name, aktion.replace("trigger_", "antwort_")))

                        states["{}_AUFLOESUNG".format(poi_name.upper())] += readTriggers(
                            aktion_list, "{}_{}_re".format(poi_name, aktion.replace("trigger_", "antwort_")))

            actions["{}_aufloesung".format(poi_name)] = [{"type": "function", "func": "eval_list", "answer_id_name_list": answer_id_name_list, "poi": poi_name, "response_text": interaktion_dict["response_text"][0][1]}]\
                + readActions(interaktion_dict["Aufloesung"], messanger=messanger, asset_url=asset_url) \
                + readActions([("Return", "{}_AUFLOESUNG".format(poi_name.upper()))], messanger=messanger, asset_url=asset_url)

            actions["{}_falsche_antwort".format(poi_name)] = readActions(
                interaktion_dict["falsch Antwort"], messanger=messanger, asset_url=asset_url)

            states["{}_FRAGE".format(poi_name.upper())] += readTriggers([("Liste", "Weiter")], "{}_aufloesung".format(poi_name))\
                + [{"handler": "TypeHandler", "type": "Update",
                    "action": "{}_falsche_antwort".format(poi_name)}]

            # Trigger weiter
            if "trigger_weiter" in interaktion_dict.keys():
                trigger_weiter = interaktion_dict["trigger_weiter"]
            else:
                trigger_weiter = [("Liste", "Weiter")]
                print(
                    "Info: {} hat keinen Trigger weiter - der Standardwert wird benutzt.".format(poi_name))

            states["{}_AUFLOESUNG".format(poi_name.upper())] += readTriggers(trigger_weiter, next_interaktion) \
                + [{"handler": "TypeHandler", "type": "Update", "action": "weiter_tipp"}]

        elif interaction_typ == "Beteiligungsfrage":
            actions["{}_frage".format(poi_name)] = readActions(
                interaktion_dict["Frage"] + [("Return", "{}_FRAGE".format(poi_name.upper()))], messanger=messanger, asset_url=asset_url)
            actions["{}_tipp".format(poi_name)] = readActions(
                interaktion_dict["Tipp"], messanger=messanger, asset_url=asset_url)

            actions["{}_aufloesung".format(poi_name)] = readActions(
                interaktion_dict["Aufloesung"] + [("Return", "{}_AUFLOESUNG".format(poi_name.upper()))], messanger=messanger, asset_url=asset_url)

            states["{}_FRAGE".format(poi_name.upper())] = readTriggers([("Liste", "Weiter")], next_interaktion) \
                + readTriggers([("Liste", "Nein")], next_interaktion) \
                + readTriggers(interaktion_dict["Typ"], "{}_aufloesung".format(poi_name)) \
                + [{"handler": "TypeHandler", "type": "Update",
                    "action": "{}_tipp".format(poi_name)}]

            # Trigger weiter
            if "trigger_weiter" in interaktion_dict.keys():
                trigger_weiter = interaktion_dict["trigger_weiter"]
            else:
                trigger_weiter = [("Liste", "Weiter")]
                print(
                    "Info: {} hat keinen Trigger weiter - der Standardwert wird benutzt.".format(poi_name))

            states["{}_AUFLOESUNG".format(poi_name.upper())] = readTriggers(trigger_weiter, next_interaktion) \
                + [{"handler": "TypeHandler", "type": "Update", "action": "weiter_tipp"}]

        elif interaction_typ == "GIF Generator":
            actions["{}_frage".format(poi_name)] = readActions(
                interaktion_dict["Frage"] + [("Return", "{}_FRAGE".format(poi_name.upper()))], messanger=messanger, asset_url=asset_url)

            actions["{}_tipp".format(poi_name)] = readActions(
                interaktion_dict["Tipp"], messanger=messanger, asset_url=asset_url)

            actions["{}_aufloesung".format(poi_name)] = readActions(
                interaktion_dict["Aufloesung"], messanger=messanger, asset_url=asset_url)

            # Trigger weiter
            if "trigger_weiter" in interaktion_dict.keys():
                trigger_weiter = interaktion_dict["trigger_weiter"]
            else:
                trigger_weiter = [("Liste", "Weiter"), ("Liste", "Nein")]
                print(
                    "Info: {} hat keinen Trigger weiter - der Standardwert wird benutzt.".format(poi_name))

            states["{}_FRAGE".format(poi_name.upper())] = readTriggers([("Foto", "")], "{}_aufloesung".format(poi_name)) \
                + readTriggers(trigger_weiter, next_interaktion) \
                + [{"handler": "TypeHandler", "type": "Update",
                    "action": "{}_tipp".format(poi_name)}]

        elif interaction_typ == "Infostrecke":
            actions["{}_info".format(poi_name)] = readActions(
                interaktion_dict["Info"] + [("Return", "{}_INFO".format(poi_name.upper()))], messanger=messanger, asset_url=asset_url)

            # Trigger weiter
            if "trigger_weiter" in interaktion_dict.keys():
                trigger_weiter = interaktion_dict["trigger_weiter"]
            else:
                trigger_weiter = [("Liste", "Weiter")]
                print(
                    "Info: {} hat keinen Trigger weiter - der Standardwert wird benutzt.".format(poi_name))

            states["{}_INFO".format(poi_name.upper())] = readTriggers(trigger_weiter, next_interaktion) \
                + [{"handler": "TypeHandler", "type": "Update", "action": "weiter_tipp"}]

        elif interaction_typ == "Assoziationskette":
            actions["{}_frage".format(poi_name)] = readActions(
                interaktion_dict["Frage"] + [("Return", "{}_FRAGE".format(poi_name.upper()))], messanger=messanger, asset_url=asset_url)
            actions["{}_loop".format(poi_name)] = readActions(
                interaktion_dict["Loop"], messanger=messanger, asset_url=asset_url)
            states["{}_FRAGE".format(poi_name.upper())] = readTriggers([("Liste", "Weiter")], "{}_aufloesung".format(poi_name)) \
                + readTriggers([("Freitext", "")], "{}_loop".format(poi_name)) \
                + [{"handler": "TypeHandler", "type": "Update",
                    "action": "{}_tipp".format(poi_name)}]
            actions["{}_tipp".format(poi_name)] = readActions(
                interaktion_dict["Tipp"], messanger=messanger, asset_url=asset_url)
            actions["{}_aufloesung".format(poi_name)] = readActions(
                interaktion_dict["Aufloesung"] + [("Return", "{}_AUFLOESUNG".format(poi_name.upper()))], messanger=messanger, asset_url=asset_url)

            # Trigger weiter
            if "trigger_weiter" in interaktion_dict.keys():
                trigger_weiter = interaktion_dict["trigger_weiter"]
            else:
                trigger_weiter = [("Liste", "Weiter")]
                print(
                    "Info: {} hat keinen Trigger weiter - der Standardwert wird benutzt.".format(poi_name))

            states["{}_AUFLOESUNG".format(poi_name.upper())] = readTriggers(trigger_weiter, next_interaktion) \
                + [{"handler": "TypeHandler", "type": "Update", "action": "weiter_tipp"}]

        else:
            print("Der Interaktionstyp {} ist nicht bekannt!".format(interaction_typ))

        return cls(poi_name, interaction_typ, states, actions, [], next_interaktion, action_requirements)
