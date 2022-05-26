from typing import Any, Dict, Optional, TypedDict

import immutables
from sym.shared.cli.helpers.config.base import ConfigBase

from sym.flow.cli.models import AuthToken, Organization


class ConfigSchema(TypedDict, total=False):
    org: str
    client_id: str
    email: str
    auth_token: AuthToken


def deepget(key: str, data: Dict[str, Any]) -> Optional[str]:
    """Tries to get a nested value from a dict"""
    for k in key.split("."):
        try:
            data = data[k]
        except KeyError:
            return None

    return data if isinstance(data, str) else None


class Config(ConfigBase[ConfigSchema]):
    @classmethod
    def get_value(cls, key: str) -> Optional[str]:
        config = cls.instance()
        return deepget(key, config)

    @classmethod
    def get_org(cls) -> immutables.Map:
        config = cls.instance()
        return immutables.Map(
            Organization(slug=config["org"], client_id=config["client_id"])
        )

    @classmethod
    def get_access_token(cls) -> Optional[str]:
        try:
            return cls.instance()["auth_token"]["access_token"]
        except KeyError:
            return None

    @classmethod
    def logout(cls):
        if not cls.is_logged_in():
            return

        cfg = cls.instance()
        del cfg["email"]
        del cfg["org"]
        del cfg["client_id"]
        del cfg["auth_token"]


def store_login_config(email: str, org: Organization, auth_token: AuthToken) -> str:
    cfg = Config.instance()
    cfg["email"] = email
    cfg["org"] = org["slug"]
    cfg["client_id"] = org["client_id"]
    cfg["auth_token"] = auth_token
    return str(cfg.file)
