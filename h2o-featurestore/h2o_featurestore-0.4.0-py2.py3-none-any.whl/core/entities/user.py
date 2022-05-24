from ..utils import Utils


class User:
    def __init__(self, user):
        self._user = user

    @property
    def id(self):
        return self._user.id

    @property
    def name(self):
        return self._user.name

    @property
    def email(self):
        return self._user.email

    def __repr__(self):
        return Utils.pretty_print_proto(self._user)
