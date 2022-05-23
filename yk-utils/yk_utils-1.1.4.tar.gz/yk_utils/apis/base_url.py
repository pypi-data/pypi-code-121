"""Base URL module.
"""


class BaseUrl:
    """Manage YooniK API base URL."""
    @classmethod
    def set(cls, base_url: str):
        """
        Sets a base URL
        :param base_url: base URL
        :return:
        """
        if not base_url.endswith('/'):
            base_url += '/'
        cls.base_url = base_url

    @classmethod
    def get(cls) -> str:
        """
        Gets the stored base URL
        :return: stored base URL
        """
        if not hasattr(cls, 'base_url'):
            cls.base_url = None
        return cls.base_url
