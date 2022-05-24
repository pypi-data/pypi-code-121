"""
Configuration exception module
"""
from typing import List

SAMPLE_JSON = '{"auth_server": "login.hyperscience.net", "hs_domain": "cloud.hyperscience.net"}'

ERROR_MESSAGE = (
    'The following json object format is expected: {sample_json}. '
    'missing parameters: {invalid_params}'
)


class InvalidConfigurationException(Exception):
    """
    This exception thrown for invalid configuration
    """

    def __init__(self, invalid_params: List[str]) -> None:
        super().__init__(
            ERROR_MESSAGE.format(invalid_params=invalid_params, sample_json=SAMPLE_JSON)
        )
