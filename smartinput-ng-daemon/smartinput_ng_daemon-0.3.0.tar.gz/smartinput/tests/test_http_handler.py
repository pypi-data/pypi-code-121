import unittest
import uuid
from smartinput.handlers.http import HttpHandler
from smartinput.types import Event, EventType
import os
import time
import flask

class HttpHandlerTestCase(unittest.TestCase):
  def test_send_get_request(self):
    handler = HttpHandler()
    handler.set_params({'method': "GET", 'url': "https://example.com/"})
    event = Event("1", EventType.short_press)

    # handler.handle_event(event)
    # time.sleep(0.01) # make sure subprocess exited
    # self.assertTrue(os.path.isfile(path))
