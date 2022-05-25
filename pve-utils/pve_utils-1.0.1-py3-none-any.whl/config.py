import os
import sys
from typing import Dict, get_type_hints

import environ

from pve_utils.utils import pprint


class Settings:
    _typings: Dict
    _instance = None
    _env = environ.Env()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._typings = get_type_hints(cls)
            if cls._env("USE_ENV_FILE", cast=bool, default=False):
                environ.Env.read_env(
                    os.path.join(
                        os.path.dirname(os.path.dirname(__file__)), ".env"
                    )
                )
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __getattribute__(self, key: str):
        if key.startswith("_"):
            return super().__getattribute__(key)
        attr = self._env(key, cast=self._typings.get(key, None), default=None)
        if attr is not None:
            return attr
        if key in dir(Settings):
            return super().__getattribute__(key)
        if attr is None:
            pprint.error(f"Variable {key} dosen`t exist in env")
            sys.exit(1)

    PROXMOX_URL: str
    PROXMOX_PORT: int
    PROXMOX_USER: str
    PROXMOX_PASSWORD: str
    PROXMOX_VERIFY_SSL: bool = False
    CT_STORAGE: str
    CT_OS_TEMPLATE: str
    CT_PASSWORD: str
    CT_NET_NAME: str
    CT_NET_BRIDGE: str
    CT_IP: str
    CT_GW: str
    CT_CIDR: int


settings = Settings()
