from requests import Response
from .logger import Logger


class ConfigHelper:
    """Static class to store configuration and status display config"""

    host = ""
    verbose = None

    @classmethod
    def show_status(self, text: str, r: Response):
        reason = r.reason if r.status_code == 200 else r.content.decode("ascii")

        Logger.write(f"[{'API':5s}] {text:30s} [{r.status_code}] {reason}")
