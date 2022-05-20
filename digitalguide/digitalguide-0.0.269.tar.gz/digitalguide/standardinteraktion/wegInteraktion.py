from collections import defaultdict
from digitalguide.standardinteraktion.Action import readActions
from digitalguide.standardinteraktion.Trigger import readTriggers


class Weg:
    def __init__(self, poi_name, interaktion_dict, messanger, asset_url):
        self.typ = "Weg"
        self.name = poi_name
        self.interaktion_dict = interaktion_dict
        self.action_requirements = []
        self.messanger = messanger

        if "Next" in interaktion_dict.keys():
            weiter_dict = dict((x, y) for x, y in interaktion_dict["Next"])
            self.next_interaktion = "{}_{}".format(
                weiter_dict["POI"], weiter_dict["Aktion"])
            self.action_requirements.append(self.next_interaktion)

        else:
            self.next_interaktion = None

        self.actions = defaultdict(list)
        self.generate_actions(asset_url)

        self.states = defaultdict(list)
        self.generate_states()
        
        self.uebertrag_actions = []


    def generate_states(self):
        states = defaultdict(list)
        # Trigger navigation
        if "trigger_navigation" in self.interaktion_dict.keys():
            trigger_navigation = self.interaktion_dict["trigger_navigation"]
        else:
            trigger_navigation = [("Liste", "Wohin")]
            print(
                "Info: {} hat keinen Trigger navigation - der Standardwert wird benutzt.".format(self.name))

        # Trigger weiter
        if "trigger_weiter" in self.interaktion_dict.keys():
            trigger_weiter = self.interaktion_dict["trigger_weiter"]
        else:
            trigger_weiter = [("Liste", "Weiter")]
            print(
                "Info: {} hat keinen Trigger weiter - der Standardwert wird benutzt.".format(self.name))

        self.states["{}_WEG".format(self.name.upper())] = readTriggers(trigger_navigation, "{}_navigation".format(self.name)) \
            + readTriggers(trigger_weiter, self.next_interaktion) \
            + [{"handler": "TypeHandler", "type": "Update",
                "action": self.tipp_action}]

    def generate_actions(self, asset_url):
        # Weg
        if "Weg" in self.interaktion_dict.keys():
            self.actions["{}_weg".format(self.name)] = readActions(self.interaktion_dict["Weg"]
                                                                + [("Return", "{}_WEG".format(self.name.upper()))], messanger=self.messanger, asset_url=asset_url)
        else:
            print("Error: {} hat keinen Weg.".format(self.name))

        # Navigation
        if "Navigation" in self.interaktion_dict.keys():
            self.actions["{}_navigation".format(self.name)] = readActions(
                self.interaktion_dict["Navigation"], messanger=self.messanger, asset_url=asset_url)
        else:
            print("Error: {} hat keine Navigation.".format(self.name))

        # Tipp
        if "Tipp" in self.interaktion_dict.keys():
            self.actions["{}_tipp".format(self.name)] = readActions(
                self.interaktion_dict["Tipp"], messanger=self.messanger, asset_url=asset_url)
            self.tipp_action = "{}_tipp".format(self.name)
        else:
            self.tipp_action = "weiter_wohin_tipp"
            self.action_requirements.append("weiter_wohin_tipp")
            print(
                "Info: {} hat keinen Tipp. - Standardwert weiter_wohin_tipp wird benutzt.".format(self.name))