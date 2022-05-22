from projectal.entity import Entity


class Note(Entity):
    """
    Implementation of the [Note](https://projectal.com/docs/latest/#tag/Note) API.
    """
    _path = 'note'
    _name = 'NOTE'

    @classmethod
    def create(cls, holder, entity):
        """Create a Note

        `holder`: `uuId` of the owner

        `entity`: The fields of the entity to be created
        """
        holder = holder['uuId'] if isinstance(holder, dict) else holder
        params = "?holder=" + holder
        return super().create(entity, params)
