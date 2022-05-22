from projectal.entity import Entity
from projectal import api


class Contact(Entity):
    """
    Implementation of the [Contact](https://projectal.com/docs/latest/#tag/Contact) API.
    """
    _path = 'contact'
    _name = 'CONTACT'

    @classmethod
    def create(cls, holder, entity):
        """Create a Contact

        `holder`: `uuId` of the owner

        `entity`: The fields of the entity to be created
        """
        params = "?holder=" + holder
        return super().create(entity, params)

    @classmethod
    def clone(cls, uuId, holder, entity):
        url = '/api/contact/clone?holder={}&reference={}'.format(holder, uuId)
        response = api.post(url, entity)
        return response['jobClue']['uuId']
