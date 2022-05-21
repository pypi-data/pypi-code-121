from __future__ import annotations

import warnings
from copy import copy
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Any, Dict, List, Mapping

from pkm.config.configuration import TomlFileConfiguration, computed_based_on
from pkm.utils.dicts import remove_none_values
from pkm.utils.hashes import HashBuilder


class RepositoriesConfigInheritanceMode(Enum):
    INHERIT_CONTEXT = 0,
    INHERIT_GLOBAL = 1,
    NO_INHERITANCE = 2


class RepositoriesConfiguration(TomlFileConfiguration):
    repositories: List[RepositoryInstanceConfig]
    inheritance_mode: RepositoriesConfigInheritanceMode
    package_bindings: Mapping[str, Any]

    @computed_based_on("inheritance")
    def inheritance_mode(self) -> RepositoriesConfigInheritanceMode:
        value = self["inheritance"]
        if value is not None:
            if value == "global":
                return RepositoriesConfigInheritanceMode.INHERIT_GLOBAL
            if not value:
                return RepositoriesConfigInheritanceMode.NO_INHERITANCE
        return RepositoriesConfigInheritanceMode.INHERIT_CONTEXT

    @computed_based_on("package-bindings")
    def package_bindings(self) -> Mapping[str, Any]:
        return self["package-bindings"] or {}

    @package_bindings.modifier
    def set_package_bindings(self, new_bindings: Mapping[str, Any]):
        self["package-bindings"] = new_bindings

    @computed_based_on("repos")
    def repositories(self) -> List[RepositoryInstanceConfig]:
        repositories: Dict[str, Dict] = self["repos"] or {}

        def read_config_warn_err(name: str, repo: Dict[str, str]) -> Optional[RepositoryInstanceConfig]:
            try:
                return RepositoryInstanceConfig.from_config(name, repo)
            except Exception as e:
                warnings.warn(f"could not process repository config for {name}: {e}, ignoring its configuration")
                return None

        return [
            repo_instance for name, repo in repositories.items()
            if (repo_instance := read_config_warn_err(name, repo)) is not None]

    @repositories.modifier
    def set_repositories(self, repos: List[RepositoryInstanceConfig]):
        self["repos"] = {r.name: r.to_config() for r in repos}


@dataclass(frozen=True, eq=True)
class RepositoryInstanceConfig:
    type: str
    bind_only: Optional[bool]
    name: Optional[str]
    args: Dict[str, str]

    def __hash__(self):
        return HashBuilder() \
            .regulars(self.type, self.name, self.bind_only) \
            .unordered_mapping(self.args) \
            .build()

    def to_config(self) -> Dict[str, Any]:
        return remove_none_values({
            **self.args,
            'type': self.type,
            'bind-only': self.bind_only
        })

    @classmethod
    def from_config(cls, name: str, config: Dict[str, Any]) -> "RepositoryInstanceConfig":
        config = copy(config)
        type_ = config.pop('type')
        bind_only: bool = config.pop('bind-only', False)
        args = config
        return RepositoryInstanceConfig(type_, bind_only, name, args)
