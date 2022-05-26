from smartinput.handlers.base import BaseHandler
from smartinput.types import Event
import subprocess


class ExecHandler(BaseHandler):
    def __init__(self) -> None:
        self.params = {}

    def handle_event(self, event: Event):
        subprocess.Popen(["bash", "-c", self.params['command']],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def set_params(self, params: dict):
        self.params = params
