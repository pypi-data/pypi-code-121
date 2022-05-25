import importlib
import os

from mvapi.settings import settings
from mvapi.web.views.base import BaseView

RESOURCE_VIEWS = {}


def import_views():
    views = [__package__] + settings.VIEWS

    for view_str in views:
        view = importlib.import_module(view_str)
        for file in os.listdir(os.path.dirname(view.__file__)):
            if not file.startswith('__') and file.endswith('.py'):
                name = file.rpartition('.')[0]
                mod = importlib.import_module(f'{view.__package__}.{name}')
                for attr_name in dir(mod):
                    attr = getattr(mod, attr_name)
                    if type(attr) == type and \
                            issubclass(attr, BaseView) and \
                            attr != BaseView:
                        RESOURCE_VIEWS[attr.resource_type] = attr
