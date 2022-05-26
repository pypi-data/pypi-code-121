import importlib
import os
import warnings
from price_val_engine.conf import default_settings
from price_val_engine.core.exceptions import ImproperlyConfigured

__all__ = [
    "settings",   
]

ENV_VAR = 'PRICE_VAL_ENG_SETTINGS_MODULE'

class Settings:
    def __init__(self, settings_module):
        # update this dict from global settings (but only for ALL_CAPS settings)
        for setting in dir(default_settings):
            if setting.isupper():
                setattr(self, setting, getattr(default_settings, setting))

        # store the settings module in case someone later cares
        self.SETTINGS_MODULE = settings_module
        self._explicit_settings = set()
        
        if self.SETTINGS_MODULE:
            mod = importlib.import_module(self.SETTINGS_MODULE)
            tuple_settings = (
                "VALIDATION_PIPELINES",
            )
            proj_settings = [setting for setting in dir(mod) if not str(setting).startswith("_")]
            for setting in proj_settings:
                if setting.isupper():
                    setting_value = getattr(mod, setting)

                    if setting in tuple_settings and not isinstance(
                        setting_value, (list, tuple)
                    ):
                        raise ImproperlyConfigured(
                            "The %s setting must be a list or a tuple." % setting
                        )
                    setattr(self, setting, setting_value)
                    self._explicit_settings.add(setting)
                    
    def __repr__(self):
        return '<%(cls)s "%(settings_module)s">' % {
            "cls": self.__class__.__name__,
            "settings_module": self.SETTINGS_MODULE,
        }

settings = Settings(os.environ.get(ENV_VAR))

