from smartinput.handlers.base import BaseHandler
from smartinput.types import Event
import pyautogui

class KeyboardHandler(BaseHandler):
  """simulates keystrokes
  
  params are:
  keys: list[str] or str if mode is write (keys to press)
  mode: 'shortcut' or 'type'
  interval: Optional[float]
  """
  def __init__(self) -> None:
    self.params = {}

  def handle_event(self, event: Event):
    if self.params.get('mode') == 'type':
      keys = self.params.get('keys')
      if isinstance(keys, list):
        keys = ' '.join(keys)
      pyautogui.typewrite(keys, self.params.get('interval') or 0)
    else:
      pyautogui.hotkey(*self.params.get('keys'))

  def set_params(self, params: dict):
    self.params = params
