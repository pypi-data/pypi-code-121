from copy import deepcopy
from dataclasses import dataclass, fields, MISSING
from typing import Any, Dict, Optional, Union, Tuple


@dataclass
class BaseConfig:
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        _data = deepcopy(data)

        def _from_dict(T: type, data: Dict[str, Union[str, BaseConfig]]):
            if data is None:
                return None
            T = unwrap_optional_type(T)
            if issubclass(T, BaseConfig):
                return T.from_dict(data)
            return data

        members = {
            f.name: _from_dict(f.type, _data.pop(f.name))
            for f in fields(cls)
            if f.name in _data
        }
        return cls(**members, **_data)

    @classmethod
    def empty(cls, **kwargs):
        """Create an empty config"""

        def _empty(T: type, **kwargs):
            if issubclass(T, BaseConfig):
                required_fields = (
                    (f.name, f.type)
                    for f in fields(T)
                    if f.default is MISSING and f.default_factory is MISSING
                )
                converted = {
                    f_name: _empty(f_type) for f_name, f_type in required_fields
                }
                converted.update(kwargs)
                return T(**converted)
            return ""

        return _empty(cls, **kwargs)


def unwrap_optional_type(T: type) -> type:
    opt_types: Tuple[type, ...] = getattr(T, "__args__", ())
    if not isinstance(None, opt_types) or getattr(T, "__origin__", None) is not Union:
        return T
    return opt_types[0]


@dataclass
class Oidc(BaseConfig):
    client_id: str
    client_secret: str
    config_url: str
    login_redirect_url: str = "/"
    logout_redirect_url: str = "/"


@dataclass
class Email(BaseConfig):
    host: str
    port: int
    use_tls: bool
    user: str
    password: str
    from_address: str
    subject_prefix: Optional[str] = ""


@dataclass
class Session(BaseConfig):
    expire_at_browser_close: bool = False
    expire_seconds: int = 86400


@dataclass
class Logging(BaseConfig):
    level: str = "INFO"
    path: Optional[str] = None
