从 wtforms 导入 widgets
从 .核心 导入 〇字段

__all__ = (
    "〇布尔型字段",
    "〇文本域字段",
    "〇密码字段",
    "〇文件字段",
    "〇多文件字段",
    "〇隐藏字段",
    "〇搜索字段",
    "〇提交字段",
    "〇字符串字段",
    "〇电话字段",
    "URL字段",
    "〇电子邮箱字段",
)


class 〇布尔型字段(〇字段):
    """
    Represents an ``<input type="checkbox">``. Set the ``checked``-status by using the
    ``default``-option. Any value for ``default``, e.g. ``default="checked"`` puts
    ``checked`` into the html-element and sets the ``data`` to ``True``

    :param false_values:
        If provided, a sequence of strings each of which is an exact match
        string of what is considered a "false" value. Defaults to the tuple
        ``(False, "false", "")``
    """

    widget = widgets.CheckboxInput()
    false_values = (False, "false", "")

    def __init__(self, 标签=None, 验证器々=None, 假值々=None, **kwargs):
        super().__init__(标签, 验证器々, **kwargs)
        if 假值々 is not None:
            self.false_values = 假值々

    def process_data(self, value):
        self.data = bool(value)

    def process_formdata(self, valuelist):
        if not valuelist or valuelist[0] in self.false_values:
            self.data = False
        else:
            self.data = True

    def _value(self):
        if self.raw_data:
            return str(self.raw_data[0])
        return "y"


class 〇字符串字段(〇字段):
    """
    This field is the base for most of the more complicated fields, and
    represents an ``<input type="text">``.
    """

    widget = widgets.TextInput()

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = valuelist[0]

    def _value(self):
        return str(self.data) if self.data is not None else ""


class 〇文本域字段(〇字符串字段):
    """
    This field represents an HTML ``<textarea>`` and can be used to take
    multi-line input.
    """

    widget = widgets.TextArea()


class 〇密码字段(〇字符串字段):
    """
    A StringField, except renders an ``<input type="password">``.

    Also, whatever value is accepted by this field is not rendered back
    to the browser like normal fields.
    """

    widget = widgets.PasswordInput()


class 〇文件字段(〇字段):
    """Renders a file upload field.

    By default, the value will be the filename sent in the form data.
    WTForms **does not** deal with frameworks' file handling capabilities.
    A WTForms extension for a framework may replace the filename value
    with an object representing the uploaded data.
    """

    widget = widgets.FileInput()

    def _value(self):
        # browser ignores value of file input for security
        return False


class 〇多文件字段(〇文件字段):
    """A :class:`FileField` that allows choosing multiple files."""

    widget = widgets.FileInput(multiple=True)

    def process_formdata(self, valuelist):
        self.data = valuelist


class 〇隐藏字段(〇字符串字段):
    """
    HiddenField is a convenience for a StringField with a HiddenInput widget.

    It will render as an ``<input type="hidden">`` but otherwise coerce to a string.
    """

    widget = widgets.HiddenInput()


class 〇提交字段(〇布尔型字段):
    """
    Represents an ``<input type="submit">``.  This allows checking if a given
    submit button has been pressed.
    """

    widget = widgets.SubmitInput()


class 〇搜索字段(〇字符串字段):
    """
    Represents an ``<input type="search">``.
    """

    widget = widgets.SearchInput()


class 〇电话字段(〇字符串字段):
    """
    Represents an ``<input type="tel">``.
    """

    widget = widgets.TelInput()


class URL字段(〇字符串字段):
    """
    Represents an ``<input type="url">``.
    """

    widget = widgets.URLInput()


class 〇电子邮箱字段(〇字符串字段):
    """
    Represents an ``<input type="email">``.
    """

    widget = widgets.EmailInput()
