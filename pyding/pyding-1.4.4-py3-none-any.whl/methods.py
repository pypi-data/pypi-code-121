# methods.py
from .event_space import global_event_space
from .structures import EventCall, EventHandler


on = global_event_space.on
call = global_event_space.call