from perun.connector.models.HasIdAbstract import HasIdAbstract


class VO(HasIdAbstract):
    def __init__(self, id: int, name: str, short_name: str):
        super().__init__(id)
        self.name = name
        self.short_name = short_name

    def __str__(self):
        return f"id: {self.id} name: {self.name} short_name: {self.short_name}"

    def __eq__(self, other):
        if isinstance(other, VO):
            return (
                self.id == other.id
                and self.name == other.name
                and self.short_name == other.short_name
            )
        return False
