from pyrasgo.api import Create, Delete, Get, Publish, Read, Update


class Rasgo:
    """
    Base connection object to handle interactions with the Rasgo API.
    """

    def __init__(self):
        self._experiment_id = None
        self.create = Create()
        self.delete = Delete()
        self.get = Get()
        self.publish = Publish()
        self.read = Read()
        self.update = Update()

    def _pyrasgo_api_key(self):
        from pyrasgo.config import get_session_api_key

        return get_session_api_key()
