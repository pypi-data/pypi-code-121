from typing import Any, cast, Dict, List, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.benchling_app_configuration import BenchlingAppConfiguration
from ..types import UNSET, Unset

T = TypeVar("T", bound="BenchlingAppConfigurationPaginatedList")


@attr.s(auto_attribs=True, repr=False)
class BenchlingAppConfigurationPaginatedList:
    """  """

    _app_configurations: Union[Unset, List[BenchlingAppConfiguration]] = UNSET
    _next_token: Union[Unset, str] = UNSET

    def __repr__(self):
        fields = []
        fields.append("app_configurations={}".format(repr(self._app_configurations)))
        fields.append("next_token={}".format(repr(self._next_token)))
        return "BenchlingAppConfigurationPaginatedList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        app_configurations: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._app_configurations, Unset):
            app_configurations = []
            for app_configurations_item_data in self._app_configurations:
                app_configurations_item = app_configurations_item_data.to_dict()

                app_configurations.append(app_configurations_item)

        next_token = self._next_token

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if app_configurations is not UNSET:
            field_dict["appConfigurations"] = app_configurations
        if next_token is not UNSET:
            field_dict["nextToken"] = next_token

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_app_configurations() -> Union[Unset, List[BenchlingAppConfiguration]]:
            app_configurations = []
            _app_configurations = d.pop("appConfigurations")
            for app_configurations_item_data in _app_configurations or []:
                app_configurations_item = BenchlingAppConfiguration.from_dict(app_configurations_item_data)

                app_configurations.append(app_configurations_item)

            return app_configurations

        app_configurations = (
            get_app_configurations()
            if "appConfigurations" in d
            else cast(Union[Unset, List[BenchlingAppConfiguration]], UNSET)
        )

        def get_next_token() -> Union[Unset, str]:
            next_token = d.pop("nextToken")
            return next_token

        next_token = get_next_token() if "nextToken" in d else cast(Union[Unset, str], UNSET)

        benchling_app_configuration_paginated_list = cls(
            app_configurations=app_configurations,
            next_token=next_token,
        )

        return benchling_app_configuration_paginated_list

    @property
    def app_configurations(self) -> List[BenchlingAppConfiguration]:
        if isinstance(self._app_configurations, Unset):
            raise NotPresentError(self, "app_configurations")
        return self._app_configurations

    @app_configurations.setter
    def app_configurations(self, value: List[BenchlingAppConfiguration]) -> None:
        self._app_configurations = value

    @app_configurations.deleter
    def app_configurations(self) -> None:
        self._app_configurations = UNSET

    @property
    def next_token(self) -> str:
        if isinstance(self._next_token, Unset):
            raise NotPresentError(self, "next_token")
        return self._next_token

    @next_token.setter
    def next_token(self, value: str) -> None:
        self._next_token = value

    @next_token.deleter
    def next_token(self) -> None:
        self._next_token = UNSET
