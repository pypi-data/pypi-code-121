from kedro_fast_api.models.config_parser import ConfigParser


class Config(ConfigParser):
    def __init__(self, path: str) -> None:
        super().__init__(path)
