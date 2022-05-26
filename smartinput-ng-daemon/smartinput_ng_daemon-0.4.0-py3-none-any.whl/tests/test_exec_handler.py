import unittest
import uuid
from smartinput.handlers.exec import ExecHandler
from smartinput.types import Event, EventType
import os
import time

class ExecHandlerTestCase(unittest.TestCase):
  def test_create_file(self):
    handler = ExecHandler()
    path = os.path.join("/tmp", str(uuid.uuid4()))
    handler.set_params({'command': f"touch {path}"})
    event = Event("1", EventType.short_press)

    handler.handle_event(event)
    time.sleep(0.01) # make sure subprocess exited
    self.assertTrue(os.path.isfile(path))
