from smartinput.handlers.base import BaseHandler
from smartinput.types import Event
import requests

class HttpHandler(BaseHandler):
  def __init__(self) -> None:
    self.params = {}

  def handle_event(self, event: Event):
    requests.request(method=self.params['method'], url=self.params['url'], json=self.params.get('json'))

  def set_params(self, params: dict):
    self.params = params
