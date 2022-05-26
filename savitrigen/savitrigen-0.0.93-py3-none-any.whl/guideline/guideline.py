from .rules import (
    MODULE_NAMING,
    FIELD_NAMING,
    PLUGIN_NAMING
)

class Guideline(object):
    def __getattr__(self, name:str):
        if name.startswith('__'):
            return getattr(object, name)

        tp = name.split('check_')[-1].upper()
        def func(*args, **kwargs):
            for t in globals()[tp]:
                self.check(*t, *args, **kwargs)

        return func

    @staticmethod
    def check(test, message, subject) -> None:
        if test(subject):
            raise TypeError('{}: {}'.format(message, subject))
