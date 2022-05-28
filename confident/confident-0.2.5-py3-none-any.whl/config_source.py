from enum import Enum


class ConfigSource(str, Enum):
    """
    Possible kinds of configuration sources.
    """
    init = 'init'
    env_var = 'env_var'
    map = 'map'
    file = 'file'
    class_default = 'class_default'

    def __repr__(self):
        return "'" + self.value + "'"

    def __str__(self):
        return str(self.value)
