import json
from json import JSONDecodeError

from keap.KeapToken import KeapToken


class KeapTokenStorage:
    def __init__(self, storage_path):
        self.storage_path = storage_path

    def load_tokens(self) -> dict:
        tokens = {}
        try:
            with open(self.storage_path, "r") as f:
                tokens = json.load(f)
        except FileNotFoundError as e:
            with open(self.storage_path, "w") as f:
                json.dump(tokens, f, indent=4, ensure_ascii=True)
        except JSONDecodeError as e:
            with open(self.storage_path, "w") as f:
                json.dump(tokens, f, indent=4, ensure_ascii=True)
        return tokens

    def get_token(self, app) -> KeapToken:
        tokens = self.load_tokens()
        try:
            if app in tokens:
                return KeapToken(**tokens[app])
        except Exception as e:
            pass
        return KeapToken()

    def save_token(self, app, token):
        tokens = self.load_tokens()
        tokens[app] = token.__dict__
        with open(self.storage_path, "w") as f:
            json.dump(tokens, f, indent=4, ensure_ascii=True)

    def list_tokens_by_name(self):
        tokens = self.load_tokens()
        return list(tokens.keys())
