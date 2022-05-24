from abc import ABC
from typing import Any, Dict, List

from dnastack.configuration.models import OAuth2Authentication
from dnastack.common.logger import get_logger


class OAuth2Adapter(ABC):
    def __init__(self, auth_info: OAuth2Authentication):
        self._auth_info = auth_info
        self._logger = get_logger(f'{type(self).__name__}/{self._auth_info.get_content_hash()[:8]}')

    @property
    def auth_info(self) -> OAuth2Authentication:
        return self._auth_info

    def check_config_readiness(self):
        property_names = self.get_expected_auth_info_fields()
        auth = self.auth_info

        missing_property_names = [
            property_name
            for property_name in property_names
            if not hasattr(auth, property_name) or not getattr(auth, property_name)
        ]

        if missing_property_names:
            raise AssertionError(f"{type(self).__module__}.{type(self).__name__}: {self._auth_info}: Missing {', '.join(missing_property_names)}")

    @classmethod
    def is_compatible_with(cls, auth_info: OAuth2Authentication) -> bool:
        property_names = cls.get_expected_auth_info_fields()
        auth = auth_info

        for property_name in property_names:
            if not hasattr(auth, property_name) or not getattr(auth, property_name):
                return False

        return True

    @staticmethod
    def get_expected_auth_info_fields() -> List[str]:
        raise NotImplementedError()

    def exchange_tokens(self) -> Dict[str, Any]:
        """
        :raises AuthException: raised when the authentication fails
        """
        raise NotImplementedError()
