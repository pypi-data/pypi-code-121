from smartinput.types import Event

class BaseHandler:
  def set_params(self, params: dict):
    raise NotImplementedError

  def handle_event(self, event: Event):
    raise NotImplementedError