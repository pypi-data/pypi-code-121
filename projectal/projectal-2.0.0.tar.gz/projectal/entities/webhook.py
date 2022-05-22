from projectal import api
from projectal.entity import Entity


class Webhook(Entity):
    """
    Implementation of the [Webhook](https://projectal.com/docs/latest/#tag/Webhook) API.
    """
    _path = 'webhook'
    _name = 'WEBHOOK'

    @classmethod
    def list(cls, start=0, limit=101, ksort='entity', order='asc'):
        """
        Get a list of registered webhooks.

        Optionally specify a range for pagination.
        """
        url = '/api/webhook/list?start={}&limit={}&ksort={}&order={}'.\
                  format(start, limit, ksort, order)
        return api.get(url)
