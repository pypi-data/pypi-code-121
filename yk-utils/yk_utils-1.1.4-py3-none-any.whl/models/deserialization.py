""" Deserialization Module """
import typing
import datetime
import sys
import six


def _deserialize(data, klass, from_db: bool = False):
    """Deserializes dict, list, str into an object.

    :param data: dict, list or str.
    :param klass: class literal, or string of class name.
    :param from_db: True if data is from the database.

    :return: object.
    """
    if data is None:
        return None

    if klass in six.integer_types or klass in (float, str, bool):
        return _deserialize_primitive(data, klass)
    elif klass == object:
        return _deserialize_object(data)
    elif klass == datetime.date:
        return deserialize_date(data)
    elif klass == datetime.datetime:
        return deserialize_datetime(data)
    elif (sys.version_info < (3, 7) and type(klass) == typing.GenericMeta) \
            or hasattr(klass, '__origin__'):  # pylint: disable=E1101
        if hasattr(klass, '__extra__'):
            if klass.__extra__ == list:
                return _deserialize_list(data, klass.__args__[0], from_db)
            if klass.__extra__ == dict:
                return _deserialize_dict(data, klass.__args__[1], from_db)
        else:
            if klass._name == 'List':
                return _deserialize_list(data, klass.__args__[0], from_db)
            if klass._name == 'Dict':
                return _deserialize_dict(data, klass.__args__[1], from_db)
    else:
        return deserialize_dbmodel(data, klass) if from_db else deserialize_model(data, klass)


def _deserialize_primitive(data, klass):
    """Deserializes to primitive type.

    :param data: data to deserialize.
    :param klass: class literal.

    :return: int, long, float, str, bool.
    :rtype: int | long | float | str | bool
    """
    try:
        value = klass(data)
    except UnicodeEncodeError:
        value = six.u(data)
    except TypeError:
        value = data
    return value


def _deserialize_object(value):
    """Return a original value.

    :return: object.
    """
    return value


def deserialize_date(string):
    """Deserializes string to date.

    :param string: str.
    :type string: str
    :return: date.
    :rtype: date
    """
    try:
        from dateutil.parser import parse
        return parse(string).date()
    except ImportError:
        return string


def deserialize_datetime(string):
    """Deserializes string to datetime.

    The string should be in iso8601 datetime format.

    :param string: str.
    :type string: str
    :return: datetime.
    :rtype: datetime
    """
    try:
        from dateutil.parser import parse
        return parse(string)
    except ImportError:
        return string


def deserialize_dbmodel(data, klass):
    """Deserializes list or dict to model.

    :param data: dict, list.
    :type data: dict | list
    :param klass: class literal.
    :return: model object.
    """
    instance = klass()

    if not instance.swagger_types_db:
        return data

    for attr, attr_type in six.iteritems(instance.swagger_types_db):
        if data is not None \
                and attr in data \
                and isinstance(data, (list, dict)):
            value = data[attr]
            setattr(instance, attr, _deserialize(value, attr_type, True))

    return instance


def deserialize_model(data, klass):
    """Deserializes list or dict to model.

    :param data: dict, list.
    :type data: dict | list
    :param klass: class literal.
    :return: model object.
    """
    instance = klass()

    if not instance.swagger_types:
        return data

    for attr, attr_type in six.iteritems(instance.swagger_types):
        attr_name = instance.attribute_map[attr] if instance.attribute_map else attr
        if data is not None \
                and attr_name in data \
                and isinstance(data, (list, dict)):
            value = data[attr_name]
            setattr(instance, attr, _deserialize(value, attr_type, False))

    return instance


def _deserialize_list(data, boxed_type, from_db: bool = False):
    """Deserializes a list and its elements.

    :param data: list to deserialize.
    :type data: list
    :param boxed_type: class literal.
    :param from_db: True if data is from the database.

    :return: deserialized list.
    :rtype: list
    """
    return [_deserialize(sub_data, boxed_type, from_db)
            for sub_data in data]


def _deserialize_dict(data, boxed_type, from_db: bool = False):
    """Deserializes a dict and its elements.

    :param data: dict to deserialize.
    :type data: dict
    :param boxed_type: class literal.
    :param from_db: True if data is from the database.

    :return: deserialized dict.
    :rtype: dict
    """
    return {k: _deserialize(v, boxed_type, from_db)
            for k, v in six.iteritems(data)}
