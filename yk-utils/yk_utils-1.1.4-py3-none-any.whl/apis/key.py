"""API subscription Key module.
"""


class Key:
    """Manage YooniK API Subscription Key."""
    @classmethod
    def set(cls, key: str):
        """Set the Subscription Key.
        :param key:
        :return:
        """
        cls.key = key

    @classmethod
    def get(cls) -> str:
        """Get the Subscription Key.
        :return:
        """
        if not hasattr(cls, 'key'):
            cls.key = None
        return cls.key
