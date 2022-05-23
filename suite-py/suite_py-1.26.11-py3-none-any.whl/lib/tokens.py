# -*- encoding: utf-8 -*-
import marshal
import os

from InquirerPy import prompt

TOKENS = ["github", "youtrack", "drone"]


class Tokens:
    def __init__(self, file_name=os.path.join(os.environ["HOME"], ".suite_py/tokens")):
        self._file_name = file_name
        self._tokens = {}
        try:
            self.load()
        except Exception:
            pass

        self._changed = False
        self.check()
        if self._changed:
            self.save()

    def load(self):
        with open(self._file_name, "rb") as configfile:
            self._tokens = marshal.load(configfile)

    def check(self):
        for token in TOKENS:
            if not self._tokens.get(token):
                self._tokens[token] = prompt(
                    [
                        {
                            "type": "input",
                            "name": token,
                            "message": f"Insert your {token.capitalize()} token:",
                        }
                    ]
                )[token]
                self._changed = True

    def save(self):
        with open(self._file_name, "wb") as configfile:
            marshal.dump(self._tokens, configfile)

    def edit(self, service, token):
        self._tokens[service] = token

    @property
    def github(self):
        return self._tokens["github"]

    @property
    def youtrack(self):
        return self._tokens["youtrack"]

    @property
    def drone(self):
        return self._tokens["drone"]
