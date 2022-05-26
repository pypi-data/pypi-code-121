from perun.connector.models.Facility import Facility
from perun.connector.models.HasIdAbstract import HasIdAbstract
from perun.connector.models.VO import VO


class Resource(HasIdAbstract):
    def __init__(self, id: int, vo: VO, facility: Facility, name: str):
        super().__init__(id)
        self.vo = vo
        self.facility = facility
        self.name = name

    def __str__(self):
        return (
            f"id: {self.id} vo: {self.vo} facility: {self.facility} "
            f"name: {self.name}"
        )

    def __eq__(self, other):
        if isinstance(other, Resource):
            return (
                self.id == other.id
                and self.vo == other.vo
                and self.facility == other.facility
                and self.name == other.name
            )
        return False
