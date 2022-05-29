from huawei_lte_api.Connection import Connection

from .local_cfg import AuthConfig


class HRC_Connection(Connection):
    def __init__(self):
        auth_cfg = AuthConfig()
        super().__init__(
            url=auth_cfg.connection_address,
            username=auth_cfg.username,
            password=auth_cfg.password
        )
