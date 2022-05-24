"""
Fields classes.

author: Matthew Casey

&copy; [Digital Content Analysis Technology Ltd](https://www.d-cat.co.uk)
"""

from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta
import i18n
import json
from marshmallow import fields
import typing


#
# Groups together all the bespoke field types used by models so that they can be serialised appropriately to JSON and so that the validation errors are localised.
# All fields descend from Marshmallow fields.
#

class Boolean(fields.Boolean):
    """
    Defines a Boolean.
    """

    # Localised validation errors.
    default_error_messages = {'invalid': i18n.t('models.fields.boolean.invalid')}


class DateTime(fields.DateTime):
    """
    Defines a datetime.
    """

    # Localised validation errors.
    default_error_messages = {'invalid': i18n.t('models.fields.datetime.invalid'), 'invalid_awareness': i18n.t('models.fields.datetime.invalid_awareness'),
                              'format': i18n.t('models.fields.datetime.format'), }

    def _serialize(self, value, attr, obj, **kwargs):
        """
        Overrides the serialization. This is because when a nested model is validated, it may be passed as a string already (from an update), instead of a datetime.

        Args:
            value: The value to serialize.
            attr: The attribute/key in `data` to deserialize.
            obj: The associated object.
            kwargs: Field-specific keyword arguments.

        Returns:
            The serialised datetime.
        """

        if isinstance(value, str):
            return value

        # Note that if the datetime does not have a timezone, we enforce UTC. See also utilities#json_default.
        value = value.astimezone(timezone.utc) if isinstance(value, datetime) and (value.tzinfo is None) else value
        return super(DateTime, self)._serialize(value, attr, obj, **kwargs)

    def _deserialize(self, value, attr, data, **kwargs):
        """
        Overrides the deserialization. This is because when a model is validated, it uses deserialization to validate the values. However,
        because the datetime is native, and not a string, the validation fails. We therefore pass the validation if the value is already a
        datetime.

        Args:
            value: The value to deserialize.
            attr: The attribute/key in `data` to deserialize.
            data: The raw input data passed to `Schema.load`.
            kwargs: Field-specific keyword arguments.

        Raises:
            ValidationError: If an invalid value is passed or if a required value is missing.
        """
        if not value:
            return None

        if value and isinstance(value, datetime):
            return value

        return super(DateTime, self)._deserialize(value, attr, data, **kwargs)


class Decimal(fields.Decimal):
    """
    Defines a decimal value.
    """

    # Localised validation errors.
    default_error_messages = {'invalid': i18n.t('models.fields.decimal.invalid'), 'too_large': i18n.t('models.fields.decimal.too_large'),
                              'special': i18n.t('models.fields.decimal.special')}


class Dict(fields.Dict):
    """
    Defines a dictionary.
    """

    # Localised validation errors.
    default_error_messages = {'invalid': i18n.t('models.fields.dict.invalid')}


class Email(fields.Email):
    """
    Defines an email.
    """

    # Localised validation errors.
    default_error_messages = {'invalid': i18n.t('models.fields.email.invalid')}


class Float(fields.Float):
    """
    Defines a float.
    """

    # Localised validation errors.
    default_error_messages = {'invalid': i18n.t('models.fields.float.invalid'), 'too_large': i18n.t('models.fields.float.too_large'),
                              'special': i18n.t('models.fields.float.special')}


class Integer(fields.Integer):
    """
    Defines an integer.
    """

    # Localised validation errors.
    default_error_messages = {'invalid': i18n.t('models.fields.integer.invalid'), 'too_large': i18n.t('models.fields.integer.too_large')}


class IP(fields.IP):
    """
    Defines an IP address.
    """

    # Localised validation errors.
    default_error_messages = {'invalid_ip': i18n.t('models.fields.ip.invalid_ip')}


class List(fields.List):
    """
    Defines a list of other fields.
    """

    # Localised validation errors.
    default_error_messages = {'invalid': i18n.t('models.fields.list.invalid')}


class Nested(fields.Nested):
    """
    Defines a nested field with its own schema.
    """

    # Localised validation errors.
    default_error_messages = {'type': i18n.t('models.fields.nested.type')}


class RelativeDelta(fields.Field):
    """
    A relative delta field. Represents a relative datetime.
    """

    # Localised validation errors.
    default_error_messages = {'invalid': i18n.t('models.fields.relativedelta.invalid')}

    def _deserialize(self, value, attr, data, **kwargs):
        """
        Deserializes the field.

        Args:
            value: The value of the field.
            attr: The attribute. Not used.
            data: The data. Not used.
            kwargs: The additional keyword arguments. Not used.

        Returns:
            The serialized value or None if the value is None.
        """

        if not value:
            return None

        if value and isinstance(value, relativedelta):
            return value

        if not isinstance(value, (str, bytes)):
            raise self.make_error('invalid')

        # Attempt to parse the string.
        try:
            dictionary = json.loads(value)
            years = dictionary.get('years', 0) if dictionary.get('years', 0) is not None else 0
            months = dictionary.get('months', 0) if dictionary.get('months', 0) is not None else 0
            days = dictionary.get('days', 0) if dictionary.get('days', 0) is not None else 0
            leapdays = dictionary.get('leapdays', 0) if dictionary.get('leapdays', 0) is not None else 0
            weeks = dictionary.get('weeks', 0) if dictionary.get('weeks', 0) is not None else 0
            hours = dictionary.get('hours', 0) if dictionary.get('hours', 0) is not None else 0
            minutes = dictionary.get('minutes', 0) if dictionary.get('minutes', 0) is not None else 0
            seconds = dictionary.get('seconds', 0) if dictionary.get('seconds', 0) is not None else 0
            microseconds = dictionary.get('microseconds', 0) if dictionary.get('microseconds', 0) is not None else 0

            return relativedelta(years=years, months=months, days=days, leapdays=leapdays, weeks=weeks, hours=hours, minutes=minutes, seconds=seconds,
                                 microseconds=microseconds, year=dictionary.get('year'), month=dictionary.get('month'), day=dictionary.get('day'),
                                 weekday=dictionary.get('weekday'), hour=dictionary.get('hour'), minute=dictionary.get('minute'), second=dictionary.get('second'),
                                 microsecond=dictionary.get('microsecond'))

        except Exception as error:
            raise self.make_error('invalid') from error

    def _serialize(self, value, attr, obj, **kwargs):
        """
        Serializes the field.

        Args:
            value: The value of the field.
            attr: The attribute. Not used.
            obj: The object. Not used.
            kwargs: The additional keyword arguments. Not used.

        Returns:
            The serialized value or None if the value is None.
        """

        if value is None:
            return None

        # Create a string representation of the relativedelta which can be parsed.
        dictionary = {'years': value.years, 'months': value.months, 'days': value.days, 'leapdays': value.leapdays, 'weeks': value.weeks, 'hours': value.hours,
                      'minutes': value.minutes, 'seconds': value.seconds, 'microseconds': value.microseconds, 'year': value.year, 'month': value.month,
                      'day': value.day, 'weekday': value.weekday, 'hour': value.hour, 'minute': value.minute, 'second': value.second,
                      'microsecond': value.microsecond}

        return json.dumps(dictionary)


class String(fields.String):
    """
    Defines a String.
    """

    # Localised validation errors.
    default_error_messages = {'invalid': i18n.t('models.fields.string.invalid'), 'invalid_utf8': i18n.t('models.fields.string.invalid_utf8')}

    def deserialize(self, value: typing.Any, attr: str = None, data: typing.Mapping[str, typing.Any] = None, **kwargs):
        """
        Deserializes a value. This method is overridden to replace empty strings with None when allowed.

        Args:
            value: The value to deserialize.
            attr: The attribute/key in `data` to deserialize.
            data: The raw input data passed to `Schema.load`.
            kwargs: Field-specific keyword arguments.

        Raises:
            ValidationError: If an invalid value is passed or if a required value is missing.
        """
        if (value is not None) and isinstance(value, str) and (len(value) <= 0) and self.allow_none:
            value = None

        return super(String, self).deserialize(value, attr, data, **kwargs)


class TimeDelta(fields.Field):
    """
    Defines a time delta. Note that we do not use the base TimeDelta class as it assumes seconds as a precision and does not allow any flexibility.
    """

    # Localised validation errors.
    default_error_messages = {'invalid': i18n.t('models.fields.timedelta.invalid')}

    def _deserialize(self, value, attr, data, **kwargs):
        """
        Deserializes the field.

        Args:
            value: The value of the field.
            attr: The attribute. Not used.
            data: The data. Not used.
            kwargs: The additional keyword arguments. Not used.

        Returns:
            The serialized value or None if the value is None.
        """

        if not value:
            return None

        if value and isinstance(value, timedelta):
            return value

        if not isinstance(value, (str, bytes)):
            raise self.make_error('invalid')

        # Attempt to parse the string.
        try:
            dictionary = json.loads(value)
            days = dictionary.get('days', 0) if dictionary.get('days', 0) is not None else 0
            seconds = dictionary.get('seconds', 0) if dictionary.get('seconds', 0) is not None else 0
            microseconds = dictionary.get('microseconds', 0) if dictionary.get('microseconds', 0) is not None else 0

            return timedelta(days=days, seconds=seconds, microseconds=microseconds)

        except Exception as error:
            raise self.make_error('invalid') from error

    def _serialize(self, value, attr, obj, **kwargs):
        """
        Serializes the field.

        Args:
            value: The value of the field.
            attr: The attribute. Not used.
            obj: The object. Not used.
            kwargs: The additional keyword arguments. Not used.

        Returns:
            The serialized value or None if the value is None.
        """

        if value is None:
            return None

        # Create a string representation of the timedelta which can be parsed.
        dictionary = {'days': value.days, 'seconds': value.seconds, 'microseconds': value.microseconds}

        return json.dumps(dictionary)


class Tuple(fields.Tuple):
    """
    Defines a tuple of other fields.
    """

    # Localised validation errors.
    default_error_messages = {'invalid': i18n.t('models.fields.tuple.invalid')}


class Url(fields.Url):
    """
    Defines a URL by enhancing the Marshmallow URL field.
    """
    default_error_messages = {'invalid': i18n.t('models.fields.url.invalid_url')}


class UUID(fields.UUID):
    """
    Defines a UUID by enhancing the Marshmallow UUID field.
    """

    # Localised validation errors.
    default_error_messages = {'invalid_uuid': i18n.t('models.fields.uuid.invalid_uuid')}
