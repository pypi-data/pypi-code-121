import unittest
from smartinput.helpers import parse_event
from smartinput.types import EventType

class ParseEventTestCase(unittest.TestCase):
  def test_short_press_key_0(self):
    event = parse_event("S:0")
    self.assertEqual(event.key, "0")
    self.assertEqual(event.event_type, EventType.short_press)

  def test_short_press_key_1(self):
    event = parse_event("S:1")
    self.assertEqual(event.key, "1")
    self.assertEqual(event.event_type, EventType.short_press)
  
  def test_release_key_6(self):
    event = parse_event("R:6")
    self.assertEqual(event.key, "6")
    self.assertEqual(event.event_type, EventType.release)
  
  def test_long_press_key_4(self):
    event = parse_event("L:4")
    self.assertEqual(event.key, "4")
    self.assertEqual(event.event_type, EventType.long_press)