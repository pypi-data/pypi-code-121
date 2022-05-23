__all__ = 'RuntimeError'


class RuntimeError(Exception):

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
