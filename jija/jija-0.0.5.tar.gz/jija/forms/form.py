import inspect

from jija.forms import fields
from jija.forms.exceptions import ValidationError


class Form:
    def __init__(self, data=None):
        self.data = data or {}
        self.errors = {}

        self.__valid = None

    async def validate(self):
        for name, obj in self.__class__.__dict__.items():
            if issubclass(type(obj), fields.Field):
                try:
                    self.data[name] = await obj.validate(self.data.get(name))

                except ValidationError as exception:
                    self.errors[name] = exception.error
                    self.data[name] = exception.value

        if inspect.iscoroutinefunction(self.clean):
            await self.clean()
        else:
            self.clean()

        self.__valid = len(self.errors) == 0
        if not self.__valid:
            print(self.errors)

        return self.__valid

    @property
    def valid(self):
        return self.__valid

    def clean(self):
        pass
