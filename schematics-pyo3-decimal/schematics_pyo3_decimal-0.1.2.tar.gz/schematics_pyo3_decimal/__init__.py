"""schematics_pyo3_decimal - """
from pyo3_decimal import Decimal
from schematics.exceptions import ValidationError
from schematics.types import BaseType

__version__ = '0.1.0'
__author__ = 'fx-kirin <fx.kirin@gmail.com>'
__all__: list = []


class DecimalType(BaseType):
    def validate_decimal(self, value):
        if not isinstance(value, Decimal):
            raise ValidationError("value must be decimal.")

    def to_primitive(self, value, context):
        return value.mantissa() * 100_000 * pow(10, -value.scale())
