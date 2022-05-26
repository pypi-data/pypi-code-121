from perun.connector.models.MemberStatusEnum import MemberStatusEnum
from perun.connector.models.HasIdAbstract import HasIdAbstract
from perun.connector.models.VO import VO


class Member(HasIdAbstract):
    def __init__(self, id: int, vo: VO, status: str):
        super().__init__(id)
        self.vo = vo
        self.status = status

    def __str__(self):
        return f"id: {self.id} vo: {self.vo} status: {self.status.name}"

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value: str):
        valid_states = MemberStatusEnum.__members__

        if value.upper() not in valid_states:
            raise ValueError(f'"{value}" is not a valid state.')

        self._status = MemberStatusEnum[value.upper()]

    def __eq__(self, other):
        if isinstance(other, Member):
            return (
                self.id == other.id
                and self.vo == other.vo
                and self.status == other.status
            )
        return False
