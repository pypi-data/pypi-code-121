class User(object):
    def __init__(self, id, properties):
        self.id = id
        self.properties = properties


class Event(object):
    def __init__(self, key, value, properties):
        self.key = key
        self.value = value
        self.properties = properties


class Hackle:
    @staticmethod
    def user(id, **kwargs):
        return User(id, kwargs)

    @staticmethod
    def event(key, value=None, **kwargs):
        return Event(key, value, kwargs)
