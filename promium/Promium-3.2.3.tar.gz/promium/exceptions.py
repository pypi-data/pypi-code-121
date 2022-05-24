

class PromiumException(Exception):
    pass


class PromiumTimeout(PromiumException):
    def __init__(self, message="no error message", seconds=10, screen=None):
        self.message = f"{message} (waited {seconds} seconds)"
        if screen:
            self.message += "Screenshot: available via screen\n"
        super(PromiumTimeout, self).__init__(self.message)


class ElementLocationException(PromiumException):
    pass


class LocatorException(PromiumException):
    pass


class BrowserConsoleException(PromiumException):
    pass
