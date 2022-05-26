class BadRequestException(Exception):
    def __init__(self, status_code, message=None):
        super(BadRequestException, self).__init__()
        self.status_code = status_code
        self.message = message

    def __str__(self):
        return self.message

    def __repr__(self):
        return self.message


class ConfigurationException(Exception):
    def __init__(self, message=None):
        super(ConfigurationException, self).__init__()
        self.message = message

    def __str__(self):
        return self.message

    def __repr__(self):
        return self.message
