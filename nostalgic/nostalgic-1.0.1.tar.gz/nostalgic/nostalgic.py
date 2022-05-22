import os
import sys
import json
import warnings
import configparser


def _show_only_warning_message(msg, *args, **kwargs):
    # the default warning behavior shows a superfluous line of code
    # See: https://stackoverflow.com/a/2187390
    return str(msg) + '\n'

warnings.formatwarning = _show_only_warning_message


class ShadowWarning(UserWarning):
    "Alert user that a Setting key is the same as a Configuration method."
    pass


class Setting:
    """Individual option setting.

    A Configuration is a collection of Settings.  A Setting represents
    some value which the developer wishes to persist beyond the
    immediate run.  Each Setting is identified by a key.  An optional
    default value may be set the initial value.  If the Setting
    corresponds to an object beside the Setting object, such as a UI
    element, optional setter and getter functions may be set.  These
    will be called on read and write.

    Parameters
    ----------
    key : Any valid dict key, str

      Setting identifier.

    default : object

      Initial value.

    setter : callable

      Function which assigns the current Setting.value.  Must take 1
      argument, the value to be set.

    getter : callable

      Function which retrieves a value.  Must have no parameters and
      return a value.

    """

    def __init__(self, key, default=None, setter=None, getter=None):

        self.key      = key
        self._default = default
        self.value   = self._default
        self.setter   = setter
        self.getter   = getter


class SingletonMetaclass(type):
    "Force a single Configuration instance."

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in SingletonMetaclass._instances:
            SingletonMetaclass._instances[cls] = super().__call__(*args, **kwargs)
        return SingletonMetaclass._instances[cls]

    def __reset(cls):
        """Delete the instance.

        Used for testing.

        Call as:

          nostalgic.Configuration._SingletonMetaclass__reset()

        """

        try:
            del SingletonMetaclass._instances[cls]
        except KeyError:
            pass


class Configuration(metaclass=SingletonMetaclass):
    """Collection of Settings.

    A Configuration describes the state of an application which the
    developer wishes to persist.  It provides a high-level interface
    to a collection of Setting objects.

    Parameters
    ----------
    filename : path-like object

      Location on disk to read and write Settings.

    """

    def __init__(self, filename=None):
        super().__init__()

        if filename is None:
            home_directory = os.path.expanduser('~')
            calling_module = os.path.basename(sys.argv[0]).split('.')[0]
            config_file    = calling_module + "_config"
            filename       = os.path.join(home_directory, config_file)

        filename = os.path.abspath(filename)

        # must define this way since we're overriding __setattr__
        self.__dict__['_settings'] = {}  # TODO mangle?

        # Default Settings
        self.add_setting('config_file', filename)

    def __getitem__(self, key):
        return self.__dict__['_settings'][key]

    def __getattr__(self, name):
        return self.__dict__['_settings'][name].value

    def __getattribute__(self, name):
        return object.__getattribute__(self, name)

    # TODO implement "(python) Emulating container types" methods

    def add_setting(self, key, default=None, getter=None, setter=None):
        # WARNING: Clobbers extant Setting with same key!
        setting = Setting(key, default=default, getter=getter, setter=setter)
        if key in Configuration.__dict__ and key[:2] != '__':
            warnings.warn(f"[WARNING]: Setting '{key}' shadows a bound method of the same name!", ShadowWarning)
        self.__dict__['_settings'][key] = setting

    def read(self, filename=None):
        if not filename:
            filename = self.config_file

        with open(filename, 'r', encoding='utf-8') as f:
            text = f.read()

        parser = configparser.ConfigParser()
        parser.read_string(text)

        for key, setting in self.__dict__['_settings'].items():
            if parser.has_option('General', key):
                raw_value = parser['General'][key]
                value = json.loads(raw_value)
                setting.value = value
                if setting.setter:
                    setting.setter(value)

    def write(self, filename=None):
        if not filename:
            filename = self.config_file

        if not os.path.isdir(os.path.dirname(self.config_file)):
            os.makedirs(os.path.dirname(self.config_file))

        parser = configparser.ConfigParser()
        parser.add_section('General')

        for key, setting in self.__dict__['_settings'].items():
            if key != 'config_file':
                if setting.getter:
                    setting.value = setting.getter()
                value = json.dumps(setting.value)
                parser.set('General', key, value)

        with open(self.config_file, 'w+', encoding='utf-8') as f:
            parser.write(f)
