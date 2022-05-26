from smartinput.types import Event
from smartinput.handlers.base import BaseHandler
from smartinput.handlers.exec import ExecHandler
from smartinput.handlers.http import HttpHandler
from smartinput.handlers.keyboard import KeyboardHandler
import logging
import threading


available_handlers = {
  'exec': ExecHandler,
  'http': HttpHandler,
  'keyboard': KeyboardHandler
}

def handle_event(event: Event, keys_config):
  event_type = event.event_type.name
  key_config = keys_config.get(event.key)
  if not key_config:
    return
  
  event_configs  = key_config.get(event_type)
  if not event_configs:
    return

  for event_config in event_configs:
    handler: BaseHandler = available_handlers[event_config['handler']]()
    handler.set_params(event_config['params'])
    logging.info(f"handling event {event.event_type.name} for key {event.key} with handler {event_config['handler']}")

    threading.Thread(target=handler.handle_event, args=(event,)).start()