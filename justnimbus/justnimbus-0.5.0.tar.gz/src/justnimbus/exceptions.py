class JustNimbusError(Exception):
    pass


class InvalidClientID(JustNimbusError):
    def __init__(self, client_id: str):
        super().__init__(f"{client_id!r} is an invalid client_id")
        self.client_id = client_id
