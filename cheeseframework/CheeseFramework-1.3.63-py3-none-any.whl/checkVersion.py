#cheese

import json
import requests
from importlib.metadata import version

class Updater:

    @staticmethod
    def checkUpdate():     
        vers = version("CheeseFramework")
        try:
            r = requests.get("https://pypi.org/pypi/CheeseFramework/json").text
            aversion = json.loads(r)["info"]["version"]
        except:
            print("Cannot check latest Cheese version")
            return

        if (vers != aversion):
            print(30*"=")
            print(f"You have got version {vers} but the latest Cheese is {aversion}")
            print("Update Cheese with command:")
            print("")
            print(f"pip install CheeseFramework=={aversion}")
            print("")
            print(30*"=")
            print("")


