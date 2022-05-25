from perun.connector.models.HasIdAbstract import HasIdAbstract
from perun.connector.models.User import User


class UserExtSource(HasIdAbstract):
    def __init__(self, id: int, name: str, login: str, user: User):
        super().__init__(id)
        self.name = name
        self.login = login
        self.user = user

    def __str__(self):
        return (
            f"id: {self.id} name: {self.name} login: {self.login} "
            f"user: {self.user}"
        )

    def __eq__(self, other):
        if isinstance(other, UserExtSource):
            return (
                self.id == other.id
                and self.name == other.name
                and self.login == other.login
                and self.user == other.user
            )
        return False
