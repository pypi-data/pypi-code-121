import inspect

from ..orange_version import ORANGE_VERSION

if ORANGE_VERSION == ORANGE_VERSION.oasys_fork:
    from orangewidget.settings import Setting
else:
    from orangewidget.settings import Setting


def is_setting(obj):
    return isinstance(obj, Setting)


def get_settings(widget_class):
    return dict(inspect.getmembers(widget_class, is_setting))
