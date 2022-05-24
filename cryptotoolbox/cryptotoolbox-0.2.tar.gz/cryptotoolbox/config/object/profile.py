__author__ = "hugo.inzirillo"

import six

from napoleontoolbox.napoleon_config_tools.object.config import Config
from npxlogger import log


class _Profile(object):

    def __init__(self, value: str):
        if isinstance(value, six.string_types):
            self.__value = value
        else:
            raise log.exception("Profile value should be string typed")

    def __call__(self, o: type):
        try:
            if isinstance(o, object):
                o.config = Config()
                o.config.package = str(__package__).split(".")[0]
                o.config.profile = self.__value

                return o
            else:
                raise TypeError("Not object typed")
        except Exception as e:
            raise e


Profile = _Profile
