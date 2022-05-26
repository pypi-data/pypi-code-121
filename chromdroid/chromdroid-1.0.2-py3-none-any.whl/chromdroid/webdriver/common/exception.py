class WebDriverException(Exception):
    pass


class NoSuchElementException(WebDriverException):
    pass


class NoSuchPageSourceException(WebDriverException):
    pass


class InvalidElementStateException(WebDriverException):
    pass


class ApplicationClosed(WebDriverException):
    pass
