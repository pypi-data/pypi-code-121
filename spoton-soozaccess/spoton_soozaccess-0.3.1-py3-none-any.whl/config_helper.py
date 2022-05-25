from requests import Response
from .logger import Logger


class ConfigHelper:
    """Static class to store configuration and status display config"""

    host = ""
    verbose = None

    @classmethod
    def show_status(self, text: str, r: Response):
        Logger.write(f"[{'API':5s}] {text:30s} [{r.status_code}] {r.reason}")
