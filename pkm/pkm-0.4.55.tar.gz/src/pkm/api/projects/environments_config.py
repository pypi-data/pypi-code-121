from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any

from pkm.config.configuration import TomlFileConfiguration, computed_based_on

ENVIRONMENT_CONFIGURATION_PATH = "etc/pkm/environments.toml"


@dataclass(frozen=True, eq=True)
class AttachedEnvironmentConfig:
    path: Optional[Path] = None
    zoo: Optional[Path] = None

    def to_config(self) -> Dict[str, Any]:
        return {k: str(v) for k, v in self.__dict__ if v is not None}

    @classmethod
    def from_config(cls, cfg: Dict[str, Any]):
        return AttachedEnvironmentConfig(**{k: Path(v) for k, v in cfg.items()})


class EnvironmentsConfiguration(TomlFileConfiguration):
    attached_env: Optional[AttachedEnvironmentConfig]

    @computed_based_on("attached-env")
    def attached_env(self) -> Optional[AttachedEnvironmentConfig]:
        if config := self["attached-env"]:
            return AttachedEnvironmentConfig.from_config(config)
        return None
