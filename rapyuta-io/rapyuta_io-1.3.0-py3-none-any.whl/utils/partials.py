from abc import abstractmethod


class PartialMixin(object):
    """
    Mixin to be used for API resource objects that have a partial set of fields in their list API, and a full set of
    fields in the get API.
    """

    PARTIAL_ATTR = '_is_partial'

    @property
    def is_partial(self):
        """
        :return: Is it a partial resource?
        :rtype: bool
        """
        return getattr(self, self.PARTIAL_ATTR, True)  # default=True: safer to assume partial resource

    @is_partial.setter
    def is_partial(self, value):
        setattr(self, self.PARTIAL_ATTR, value)

    @abstractmethod
    def refresh(self):
        """
        Fetches the updated resource from the server, and adds/updates object attributes based on it.

        :raises: :py:class:`~utils.error.APIError`: If the api returns an error, the status code is
            anything other than 200/201
        """
        raise NotImplementedError
