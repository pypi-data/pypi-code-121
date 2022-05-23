import datetime

from wtforms import widgets
from .核心 import 〇字段
from wtforms.utils import clean_datetime_format_for_strptime

__all__ = (
    "〇日时字段",
    "〇日期字段",
    "〇时间字段",
    "〇月份字段",
    "〇本地日时字段",
)


class 〇日时字段(〇字段):
    """
    A text field which stores a :class:`datetime.datetime` matching one or
    several formats. If ``format`` is a list, any input value matching any
    format will be accepted, and the first format in the list will be used
    to produce HTML values.
    """

    widget = widgets.DateTimeInput()

    def __init__(
        self, 标签=None, 验证器々=None, 格式="%Y-%m-%d %H:%M:%S", **kwargs
    ):
        super().__init__(标签, 验证器々, **kwargs)
        self.format = 格式 if isinstance(格式, list) else [格式]
        self.strptime_format = clean_datetime_format_for_strptime(self.format)

    def _value(self):
        if self.raw_data:
            return " ".join(self.raw_data)
        return self.data and self.data.strftime(self.format[0]) or ""

    def process_formdata(self, valuelist):
        if not valuelist:
            return

        date_str = " ".join(valuelist)
        for format in self.strptime_format:
            try:
                self.data = datetime.datetime.strptime(date_str, format)
                return
            except ValueError:
                self.data = None

        raise ValueError(self.gettext("Not a valid datetime value."))


class 〇日期字段(〇日时字段):
    """
    Same as :class:`~wtforms.fields.DateTimeField`, except stores a
    :class:`datetime.date`.
    """

    widget = widgets.DateInput()

    def __init__(self, 标签=None, 验证器々=None, 格式="%Y-%m-%d", **kwargs):
        super().__init__(标签, 验证器々, 格式, **kwargs)

    def process_formdata(self, valuelist):
        if not valuelist:
            return

        date_str = " ".join(valuelist)
        for format in self.strptime_format:
            try:
                self.data = datetime.datetime.strptime(date_str, format).date()
                return
            except ValueError:
                self.data = None

        raise ValueError(self.gettext("Not a valid date value."))


class 〇时间字段(〇日时字段):
    """
    Same as :class:`~wtforms.fields.DateTimeField`, except stores a
    :class:`datetime.time`.
    """

    widget = widgets.TimeInput()

    def __init__(self, 标签=None, 验证器々=None, 格式="%H:%M", **kwargs):
        super().__init__(标签, 验证器々, 格式, **kwargs)

    def process_formdata(self, valuelist):
        if not valuelist:
            return

        time_str = " ".join(valuelist)
        for format in self.strptime_format:
            try:
                self.data = datetime.datetime.strptime(time_str, format).time()
                return
            except ValueError:
                self.data = None

        raise ValueError(self.gettext("Not a valid time value."))


class 〇月份字段(〇日期字段):
    """
    Same as :class:`~wtforms.fields.DateField`, except represents a month,
    stores a :class:`datetime.date` with `day = 1`.
    """

    widget = widgets.MonthInput()

    def __init__(self, 标签=None, 验证器々=None, 格式="%Y-%m", **kwargs):
        super().__init__(标签, 验证器々, 格式, **kwargs)


class 〇本地日时字段(〇日时字段):
    """
    Same as :class:`~wtforms.fields.DateTimeField`, but represents an
    ``<input type="datetime-local">``.
    """

    widget = widgets.DateTimeLocalInput()

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("格式", ["%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"])
        super().__init__(*args, **kwargs)
