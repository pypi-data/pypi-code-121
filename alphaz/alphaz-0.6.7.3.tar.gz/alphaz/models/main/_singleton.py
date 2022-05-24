class Singleton(object):
    _instance = None
    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)
        return class_._instance

def singleton(cls):
    instance = None
    def ctor(*args, **kwargs):
        nonlocal instance
        if not instance:
            instance = cls(*args, **kwargs)
        return instance
    return ctor

"""class AlphaSingleton:
    class __OnlyOne:
        def __init__(self, arg):
            self.val = arg
        def __str__(self):
            return repr(self) + self.val

    instance = None

    def __init__(self, arg):
        if not AlphaSingleton.instance:
            AlphaSingleton.instance = AlphaSingleton.__OnlyOne(arg)
        else:
            AlphaSingleton.instance.val = arg

    def __getattr__(self, name):
        return getattr(self.instance, name)"""