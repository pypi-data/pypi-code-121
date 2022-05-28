class ValidationError(Exception):
    def __init__(self, error, value):
        self.error = error
        self.value = value
