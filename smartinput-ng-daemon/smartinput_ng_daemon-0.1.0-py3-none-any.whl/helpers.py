from smartinput.types import EventType, Event
import serial

def parse_event(payload: str):
    try:
      event_type_raw, key_raw  = payload.split(":")
      key = key_raw.rstrip()
      event_type = EventType(event_type_raw)
    except ValueError:
      return None

    return Event(key=key, event_type=event_type)

def wait_for_event(device: serial.Serial):
    event = None
    while event == None:
      data = device.readline().decode()
      event = parse_event(data)
    return event
