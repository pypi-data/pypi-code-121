from dataclasses import dataclass


@dataclass
class JupyterAPI:
    host: str = "127.0.0.1"
    port: int = 8888
    token: str = ""
