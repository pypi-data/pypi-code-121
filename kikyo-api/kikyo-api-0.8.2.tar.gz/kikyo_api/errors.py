class KikyoClientError(Exception):
    @property
    def status_code(self) -> int:
        return self.args[0]

    @property
    def error(self) -> str:
        return self.args[1]


class KikyoAPIError(Exception):
    pass
