from perun.connector.models.HasIdAbstract import HasIdAbstract


class User(HasIdAbstract):
    def __init__(self, id: int, name: str):
        super().__init__(id)
        self.name = name

    def __str__(self):
        return f"id: {self.id} name: {self.name}"

    def __eq__(self, other):
        if isinstance(other, User):
            return self.id == other.id and self.name == other.name
        return False
