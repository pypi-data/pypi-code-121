from collections import defaultdict
from digitalguide.standardinteraktion.Interaktion import Interaktion

class Route:
    def __init__(self):
        self.interaktionen = []
        self.states = defaultdict(list)
        self.actions = defaultdict(list)

    def from_excel_dict(self, excel_dict, messanger="Telegram", asset_url=""):
        self.messanger = messanger
        for excel_dict_item in excel_dict.items():
        
            interaktion = Interaktion.from_excel_dict(excel_dict_item, messanger=messanger, asset_url=asset_url)
            
            self.interaktionen.append(interaktion)

        self.generate_states()
        self.generate_actions()

        self.validate()

    def validate(self):
        action_requirements = []
        for interaktion in self.interaktionen:
            action_requirements += interaktion.action_requirements

        for action_requirement in action_requirements:
            if not action_requirement in self.actions.keys():
                print("ERROR: Die erforderliche Aktion {} ist nicht definiert.".format(action_requirement))

    def generate_states(self):
        self.states = {}
        for interaktion in self.interaktionen:
            self.states = {**self.states, **interaktion.states}

        if self.messanger == "Telegram":
            self.states["NONE"]=[]
        if self.messanger == "WhatsApp":
            from configparser import ConfigParser

            config = ConfigParser()
            config.read("config.ini")

            self.states["START_START"]=[{"handler": "TypeHandler", "type": "Update", "action": config["bot"]["start_action"]}]

    def generate_actions(self):
        self.actions = {}
        for interaktion in self.interaktionen:
            self.actions = {**self.actions, **interaktion.actions}
        
