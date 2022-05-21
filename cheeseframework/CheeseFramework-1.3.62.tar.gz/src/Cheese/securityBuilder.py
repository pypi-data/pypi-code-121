#cheese

import os
import json

from Cheese.resourceManager import ResMan
from Cheese.finder import Finder

class SecurityBuilder:
    
    @staticmethod
    def build(parent):
        with open(ResMan.root("adminSettings.json"), "r") as f:
            data = json.loads(f.read())

        parent.dictJson["ADMIN"] = data

        secPath = ResMan.root("securitySettings.json")
        with open(secPath, "r") as f:
            data = json.loads(f.read())

        finder = Finder()
        finder.validateKey("authentication", data, secPath)
        finder.validateKey("roles", data, secPath)
        finder.validateKey("access", data, secPath)
        
        security = {}
        security["AUTHENTICATION"] = data["authentication"]
        security["ROLES"] = data["roles"]
        access = {}
        controllers = parent.dictJson["CONTROLLERS"]

        for key in data["access"].keys():
            if (key.endswith("*")):
                keyFor = key.replace("*", "")
                for contKey in controllers.keys():
                    contr = controllers[contKey]
                    mainEndpoint = contr["CONTROLLER"]
                    if (keyFor.startswith(mainEndpoint)):
                        # this is it
                        methodKeys = contr["METHODS"].keys()
                        for methodKey in methodKeys:
                            if (methodKey not in data["access"].keys()):
                                access[keyFor + methodKey] = data["access"][key]
            else:
                access[key] = data["access"][key]

        security["ACCESS"] = access

        parent.dictJson["SECURITY"] = security

        if (os.path.exists(ResMan.root("secrets.json"))):
            with open(ResMan.root("secrets.json"), "r") as f:
                secrets = json.loads(f.read())
        else:
            secrets = {}
        parent.dictJson["SECRETS"] = secrets

