
from django.conf import settings
from django.forms import DateInput


class DatePickerInput(DateInput):

    def __init__(self, attrs=None, format=None):

        if format is None:
            format = settings.DATE_INPUT_FORMATS[0]

        if attrs is None:
            attrs = {}

        attrs['data-role'] = 'datepicker'

        super().__init__(attrs=attrs, format=format)
