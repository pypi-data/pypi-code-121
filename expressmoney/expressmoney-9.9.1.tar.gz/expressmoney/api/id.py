"""
 Microservice endpoint identifier
"""
__all__ = ('ID',)


class ID:
    """Base microservice endpoint identifier"""
    _service = None
    _app = None
    _view_set = None

    def __init__(self):
        self._lookup_field_value = None
        super().__init__()

    @property
    def id(self):
        return f'{self.service}_{self._app}_{self._view_set}'

    @property
    def path(self):
        result = f'/{self._app}' if self._view_set is None else f'/{self._app}/{self._view_set}'
        result = result if self._lookup_field_value is None else f'{result}/{self._lookup_field_value}'
        return result

    @property
    def service(self):
        return self._service

    @property
    def lookup_field_value(self):
        return self._lookup_field_value

    @lookup_field_value.setter
    def lookup_field_value(self, value):
        self._lookup_field_value = value
