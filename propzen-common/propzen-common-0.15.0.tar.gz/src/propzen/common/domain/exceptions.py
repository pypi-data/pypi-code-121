class DomainBaseException(Exception):
    def __init__(self, service_code, type_code, exc_type='DomainException', message=None):
        self.service_code = service_code
        self.type_code = type_code
        self.exc_type = exc_type
        self.message = message
        super().__init__(self.message)

    @property
    def code(self):
        return f'{self.service_code}-{self.type_code}'


class DomainException(DomainBaseException):
    def __init__(self, service_code='0', type_code='0', exc_type='DomainException', message=None):
        super().__init__(service_code, type_code, exc_type, message)


class EntityNotFound(DomainBaseException):
    def __init__(self, service_code='0', type_code='1', exc_type='EntityNotFound', message=None):
        super().__init__(service_code, type_code, exc_type, message)
