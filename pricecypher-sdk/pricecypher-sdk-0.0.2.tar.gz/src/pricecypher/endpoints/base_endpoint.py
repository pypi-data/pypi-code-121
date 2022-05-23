from typing import Union
from better_abc import ABCMeta, abstract_attribute


class BaseEndpoint(metaclass=ABCMeta):
    base_url: str = abstract_attribute()

    def _url(self, path: Union[None, str, list[str]] = None):
        """
        Get URL composed of the base URL in this endpoint with the given path appended.

        :param None or str or list[str] path: path or path components to append to the base URL.
        :return: Base URL with given path appended. Different path components will be joined using a '/'.
        :rtype: str
        """
        if path is None:
            return self.base_url
        if type(path) is list:
            path = '/'.join(str(s).strip('/') for s in path)
        else:
            path = path.strip('/')
        return '{}/{}'.format(self.base_url.strip('/'), path)
