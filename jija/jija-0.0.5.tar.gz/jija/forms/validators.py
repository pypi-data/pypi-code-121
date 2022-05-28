import datetime
import re

from jija.forms.exceptions import ValidationError


class Validator:
    @classmethod
    async def validate(cls, value, field):
        raise NotImplementedError()


class LengthMinValidator(Validator):
    @classmethod
    async def validate(cls, value, field):
        if field.min_length and len(value) < field.min_length:
            raise ValidationError(f'Строка должна быть больше {field.min_length} символов', value)

        return value


class LengthMaxValidator(Validator):
    @classmethod
    async def validate(cls, value, field):
        if field.max_length and len(value) > field.max_length:
            raise ValidationError(f'Строка должна быть больше {field.max_length} символов', value)

        return value


class RegexValidator(Validator):
    @classmethod
    async def validate(cls, value, field):
        if field.regex and not re.match(field.regex, value):
            raise ValidationError(f'Строка не соответствует шаблону', value)

        return value


class IntegerValidator(Validator):
    @classmethod
    async def validate(cls, value, field):
        try:
            return int(value)
        except ValueError:
            raise ValidationError('Поле должно быть числом', value)


class FloatValidator(Validator):
    @classmethod
    async def validate(cls, value, field):
        try:
            return float(value)
        except ValueError:
            raise ValidationError('Поле должно быть числом', value)


class RangeMinValidator(Validator):
    @classmethod
    async def validate(cls, value, field):
        if field.min_value and value < field.min_value:
            raise ValidationError(f'Число должна быть больше либо равно {field.min_value}', value)

        return value


class RangeMaxValidator(Validator):
    @classmethod
    async def validate(cls, value, field):
        if field.max_value and value > field.max_value:
            raise ValidationError(f'Число должно быть меньше либо равно {field.max_value}', value)

        return value


class DateValidator(Validator):
    @classmethod
    async def validate(cls, value, field):
        try:
            return datetime.datetime.strptime(value, '%Y-%m-%d')
        except ValueError:
            raise ValidationError('Неверный формат', value)


class OptionsValidator(Validator):
    @classmethod
    async def validate(cls, value, field):
        if value not in field.options:
            raise ValidationError(f'Недопустимое значение', value)

        return value
