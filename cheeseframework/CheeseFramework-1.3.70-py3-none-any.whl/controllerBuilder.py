#cheese

import os

from Cheese.resourceManager import ResMan
from Cheese.finder import Finder

class ControllerBuilder:

    @staticmethod
    def build(parent):
        controllers = []

        for root, dirs, files in os.walk(ResMan.root()):
            for file in files:
                if (not file.endswith(".py")): continue

                path = os.path.join(root, file)

                if (Finder.isSomething(path, "controller")): 
                    controllers.append(path)

        parent.doJson(controllers, "CONTROLLERS", 
            ["CONTROLLER"],
            [("POST", [("POST",)]), ("GET", [("GET",)])]
        )

