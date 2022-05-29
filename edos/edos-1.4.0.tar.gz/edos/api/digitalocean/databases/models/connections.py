import dataclasses


@dataclasses.dataclass
class DatabaseConnection:
    uri: str
    database: str
    host: str
    port: int
    user: str
    password: str
    ssl: bool
