from typing import Optional, Mapping, Tuple, Any

from hbutils.model import get_repr_info
from hbutils.string import env_template

from .base import SectionInfoTemplate, SectionInfo
from ...base import _process_environ


class _IStaticSectionInfo:
    def __init__(self, value: str):
        """
        :param value: static value 
        """
        self.__value = value

    def __repr__(self):
        """
        :return: representation string 
        """
        return get_repr_info(
            cls=self.__class__,
            args=[
                ('value', lambda: repr(self.__value)),
            ]
        )


class StaticSectionInfoTemplate(SectionInfoTemplate, _IStaticSectionInfo):
    def __init__(self, value: str):
        """
        :param value: static value 
        """
        self.__value = value
        _IStaticSectionInfo.__init__(self, self.__value)

    @property
    def value(self):
        return self.__value

    def __call__(self, environ: Optional[Mapping[str, str]] = None, **kwargs) -> 'StaticSectionInfo':
        """
        get static info info object
        :param environ: environment variables
        :return: static info info object
        """
        environ = _process_environ(environ)
        if isinstance(self.__value, str):
            _value = env_template(self.__value, environ)
        else:
            _value = self.__value

        return StaticSectionInfo(value=_value)


class StaticSectionInfo(SectionInfo, _IStaticSectionInfo):
    def __init__(self, value: str):
        """
        :param value: static value 
        """
        self.__value = value
        _IStaticSectionInfo.__init__(self, self.__value)

    @property
    def value(self):
        return self.__value

    def __call__(self, **kwargs) -> Tuple[bool, Any]:
        """
        execute this info info
        """
        return True, self.__value
