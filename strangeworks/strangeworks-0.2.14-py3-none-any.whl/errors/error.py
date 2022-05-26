from __future__ import annotations


class StrangeworksError(Exception):
    """
    This is the standard Strangeworks exception type utilized
    in both API responses to errors or from the SDK implementation
    when a known error is captured.
    """

    def __init__(
        self,
        message: str = "",
        help_page_url: str = "",
    ):
        self.message = message
        self.help_page_url = help_page_url
        super().__init__(self.message)

    @classmethod
    def authentication_error(cls, message: str = None, help_page_url: str = None):
        return cls.__builder(
            message=message,
            default_message="authentication is invalid, utilize client.authenticate() to refresh",
            help_page_url=help_page_url,
        )

    @classmethod
    def invalid_argument(cls, message: str = None, help_page_url: str = None):
        return cls.__builder(
            message=message,
            default_message="invalid argument provided",
            help_page_url=help_page_url,
        )

    @classmethod
    def not_implemented(cls, help_page_url: str = None):
        return cls.__builder(
            message="This feature is not yet implemented",
            help_page_url=help_page_url,
        )

    @classmethod
    def timeout(cls, message: str = None, help_page_url: str = None):
        return cls.__builder(
            default_message="Timeout attempting request",
            message=message,
            help_page_url=help_page_url,
        )

    @classmethod
    def bad_response(cls, message: str = "", help_page_url: str = None):
        """TODO: should replace this with many constructors based on codes and correlated help pages"""
        return cls.__builder(
            message=message,
            default_message="invalid response from server",
            help_page_url=help_page_url,
        )

    @classmethod
    def __builder(
        cls,
        message: str = None,
        help_page_url: str = None,
        default_message: str = "",
        default_help_page_url: str = "",
    ):
        if message is None:
            message = default_message
        sw = StrangeworksError(message)
        sw.help_page_url = help_page_url
        if help_page_url is None:
            sw.help_page_url = default_help_page_url
        return sw
