from types import FunctionType, MethodType, ModuleType

class eventMeta(type):
    def __new__(cls, name, bases, dct):
        attrs = {'_eventList': {}}
        for key, value in dct.items():
            attrs[key]= value
        attrs['_event_register']= register
        attrs['_event_on']= trigger
        attrs['_event_remove']= removeEvent
        return super(eventMeta, cls).__new__(cls, name, bases, attrs)

def register(self, name, func):
    if name not in self._eventList:
        self._eventList[name] = func
    else:
        raise Exception('event (%s) already registered.' % name)


def removeEvent(self, name):
    if name in self._eventList:
        self._eventList.pop(name)
    else:
        raise Exception('event (%s) not registered.' % name)


def trigger(self, name, *args, **kwargs):
    if name in self._eventList:
        self._eventList[name](self, *args, **kwargs)
    else:
        raise Exception('event (%s) not registered.' % name)

