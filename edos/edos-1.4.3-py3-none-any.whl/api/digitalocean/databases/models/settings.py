import dataclasses


@dataclasses.dataclass
class MysqlSettings:
    auth_plugin: str
