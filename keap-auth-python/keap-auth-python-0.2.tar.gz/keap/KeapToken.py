from time import time


class KeapToken:
    def __init__(self, **kwargs):
        self.access_token = kwargs.get("access_token", None)
        self.refresh_token = kwargs.get("refresh_token", None)
        self.expires_in = kwargs.get("expires_in", 0)
        self.end_of_life = kwargs.get("end_of_life", int(time()) + self.expires_in)
        self.scope = kwargs.get("scope", None)

    @property
    def is_expired(self):
        return self.end_of_life < int(time())
