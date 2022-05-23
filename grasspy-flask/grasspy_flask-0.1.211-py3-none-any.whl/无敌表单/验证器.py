import ipaddress
import math
import re
import uuid

try:
    import email_validator
except ImportError:
    email_validator = None

从 wtforms.validators 导入 ValidationError, StopValidation

__all__ = (
    "〇需要数据",
    "需要数据",
    "〇电子邮箱",
    "电子邮箱",
    "〇等于",
    "等于",
    "IP地址",
    "ip地址",
    "〇需要输入",
    "需要输入",
    "〇长度",
    "长度",
    "〇数字范围",
    "数字范围",
    "〇可选",
    "可选",
    "〇正则表达式",
    "正则表达式",
    "URL",
    "url",
    "〇任何一个",
    "任何一个",
    "〇不在其中",
    "不在其中",
    "Mac地址",
    "mac地址",
    "UUID",
    "爻验证错误",
    "爻停止验证",
)

类 爻验证错误(ValidationError):
    """
    验证器验证输入失败时抛出.
    """

    # def __init__(self, 消息="", *args, **kwargs):
        # ValueError.__init__(self, 消息, *args, **kwargs)


class 爻停止验证(StopValidation):
    """
    致使验证链停止.

    如果抛出 爻停止验证, no more validators in the validation chain are
    called. If raised with a message, the message will be added to the errors
    list.
    """

    # def __init__(self, 消息="", *args, **kwargs):
        # Exception.__init__(self, 消息, *args, **kwargs)


class 〇等于:
    """
    Compares the values of two fields.

    :param fieldname:
        The name of the other field to compare to.
    :param message:
        Error message to raise in case of a validation error. Can be
        interpolated with `%(other_label)s` and `%(other_name)s` to provide a
        more helpful error.
    """

    def __init__(self, 字段名, 消息=None):
        self.字段名 = 字段名
        self.消息 = 消息

    def __call__(self, form, field):
        try:
            other = form[self.字段名]
        except KeyError as exc:
            raise 爻验证错误(
                field.gettext("Invalid field name '%s'.") % self.字段名
            ) from exc
        if field.data == other.data:
            return

        d = {
            "other_label": hasattr(other, "label")
            and other.label.text
            or self.字段名,
            "other_name": self.字段名,
        }
        消息 = self.消息
        if 消息 is None:
            消息 = field.gettext("Field must be equal to %(other_name)s.")

        raise 爻验证错误(消息 % d)


class 〇长度:
    """
    Validates the length of a string.

    :param min:
        The minimum required length of the string. If not provided, minimum
        length will not be checked.
    :param max:
        The maximum length of the string. If not provided, maximum length
        will not be checked.
    :param message:
        Error message to raise in case of a validation error. Can be
        interpolated using `%(min)d` and `%(max)d` if desired. Useful defaults
        are provided depending on the existence of min and max.

    When supported, sets the `minlength` and `maxlength` attributes on widgets.
    """

    def __init__(self, 最短=-1, 最长=-1, 消息=None):
        assert (
            最短 != -1 or 最长 != -1
        ), "必须指定 `最短` 和 `最长` 中的至少一个."
        assert 最长 == -1 or 最短 <= 最长, "`最短` 不能大于 `最长`."
        self.最短 = 最短
        self.最长 = 最长
        self.消息 = 消息
        self.field_flags = {}
        if self.最短 != -1:
            self.field_flags["minlength"] = self.最短
        if self.最长 != -1:
            self.field_flags["maxlength"] = self.最长

    def __call__(self, form, field):
        length = field.data and len(field.data) or 0
        if length >= self.最短 and (self.最长 == -1 or length <= self.最长):
            return

        if self.消息 is not None:
            消息 = self.消息

        elif self.最长 == -1:
            消息 = field.ngettext(
                "Field must be at least %(最短)d character long.",
                "Field must be at least %(最短)d characters long.",
                self.最短,
            )
        elif self.最短 == -1:
            消息 = field.ngettext(
                "Field cannot be longer than %(最长)d character.",
                "Field cannot be longer than %(最长)d characters.",
                self.最长,
            )
        elif self.最短 == self.最长:
            消息 = field.ngettext(
                "Field must be exactly %(最长)d character long.",
                "Field must be exactly %(最长)d characters long.",
                self.最长,
            )
        else:
            消息 = field.gettext(
                "Field must be between %(最短)d and %(最长)d characters long."
            )

        raise 爻验证错误(消息 % dict(最短=self.最短, 最长=self.最长, length=length))


class 〇数字范围:
    """
    Validates that a number is of a minimum and/or maximum value, inclusive.
    This will work with any comparable number type, such as floats and
    decimals, not just integers.

    :param min:
        The minimum required value of the number. If not provided, minimum
        value will not be checked.
    :param max:
        The maximum value of the number. If not provided, maximum value
        will not be checked.
    :param message:
        Error message to raise in case of a validation error. Can be
        interpolated using `%(min)s` and `%(max)s` if desired. Useful defaults
        are provided depending on the existence of min and max.

    When supported, sets the `min` and `max` attributes on widgets.
    """

    def __init__(self, 最小=None, 最大=None, 消息=None):
        self.最小 = 最小
        self.最大 = 最大
        self.消息 = 消息
        self.field_flags = {}
        if self.最小 is not None:
            self.field_flags["min"] = self.最小
        if self.最大 is not None:
            self.field_flags["max"] = self.最大

    def __call__(self, form, field):
        data = field.data
        if (
            data is not None
            and not math.isnan(data)
            and (self.最小 is None or data >= self.最小)
            and (self.最大 is None or data <= self.最大)
        ):
            return

        if self.消息 is not None:
            消息 = self.消息

        # we use %(最小)s interpolation to support floats, None, and
        # Decimals without throwing a formatting exception.
        elif self.最大 is None:
            消息 = field.gettext("Number must be at least %(最小)s.")

        elif self.最小 is None:
            消息 = field.gettext("Number must be at most %(最大)s.")

        else:
            消息 = field.gettext("Number must be between %(最小)s and %(最大)s.")

        raise 爻验证错误(消息 % dict(最小=self.最小, 最大=self.最大))


class 〇可选:
    """
    Allows empty input and stops the validation chain from continuing.

    If input is empty, also removes prior errors (such as processing errors)
    from the field.

    :param strip_whitespace:
        If True (the default) also stop the validation chain on input which
        consists of only whitespace.

    Sets the `optional` attribute on widgets.
    """

    def __init__(self, 去除空白=True):
        if 去除空白:
            self.string_check = lambda s: s.strip()
        else:
            self.string_check = lambda s: s

        self.field_flags = {"optional": True}

    def __call__(self, form, field):
        if (
            not field.raw_data
            or isinstance(field.raw_data[0], str)
            and not self.string_check(field.raw_data[0])
        ):
            field.errors[:] = []
            raise 爻停止验证()


class 〇需要数据:
    """
    Checks the field's data is 'truthy' otherwise stops the validation chain.

    This validator checks that the ``data`` attribute on the field is a 'true'
    value (effectively, it does ``if field.data``.) Furthermore, if the data
    is a string type, a string containing only whitespace characters is
    considered false.

    If the data is empty, also removes prior errors (such as processing errors)
    from the field.

    **NOTE** this validator used to be called `Required` but the way it behaved
    (requiring coerced data, not input data) meant it functioned in a way
    which was not symmetric to the `Optional` validator and furthermore caused
    confusion with certain fields which coerced data to 'falsey' values like
    ``0``, ``Decimal(0)``, ``time(0)`` etc. Unless a very specific reason
    exists, we recommend using the :class:`InputRequired` instead.

    :param message:
        Error message to raise in case of a validation error.

    Sets the `required` attribute on widgets.
    """

    def __init__(self, 消息=None):
        self.消息 = 消息
        self.field_flags = {"required": True}

    def __call__(self, form, field):
        if field.data and (not isinstance(field.data, str) or field.data.strip()):
            return

        if self.消息 is None:
            消息 = field.gettext("This field is required.")
        else:
            消息 = self.消息

        field.errors[:] = []
        raise 爻停止验证(消息)


class 〇需要输入:
    """
    Validates that input was provided for this field.

    Note there is a distinction between this and DataRequired in that
    InputRequired looks that form-input data was provided, and DataRequired
    looks at the post-coercion data.

    Sets the `required` attribute on widgets.
    """

    def __init__(self, 消息=None):
        self.消息 = 消息
        self.field_flags = {"required": True}

    def __call__(self, form, field):
        if field.raw_data and field.raw_data[0]:
            return

        if self.消息 is None:
            消息 = field.gettext("This field is required.")
        else:
            消息 = self.消息

        field.errors[:] = []
        raise 爻停止验证(消息)


class 〇正则表达式:
    """
    Validates the field against a user provided regexp.

    :param regex:
        The regular expression string to use. Can also be a compiled regular
        expression pattern.
    :param flags:
        The regexp flags to use, for example re.IGNORECASE. Ignored if
        `regex` is not a string.
    :param message:
        Error message to raise in case of a validation error.
    """

    def __init__(self, 正则式, 标志々=0, 消息=None):
        if isinstance(正则式, str):
            正则式 = re.compile(正则式, 标志々)
        self.正则式 = 正则式
        self.消息 = 消息

    def __call__(self, form, field, 消息=None):
        match = self.正则式.match(field.data or "")
        if match:
            return match

        if 消息 is None:
            if self.消息 is None:
                消息 = field.gettext("Invalid input.")
            else:
                消息 = self.消息

        raise 爻验证错误(消息)


class 〇电子邮箱:
    """
    Validates an email address. Requires email_validator package to be
    installed. For ex: pip install wtforms[email].

    :param message:
        Error message to raise in case of a validation error.
    :param granular_message:
        Use validation failed message from email_validator library
        (Default False).
    :param check_deliverability:
        Perform domain name resolution check (Default False).
    :param allow_smtputf8:
        Fail validation for addresses that would require SMTPUTF8
        (Default True).
    :param allow_empty_local:
        Allow an empty local part (i.e. @example.com), e.g. for validating
        Postfix aliases (Default False).
    """

    def __init__(
        self,
        消息=None,
        granular_message=False,
        check_deliverability=False,
        allow_smtputf8=True,
        allow_empty_local=False,
    ):
        if email_validator is None:  # pragma: no cover
            raise Exception("电子邮箱验证需要安装 'email_validator'.")
        self.消息 = 消息
        self.granular_message = granular_message
        self.check_deliverability = check_deliverability
        self.allow_smtputf8 = allow_smtputf8
        self.allow_empty_local = allow_empty_local

    def __call__(self, form, field):
        try:
            if field.data is None:
                raise email_validator.EmailNotValidError()
            email_validator.validate_email(
                field.data,
                check_deliverability=self.check_deliverability,
                allow_smtputf8=self.allow_smtputf8,
                allow_empty_local=self.allow_empty_local,
            )
        except email_validator.EmailNotValidError as e:
            消息 = self.消息
            if 消息 is None:
                if self.granular_message:
                    消息 = field.gettext(e)
                else:
                    消息 = field.gettext("Invalid email address.")
            raise 爻验证错误(消息) from e


class IP地址:
    """
    Validates an IP address.

    :param ipv4:
        If True, accept IPv4 addresses as valid (default True)
    :param ipv6:
        If True, accept IPv6 addresses as valid (default False)
    :param message:
        Error message to raise in case of a validation error.
    """

    def __init__(self, ipv4=True, ipv6=False, 消息=None):
        if not ipv4 and not ipv6:
            raise ValueError(
                "IP 地址验证器必须启用 ipv4 和 ipv6 中的至少一个."
            )
        self.ipv4 = ipv4
        self.ipv6 = ipv6
        self.消息 = 消息

    def __call__(self, form, field):
        value = field.data
        valid = False
        if value:
            valid = (self.ipv4 and self.check_ipv4(value)) or (
                self.ipv6 and self.check_ipv6(value)
            )

        if valid:
            return

        消息 = self.消息
        if 消息 is None:
            消息 = field.gettext("Invalid IP address.")
        raise 爻验证错误(消息)

    @classmethod
    def check_ipv4(cls, value):
        try:
            address = ipaddress.ip_address(value)
        except ValueError:
            return False

        if not isinstance(address, ipaddress.IPv4Address):
            return False

        return True

    检查ipv4 = check_ipv4

    @classmethod
    def check_ipv6(cls, value):
        try:
            address = ipaddress.ip_address(value)
        except ValueError:
            return False

        if not isinstance(address, ipaddress.IPv6Address):
            return False

        return True

    检查ipv6 = check_ipv6


class Mac地址(〇正则表达式):
    """
    Validates a MAC address.

    :param message:
        Error message to raise in case of a validation error.
    """

    def __init__(self, 消息=None):
        pattern = r"^(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}$"
        super().__init__(pattern, 消息=消息)

    def __call__(self, form, field):
        消息 = self.消息
        if 消息 is None:
            消息 = field.gettext("Invalid Mac address.")

        super().__call__(form, field, 消息)


class URL(〇正则表达式):
    """
    Simple regexp based url validation. Much like the email validator, you
    probably want to validate the url later by other means if the url must
    resolve.

    :param require_tld:
        If true, then the domain-name portion of the URL must contain a .tld
        suffix.  Set this to false if you want to allow domains like
        `localhost`.
    :param message:
        Error message to raise in case of a validation error.
    """

    def __init__(self, require_tld=True, 消息=None):
        正则式 = (
            r"^[a-z]+://"
            r"(?P<host>[^\/\?:]+)"
            r"(?P<port>:[0-9]+)?"
            r"(?P<path>\/.*?)?"
            r"(?P<query>\?.*)?$"
        )
        super().__init__(正则式, re.IGNORECASE, 消息)
        self.validate_hostname = 〇主机名验证(
            require_tld=require_tld, allow_ip=True
        )

    def __call__(self, form, field):
        消息 = self.消息
        if 消息 is None:
            消息 = field.gettext("Invalid URL.")

        match = super().__call__(form, field, 消息)
        if not self.validate_hostname(match.group("host")):
            raise 爻验证错误(消息)


class UUID:
    """
    Validates a UUID.

    :param message:
        Error message to raise in case of a validation error.
    """

    def __init__(self, 消息=None):
        self.消息 = 消息

    def __call__(self, form, field):
        消息 = self.消息
        if 消息 is None:
            消息 = field.gettext("Invalid UUID.")
        try:
            uuid.UUID(field.data)
        except ValueError as exc:
            raise 爻验证错误(消息) from exc


class 〇任何一个:
    """
    Compares the incoming data to a sequence of valid inputs.

    :param values:
        A sequence of valid inputs.
    :param message:
        Error message to raise in case of a validation error. `%(values)s`
        contains the list of values.
    :param values_formatter:
        Function used to format the list of values in the error message.
    """

    def __init__(self, 值々, 消息=None, 值格式化函数=None):
        self.值々 = 值々
        self.消息 = 消息
        if 值格式化函数 is None:
            值格式化函数 = self.default_values_formatter
        self.值格式化函数 = 值格式化函数

    def __call__(self, form, field):
        if field.data in self.值々:
            return

        消息 = self.消息
        if 消息 is None:
            消息 = field.gettext("Invalid value, must be one of: %(值々)s.")

        raise 爻验证错误(消息 % dict(值々=self.值格式化函数(self.值々)))

    @staticmethod
    def default_values_formatter(值々):
        return ", ".join(str(x) for x in 值々)


class 〇不在其中:
    """
    Compares the incoming data to a sequence of invalid inputs.

    :param values:
        A sequence of invalid inputs.
    :param message:
        Error message to raise in case of a validation error. `%(values)s`
        contains the list of values.
    :param values_formatter:
        Function used to format the list of values in the error message.
    """

    def __init__(self, 值々, 消息=None, 值格式化函数=None):
        self.值々 = 值々
        self.消息 = 消息
        if 值格式化函数 is None:
            值格式化函数 = self.default_values_formatter
        self.值格式化函数 = 值格式化函数

    def __call__(self, form, field):
        if field.data not in self.值々:
            return

        消息 = self.消息
        if 消息 is None:
            消息 = field.gettext("Invalid value, can't be any of: %(值々)s.")

        raise 爻验证错误(消息 % dict(值々=self.值格式化函数(self.值々)))

    @staticmethod
    def default_values_formatter(v):
        return ", ".join(str(x) for x in v)


class 〇主机名验证:
    """
    Helper class for checking hostnames for validation.

    This is not a validator in and of itself, and as such is not exported.
    """

    hostname_part = re.compile(r"^(xn-|[a-z0-9_]+)(-[a-z0-9_-]+)*$", re.IGNORECASE)
    tld_part = re.compile(r"^([a-z]{2,20}|xn--([a-z0-9]+-)*[a-z0-9]+)$", re.IGNORECASE)

    def __init__(self, require_tld=True, allow_ip=False):
        self.require_tld = require_tld
        self.allow_ip = allow_ip

    def __call__(self, hostname):
        if self.allow_ip and (
            IP地址.check_ipv4(hostname) or IP地址.check_ipv6(hostname)
        ):
            return True

        # Encode out IDNA hostnames. This makes further validation easier.
        try:
            hostname = hostname.encode("idna")
        except UnicodeError:
            pass

        # Turn back into a string in Python 3x
        if not isinstance(hostname, str):
            hostname = hostname.decode("ascii")

        if len(hostname) > 253:
            return False

        # Check that all labels in the hostname are valid
        parts = hostname.split(".")
        for part in parts:
            if not part or len(part) > 63:
                return False
            if not self.hostname_part.match(part):
                return False

        if self.require_tld and (len(parts) < 2 or not self.tld_part.match(parts[-1])):
            return False

        return True


电子邮箱 = 〇电子邮箱
等于 = 〇等于
ip地址 = IP地址
mac地址 = Mac地址
长度 = 〇长度
数字范围 = 〇数字范围
可选 = 〇可选
需要输入 = 〇需要输入
需要数据 = 〇需要数据
正则表达式 = 〇正则表达式
url = URL
任何一个 = 〇任何一个
不在其中 = 〇不在其中

