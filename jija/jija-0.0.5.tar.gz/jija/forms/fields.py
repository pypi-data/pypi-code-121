from jija.forms.validators import *
from jija.forms.exceptions import ValidationError


class Field:
    validators = ()

    def __init__(self, *, required=True, default=None):
        self.required = required
        self.default = default

    async def validate(self, value):
        if not value:
            if self.required:
                raise ValidationError('Обязательное поле', value)
            else:
                return value

        for validator in self.validators:
            value = await validator.validate(value, self)

        return value


class CharField(Field):
    validators = (LengthMinValidator, LengthMaxValidator)

    def __init__(self, *, min_length=None, max_length=None, regex=None, **kwargs):
        super().__init__(**kwargs)
        self.min_length = min_length
        self.max_length = max_length
        self.regex = regex


class NumericField(Field):
    def __init__(self, *, min_value=None, max_value=None, **kwargs):
        super().__init__(**kwargs)
        self.min_value = min_value
        self.max_value = max_value


class IntegerField(NumericField):
    validators = (IntegerValidator, RangeMinValidator, RangeMaxValidator)


class FloatField(NumericField):
    validators = (FloatValidator, RangeMinValidator, RangeMaxValidator)


class DateField(Field):
    validators = (DateValidator, RangeMinValidator, RangeMaxValidator)

    def __init__(self, *, min_value=None, max_value=None, **kwargs):
        super().__init__(**kwargs)
        self.min_value = min_value
        self.max_value = max_value


class SelectField(Field):
    validators = (OptionsValidator,)

    def __init__(self, *, options, **kwargs):
        super().__init__(**kwargs)
        self.options = options
