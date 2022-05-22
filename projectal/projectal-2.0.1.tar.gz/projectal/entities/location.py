from datetime import datetime

from projectal.entity import Entity
from projectal import api


class Location(Entity):
    """
    Implementation of the [Location](https://projectal.com/docs/latest/#tag/Location) API.
    """
    _path = 'location'
    _name = 'LOCATION'

    @classmethod
    def calendar(cls, uuId, begin=None, until=None):
        """
        Get the location's calendar.
        `uuId`: The location `uuId`
        `begin`: Start date in `yyyy-MM-dd` format
        `until`: End date in `yyyy-MM-dd` format
        """
        if begin:
            begin = datetime.strptime(begin, '%Y-%m-%d').date()
        if until:
            until = datetime.strptime(until, '%Y-%m-%d').date()

        url = '/api/location/{}/calendar?'.format(uuId)
        params = []
        params.append('begin={}'.format(begin)) if begin else None
        params.append('until={}'.format(until)) if until else None
        url += '&'.join(params)

        return api.get(url)
