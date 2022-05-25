from perun.connector.models.HasIdAbstract import HasIdAbstract
from perun.connector.models.VO import VO


class Group(HasIdAbstract):
    def __init__(
        self,
        id: int,
        vo: VO,
        uuid: str,
        name: str,
        unique_name: str,
        description: str,
    ):
        super().__init__(id)
        self.vo = vo
        self.uuid = uuid
        self.name = name
        self.unique_name = unique_name
        self.description = description

    def __str__(self):
        return (
            f"id: {self.id} vo: {self.vo} uuid: {self.uuid} name: "
            f"{self.name} unique_name: {self.unique_name}, descri"
            f"ption: {self.description}"
        )

    def __eq__(self, other):
        if isinstance(other, Group):
            return (
                self.id == other.id
                and self.vo == other.vo
                and self.uuid == other.uuid
                and self.name == other.name
                and self.unique_name == other.unique_name
                and self.description == other.description
            )
        return False
