from smartinput.types import EventType, Event
import serial
import signal
import logging
import sys

def parse_event(payload: str):
    try:
      event_type_raw, key_raw  = payload.split(":")
      key = key_raw.rstrip()
      event_type = EventType(event_type_raw)
    except ValueError:
      return None

    return Event(key=key, event_type=event_type)

def alarm_handler(signum, frame):
    logging.error("Connection lost, exiting")
    sys.exit(1)

signal.signal(signal.SIGALRM, alarm_handler)
def wait_for_event(device: serial.Serial):
    event = None
    while event == None:
      signal.alarm(2) # not really convinced wheter I hate or love this
      data = device.readline().decode()
      signal.alarm(0)
      event = parse_event(data)
    return event
