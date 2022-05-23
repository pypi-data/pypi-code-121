import enum
import json
import os
from sys import platform


class Action(enum.Enum):
    SHOW_ERROR = "show_error"
    SHOW_MESSAGE = "show_message"
    RESULT = "result"
    OPEN_FILE = "open_file"
    COMMAND = "command"


class Intellij():
    __instance = None

    @staticmethod
    def getInstance():
        if Intellij.__instance == None:
            return Intellij()
        return Intellij.__instance

    def __init__(self):
        Intellij.__instance = self
        self.actions = []

    def put_data(self, value, message):
        for action in self.actions:
            if action["action"] == value:
                action["param"] += "\n%s" % message
                return
        self.actions.append({"action": value, "param": message})

    def add_error(self, message):
        self.put_data(Action.SHOW_ERROR.value, message)

    def add_message(self, message):
        self.put_data(Action.SHOW_MESSAGE.value, message)

    def add_result(self, result):
        self.put_data(Action.RESULT.value, result)

    def add_open_file(self, path):
        self.put_data(Action.OPEN_FILE.value, path)

    def add_command(self, command):
        self.put_data(Action.COMMAND.value, command)

    def to_file(self):
        if self.actions:
            from .file_helpers import get_local_data_dictionary
            data_folder = get_local_data_dictionary()
            if platform == "win32" or platform == "win64":
                process_id = os.getppid()
            else:
                process_id = os.getpid()
            with open("%s/%s.pt" % (data_folder, process_id), "w") as f:
                data = json.dumps({"actions": self.actions},
                                  sort_keys=True, indent=4)
                f.write(data)
