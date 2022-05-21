from base64 import b64encode
from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True, eq=True)
class BasicAuthentication:
    username: str
    password: str

    def as_header(self) -> Tuple[str, str]:
        return 'Authorization', f'Basic {b64encode(f"{self.username}:{self.password}".encode()).decode("ascii")}'
