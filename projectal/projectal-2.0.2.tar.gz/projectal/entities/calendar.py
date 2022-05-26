from projectal.errors import UnsupportedException

from projectal.entity import Entity


class Calendar(Entity):
    """
    Implementation of the [Calendar](https://projectal.com/docs/latest/#tag/Calendar) API.
    """
    _path = 'calendar'
    _name = 'CALENDAR'

    @classmethod
    def create(cls, holder, entity):
        """Create a Calendar

        `holder`: `uuId` of the owner

        `entity`: The fields of the entity to be created
        """
        params = "?holder=" + holder
        return super().create(entity, params)

    @classmethod
    def list(cls, expand=False, links=None):
        raise UnsupportedException("Calendar list is not supported by the API.")
