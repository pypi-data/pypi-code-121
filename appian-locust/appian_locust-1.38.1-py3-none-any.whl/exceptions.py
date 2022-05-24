class BadCredentialsException(Exception):
    def __init__(self) -> None:
        super(Exception, self).__init__("Could not log in, check the credentials")


class MissingCsrfTokenException(Exception):
    def __init__(self, found_cookies: dict) -> None:
        super(Exception, self).__init__(
            f"Login unsuccessful, no multipart cookie found, only found {found_cookies}, make sure credentials are correct")


class MissingConfigurationException(Exception):
    def __init__(self, missing_keys: list) -> None:
        super(Exception, self).__init__(
            f'Missing keys in configuration file, please verify that all of the following exist and are correct: {missing_keys}')


class ComponentNotFoundException(Exception):
    pass


class InvalidComponentException(Exception):
    pass


class ChoiceNotFoundException(Exception):
    pass
