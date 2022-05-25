import requests

PERMA_URL = "https://avd.al/globals.json"


class Globals:
    def __init__(self):
        self.globals = requests.get(PERMA_URL).json()
        self.globals = self.globals["globals"]
        self.vars = self.globals["vars"]

    def get_var(self, name, default=None):
        return self.vars.get(name, default)
