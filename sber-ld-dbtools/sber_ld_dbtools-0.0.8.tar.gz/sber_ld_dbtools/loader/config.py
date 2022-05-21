from collections.abc import Mapping as _Mapping
from typing import Mapping, Dict, Type, Optional, Any

from typing_extensions import final
from varutils.typing import check_type_compatibility

from sber_ld_dbtools.credentials import PasswordKeeper

__all__ = (
    'GlobalConfigType',
)


class GlobalConfigType:
    __slots__ = ('__default_credentials', '__default_parameters')
    __instances: Dict[Type['GlobalConfigType'], 'GlobalConfigType'] = {}

    @final
    def __new__(cls) -> 'GlobalConfigType':
        instances = GlobalConfigType.__instances
        instance = instances.get(cls)
        if instance is None:
            instance = super().__new__(cls)
            instances[cls] = instance
        return instance

    def __init__(self) -> None:
        self.__default_credentials: Optional[PasswordKeeper] = None
        self.__default_parameters: Optional[Dict[str, Any]] = None

    @property
    def DEFAULT_CREDENTIALS(self) -> Optional[PasswordKeeper]:
        return self.__default_credentials

    @DEFAULT_CREDENTIALS.setter
    def DEFAULT_CREDENTIALS(self, value: PasswordKeeper) -> None:
        check_type_compatibility(value, PasswordKeeper)
        self.__default_credentials = value

    @property
    def DEFAULT_LOGIN_PARAMETERS(self) -> Optional[Dict[str, Any]]:
        return self.__default_parameters

    @DEFAULT_LOGIN_PARAMETERS.setter
    def DEFAULT_LOGIN_PARAMETERS(self, value: Mapping[str, Any]) -> None:
        check_type_compatibility(value, _Mapping, 'Mapping')
        self.__default_parameters = dict(value)
