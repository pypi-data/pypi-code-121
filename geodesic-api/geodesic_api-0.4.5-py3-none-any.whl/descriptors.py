"""
This contains all of the Descriptor objects we'll will use to compose the
basic classes that inherit from geodesic.bases.APIObject. The follow the
pattern <Name>Descr. Rather than simply being namespaced here, the Descr
suffix will allow them to be aligned with other objects that will be
implemented as descriptors, such as AssetSpec and Project, and such.
These, by necessity need to be implemented in separate packages and
this convention will keep things internally consistent.
"""


import datetime
import re
from typing import Union
from urllib.parse import urlparse
import numpy as np
import pytz
from shapely.geometry import shape, box
from shapely.geometry.base import BaseGeometry
from shapely.wkb import loads as loads_wkb
from shapely.wkt import loads as loads_wkt
from dateutil.parser import isoparse

from geodesic.utils import datetime_to_utc


class BaseDescr:
    """base functionality of Descriptor objects for us with APIObject

    BaseDescr adds the basic functionality we use such as the attribute name and the private_name,
    which is prefixed by an "_"
    """
    def __init__(self, nested: str = None, doc: str = None, default=None, dict_name=None):
        """
        Args:
            nested: a subfield in the object's dict to retrieve this out of. A json path, separated by '.'.
                only object paths are supported, not full JSON paths such as list indices or wildcards
            doc: a custom docstring to override the default field descriptor docstring.
            default: a default value for this field
            dict_name: if the attribute name needs to be different than the name in the dictionary, it can be set
                with this. (example: `object_class` -> `class` since `class` is a reserved word)
        """
        if nested is not None:
            self.nested = nested.split('.')
        else:
            self.nested = None
        self.doc = doc
        self.default = default
        self.dict_name = dict_name

    def __set_name__(self, owner: object, name: str):
        self.public_name = name
        self.private_name = "_" + name
        if self.dict_name is None:
            self.dict_name = self.public_name
        if self.doc is not None:
            attr = getattr(owner, name)

            new_doc = self.doc
            doc = getattr(attr, '__doc__')
            if doc is not None:
                new_doc += "\n\nDescriptor:\n" + doc

            setattr(attr, '__doc__', new_doc)

    def __get__(self, obj: object, objtype=None) -> object:
        if obj is None:
            return self
        return self._get(obj, objtype=objtype)

    def _get(self, obj: object, objtype=None) -> object:
        raise NotImplementedError(f"_get is not implemented for {type(obj)}")

    def __set__(self, obj: object, value: object):
        self._validate(obj, value)
        self._set(obj, value)

    def _validate(self, obj: object, value: object) -> None:
        """
        override for type specific validation. Should raise an exception if invalid,
        not return a bool
        """
        # No exception raised by default
        pass

    def _set(self, obj: object, value: object) -> None:
        raise NotImplementedError('_set is not implemented')

    def _attribute_error(self, objtype):
        raise AttributeError(f"'{objtype.__name__}' object has no attribute '{self.public_name}'")

    def _get_object(self, obj: object) -> object:
        """
        Gets a field that is nested in another dictionary object. Allows a descriptor to grab a property
        from inside a dict that is potentially many levels deep
        """
        if self.nested is None:
            # This will happen when checking if the class has this attribute. Return the descriptor
            if obj is None:
                return self
            return obj[self.dict_name]

        nestedObj = self.__traverse_nested_objects(obj)

        return nestedObj[self.dict_name]

    def _set_object(self, obj: object, value: object) -> None:
        """
        Sets a field that is nested in another dictionary object. If that dictionary doesn't exist, this creates
        it, first checking that the attribute exists
        """
        if self.nested is None:
            return obj._set_item(self.dict_name, value)

        nestedObj = self.__traverse_nested_objects(obj)

        # finally, set the nested object on the dict/APIObject requested.
        desc = getattr(nestedObj.__class__, self.public_name, None)
        if desc is not None:
            setattr(nestedObj, self.public_name, value)
        else:
            nestedObj[self.dict_name] = value

    def __traverse_nested_objects(self, obj: object) -> object:
        """
        Goes through nested objects until it has traversed all nested levels. Returns that object, creating it
        and parents along the way.
        """
        for f in self.nested:
            # Does it have a descriptor for this nested field? If so, use it
            desc = getattr(obj.__class__, f, None)
            # There is a descriptor or it has this attribute, use getattr
            if desc is not None or hasattr(obj, f):
                try:
                    obj = getattr(obj, f)
                # Attribute doesn't exist, set it as an empty dict. We have to assume that descriptor handles this okay
                # but we'll get an exception otherwise, just might be hard to track down.
                except Exception:
                    setattr(obj, f, {})
                    obj = getattr(obj, f)
            else:
                try:
                    obj = obj[f]
                except KeyError:
                    obj[f] = {}
                    obj = obj[f]
        return obj


class GeometryDescr(BaseDescr):
    """GeometryDescr is a geometry field descriptor for a geodesic.bases.APIObject.

    Args:
        bbox: a bbox attribute that will be set when the geometry is updated. This is
            important for keeping geometry/bbox in sync on objects where the bbox is
            always derived from a geometry field.

    __get__ returns a shapely representation of the geometry
    __set__ coerces the input into a geojson dict (__geo_interface__)
        and stores internally to the APIObject dict

    """

    def __init__(self, bbox=None, **kwargs):
        super().__init__(**kwargs)
        self.bbox = bbox

    def _get(self, obj, objtype=None) -> BaseGeometry:
        """
        Gets the geometry attribute of an object.

        Raises:
            AttributeError if geometry is None or doesn't exist
        """
        # Try to get the private attribute by name (e.g. '_geometry')
        g = getattr(obj, self.private_name, None)
        if g is not None:
            # Return it if it exists
            return g

        # Otherwise, extract and compute. The attribute should be a geojson geometry, so this should work if
        # it's valid
        try:
            shp = self._get_object(obj)
            shp = shape(shp)
            setattr(obj, self.private_name, shp)
        except KeyError:
            if self.default is None:
                self._attribute_error(objtype)
            return self.default
        except Exception:
            raise ValueError(f"unable to get '{self.public_name}'")
        return shp

    def _set(self, obj: object, value: Union[object, dict, str, bytes]) -> None:
        """
        Sets a geometry on obj.

        Args:
            obj: the object to be modified
            value: any object implementing the __geo_interface__ convention (https://gist.github.com/sgillies/2217756),
                a dict representing an RFC 7946 GeoJSON geometry, a WKT string, or a WKB bytestring
        """
        # Reset the private attribute (e.g. "_geometry") to None
        setattr(obj, self.private_name, None)

        # If it's a dict, set directly
        if isinstance(value, dict):
            setval = value
        # Is it WKT?
        elif isinstance(value, str):
            shp = loads_wkt(value)
            setval = shp.__geo_interface__
        # Is it WKB?
        elif isinstance(value, bytes):
            shp = loads_wkb(value)
            setval = shp.__geo_interface__
        # Otherwise use the __geo_interface__ attr
        else:
            setval = value.__geo_interface__

        self._set_object(obj, setval)

        if self.bbox is not None:
            self.bbox.__set__(obj, self.__get__(obj).bounds)

    def _validate(self, obj: object, value: object) -> None:
        if isinstance(value, dict):
            # make sure value is a geojson geometry
            try:
                shp = shape(value)
                if not shp.is_valid:
                    shp = shp.buffer(0)
                    if not shp.is_valid:
                        raise ValueError("this does not appear to be a valid geometry")
            except Exception as e:
                raise ValueError("this does not appear to be a valid geometry") from e
        elif isinstance(value, str):
            # make sure value is WKT
            try:
                loads_wkt(value)
            except Exception as e:
                raise ValueError("unable to parse input string: must be well-known text (WKT)") from e
        elif isinstance(value, bytes):
            # make sure value is WKB
            try:
                loads_wkb(value)
            except Exception as e:
                raise ValueError("unable to parse input string: must be well-known binary (WKB)") from e
            # make sure value it implements __geo_interface__
        elif not hasattr(value, '__geo_interface__'):
            raise ValueError(f"invalid geometry of type '{type(value)}'")


class BBoxDescr(GeometryDescr):
    """
    BBoxDescr is a bounding box field descriptor for a geodesic.bases.APIObject.

    Inherits from GeometerDescr to use its validator

    __get__ returns a tuple of 4 values representing corners of the bbox (xmin, ymin, xmax, ymax)
    __set__ coerces the input into a shapely geom before taking the bounds
        and stores internally to the APIObject dict
    """

    def _get(self, obj: object, objtype=None) -> tuple:
        # Try to get the private attribute by name (e.g. '_bbox')
        g = getattr(obj, self.private_name, None)
        if g is not None:
            # Return it if it exists
            return g

        # Otherwise, extract and compute. The attribute should be a list/tuple
        try:
            bbox = self._get_object(obj)
            bbox = box(*bbox)
            bbox = bbox.bounds
            setattr(obj, self.private_name, bbox)
        except KeyError:
            if self.default is None:
                self._attribute_error(objtype)
            return self.default
        except Exception:
            raise ValueError(f"unable to get '{self.public_name}'")
        return bbox

    def _set(self, obj: object, value: Union[object, dict, str, bytes, tuple, list]) -> None:
        # if it's a list/tuple, set directly
        if isinstance(value, (tuple, list)):
            bbox = tuple(value)
        # If it's a dict, get shape bounds
        elif isinstance(value, dict):
            bbox = shape(value).bounds
        # Is it WKT?
        elif isinstance(value, str):
            shp = loads_wkt(value)
            bbox = shp.bounds
        # Is it WKB?
        elif isinstance(value, bytes):
            shp = loads_wkb(value)
            bbox = shp.bounds
        # Otherwise use the __geo_interface__ attr
        else:
            shp = shape(value.__geo_interface__)
            bbox = shp.bounds

        self._set_object(obj, bbox)

    def _validate(self, obj: object, value: object) -> None:
        if isinstance(value, (list, tuple)):
            if len(value) != 4:
                raise ValueError("bbox must contain exactly 4 values")
            for x in value:
                if not isinstance(x, (int, float)):
                    raise ValueError("bbox elements must be real numbers")
        else:
            super()._validate(obj, value)


class RegexDescr(BaseDescr):
    """
    RegexDescr is a field that is _validated against a regex

    This field is configured against the regular expression: {regex}

    __get__ returns the validated string
    __set__ validates a string and then sets the value in the APIObject dict
    """
    def __init__(self, regex: Union[re.Pattern, str], **kwargs) -> None:
        super().__init__(**kwargs)
        if isinstance(regex, str):
            self.regex = re.compile(regex)
        elif isinstance(regex, re.Pattern):
            self.regex = regex
        else:
            raise TypeError("regex must be a string or a re.Pattern object")
        self.__doc__ = self.__doc__.format(regex=self.regex.pattern)

    def _get(self, obj: object, objtype=None) -> str:
        try:
            return self._get_object(obj)
        except KeyError:
            if self.default is None:
                self._attribute_error(objtype)
            return self.default

    def _set(self, obj: object, value: str) -> None:
        self._set_object(obj, value)

    def _validate(self, obj: object, value: str) -> None:
        if not isinstance(value, str):
            raise ValueError(f"'{self.public_name}' must be a string")

        match = self.regex.match(value)
        if not match:
            raise ValueError(f"'{self.public_name}' must match {self.regex.pattern}")


class DictDescr(BaseDescr):
    """
    DictDescr is a dictionary field, such as properties in a GeoJSON object.
    This set/returns a dictionary field no matter what, it doesn't raise an
    attribute error

    __get__ returns the dict, creating it on the base object if necessary
    __set__ sets the dictionary after validating that it is a dict
    """
    def _get(self, obj: object, objtype=None) -> dict:
        try:
            d = self._get_object(obj)
        except KeyError:
            if self.default is not None:
                return self.default
            d = {}
            self._set_object(obj, d)
        return d

    def _set(self, obj: object, value: dict):
        if value is None:
            self._set_object(obj, {})
            return
        self._set_object(obj, value)

    def _validate(self, obj: object, value: dict) -> None:
        if value is None:
            return
        if not isinstance(value, dict):
            raise ValueError('must be a dict')


class ListDescr(BaseDescr):
    """
    ListDescr is a list field, such as links in a GeoJSON feature collection object.
    This sets/returns a list field no matter what, it doesn't raise an
    attribute error

    __get__ returns the list, creating it on the base object if necessary
    __set__ sets the list after validating that it is a list
    """
    def __init__(self, item_type=None, min_len=None, max_len=None, **kwargs):
        super().__init__(**kwargs)
        self.item_type = item_type
        self.max_len = max_len
        self.min_len = min_len

    def _get(self, obj: object, objtype=None) -> list:
        try:
            d = self._get_object(obj)
        except KeyError:
            if self.default is not None:
                return self.default
            d = []
            self._set_object(obj, d)
        return d

    def _set(self, obj: object, value: list):
        if value is None:
            return self._set_object(obj, [])
        self._set_object(obj, value)

    def _validate(self, obj: object, value: list) -> None:
        if value is None:
            return
        if not isinstance(value, list):
            raise ValueError(f'must be a list, got {type(value)}')

        # len check
        if self.max_len is not None and len(value) > self.max_len:
            raise ValueError(f"list must be less than or equal to {self.max_len} elements in length")
        if self.min_len is not None and len(value) < self.min_len:
            raise ValueError(f"list must be greater than or equal to {self.min_len} elements in length")

        if self.item_type is not None:
            if len(value) > 0:
                if not isinstance(value[0], self.item_type):
                    raise ValueError(f"'{self.public_name}' must be a list of {self.item_type}")


class TupleDescr(BaseDescr):
    """represents a tuple field

    TupleDescr is a tuple field (immutable), such as image shape.
    This raises an attribute error

    __get__ returns the tuple, creating it on the base object if necessary
    __set__ sets the tuple after validating that it is a tuple
    """
    def __init__(self, item_type=None, min_len=None, max_len=None, **kwargs):
        super().__init__(**kwargs)
        self.item_type = item_type
        self.max_len = max_len
        self.min_len = min_len

    def _get(self, obj: object, objtype=None) -> tuple:
        try:
            d = self._get_object(obj)
        except KeyError:
            self._attribute_error(objtype)
        return d

    def _set(self, obj: object, value: tuple):
        self._set_object(obj, tuple(value))

    def _validate(self, obj: object, value: tuple) -> None:
        if not isinstance(value, (tuple, list)):
            raise ValueError(f'must be a tuple or list, got {type(value)}')

        # len check
        if self.max_len is not None and len(value) > self.max_len:
            raise ValueError(f"tuple must be less than or equal to {self.max_len} elements in length")
        if self.min_len is not None and len(value) < self.min_len:
            raise ValueError(f"tuple must be greater than or equal to {self.min_len} elements in length")

        if self.item_type is not None:
            if len(value) > 0:
                if not isinstance(value[0], self.item_type):
                    raise ValueError(f"'{self.public_name}' must be a tuple of {self.item_type}")


class DatetimeDescr(BaseDescr):
    """
    DatetimeDescr is a UTC datetime field and is setable through typical python datetime objects,
        numpy datetime64, or pandas.Timestamp objects, pandas datetime objects, and RFC3339 strings

    __get__ returns the datetime, raise an AttributeError if missing
    __set__ sets the datetime, storing internally as an RFC3339 string
    """

    rfc3339_regex = re.compile(r'^((?:(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}:\d{2}(?:\.\d+)?))(Z|[\+-]\d{2}:\d{2})?)$')

    def _get(self, obj: object, objtype=None) -> datetime.datetime:
        # Try to get the private attribute by name (e.g. '_datetime')
        dt = getattr(obj, self.private_name, None)
        if dt is not None:
            # Return it if it exists
            return dt

        # Otherwise, extract and compute. The attribute should be an RFC3339 string
        try:
            dt = self._get_object(obj)
            dt = isoparse(dt)
            dt = datetime_to_utc(dt)
            setattr(obj, self.private_name, dt)
        except KeyError:
            if self.default is None:
                self._attribute_error(objtype)
            return self.default
        except Exception:
            raise ValueError(f"unable to get '{self.public_name}', ")
        return dt

    def _set(self, obj: object, value: Union[str, datetime.datetime, np.datetime64]) -> None:
        # Reset the private attribute (e.g. "_datetime") to None
        setattr(obj, self.private_name, None)

        setval = None
        if isinstance(value, str):
            setval = value
        elif isinstance(value, datetime.datetime):
            # Convert to UTC
            value = datetime_to_utc(value)
            setval = value.isoformat()
        elif isinstance(value, np.datetime64):
            dtstr = np.datetime_as_string(value, timezone=pytz.UTC)
            dt = isoparse(dtstr)
            setval = dt.isoformat()
        else:
            raise ValueError("unable to set value")

        self._set_object(obj, setval)

    def _validate(self, obj: object, value: object) -> None:
        if isinstance(value, str):
            if not self.rfc3339_regex.match(value):
                raise ValueError('value is not an RFC3339 formatted datetime string')
        elif isinstance(value, datetime.datetime):
            # Convert to UTC
            try:
                value = datetime_to_utc(value)
            # I can't think of how this could fail, but it's here just in case
            except Exception as e:
                raise ValueError('invalid datetime') from e

        elif isinstance(value, np.datetime64):
            try:
                dtstr = np.datetime_as_string(value, timezone=pytz.UTC)
                isoparse(dtstr)
            # I can't think of how this could fail, but it's here just in case
            except Exception as e:
                raise ValueError('invalid datetime64') from e
        else:
            raise ValueError("invalid value to datetime, must be string, "
                             "datetime.datetime or numpy.datetime64")


class StringDescr(BaseDescr):
    """
    StringDescr is a string field, raises attribute error if the string isn't set

    Args:
        one_of: is provide a list of possible values this string can be.

    __get__ returns the string
    __set__ sets the string after validating that it is a string/unicode
    """
    def __init__(self, one_of=[], **kwargs):
        super().__init__(**kwargs)
        self.one_of = one_of

    def _get(self, obj: object, objtype=None) -> str:
        try:
            return self._get_object(obj)
        except KeyError:
            if self.default is None:
                self._attribute_error(objtype)
            return self.default

    def _set(self, obj: object, value: str):
        self._set_object(obj, value)

    def _validate(self, obj: object, value: str) -> None:
        if not isinstance(value, str):
            raise ValueError('must be a str')
        if self.one_of:
            if value not in self.one_of:
                raise ValueError(f'value must be one of {", ".join(self.one_of)}')


class IntDescr(BaseDescr):
    """
    IntDescr is an integer field, raises attribute error if the int isn't set

    __get__ returns the int
    __set__ sets the int after validating that it is an int
    """
    def _get(self, obj: object, objtype=None) -> int:
        try:
            return self._get_object(obj)
        except KeyError:
            if self.default is None:
                self._attribute_error(objtype)
            return self.default

    def _set(self, obj: object, value: int):
        self._set_object(obj, value)

    def _validate(self, obj: object, value: int) -> None:
        if not isinstance(value, int):
            raise ValueError('must be an int')


class FloatDescr(BaseDescr):
    """
    FloatDescr is an float field, raises attribute error if the float isn't set

    __get__ returns the float
    __set__ sets the float after validating that it is an float
    """
    def _get(self, obj: object, objtype=None) -> float:
        try:
            return self._get_object(obj)
        except KeyError:
            if self.default is None:
                self._attribute_error(objtype)
            return self.default

    def _set(self, obj: object, value: float):
        self._set_object(obj, value)

    def _validate(self, obj: object, value: float) -> None:
        if not isinstance(value, float):
            raise ValueError('must be a float')


class NumberDescr(BaseDescr):
    """
    NumberDescr is an numeric field, raises attribute error if the number isn't set

    __get__ returns the number
    __set__ sets the number after validating that it is a number
    """
    def _get(self, obj: object, objtype=None) -> Union[float, int, complex]:
        try:
            return self._get_object(obj)
        except KeyError:
            if self.default is None:
                self._attribute_error(objtype)
            return self.default

    def _set(self, obj: object, value: Union[float, int, complex]):
        self._set_object(obj, value)

    def _validate(self, obj: object, value: Union[float, int, complex]) -> None:
        if not isinstance(value, (int, float, complex)):
            raise ValueError('must be a number')


class BoolDescr(BaseDescr):
    """
    BoolDescr is an bool field, raises attribute error if the bool isn't set

    __get__ returns the bool
    __set__ sets the bool after validating that it is an bool
    """

    def _get(self, obj: object, objtype=None) -> bool:
        try:
            return self._get_object(obj)
        except KeyError:
            if self.default is None:
                self._attribute_error(objtype)
            return self.default

    def _set(self, obj: object, value: bool):
        self._set_object(obj, value)

    def _validate(self, obj: object, value: bool) -> None:
        if not isinstance(value, bool):
            raise ValueError('must be a bool')


class DatetimeIntervalDescr(BaseDescr):
    rfc3339_regex = re.compile(r'^((?:(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}:\d{2}(?:\.\d+)?))(Z|[\+-]\d{2}:\d{2})?)$')

    """
    DatetimeIntervalDescr is a start/end pair which can be specified using either RFC3339 strings
        datetime.datetime, pandas.Timestamp, or numpy.datetime64

    __get__ returns the datetime interval as a tuple, raise an AttributeError if missing
    __set__ sets the datetime interval, storing internally as a string of the format '<start>/<end>' where
        start/end are RFC3339 formatted strings or "..". This is in accordance with the STAC datetime spec
    """

    def _get(self, obj: object, objtype=None) -> tuple:
        # Try to get the private attribute by name (e.g. '_datetime')
        dt = getattr(obj, self.private_name, None)
        if dt is not None:
            # Return it if it exists
            return dt

        try:
            dt = self._get_object(obj)
            start_str, end_str = dt.split('/')
            start = end = None
            if '..' not in start_str:
                start = isoparse(start_str)
                start = datetime_to_utc(start)
            if '..' not in end_str:
                end = isoparse(end_str)
                end = datetime_to_utc(end)

            setattr(obj, self.private_name, (start, end))
        except KeyError:
            if self.default is None:
                self._attribute_error(objtype)
            return self.default
        except Exception:
            raise ValueError(f"unable to get '{self.public_name}', ")
        return (start, end)

    def _set(self, obj: object, value: object) -> None:

        setattr(obj, self.private_name, None)

        if isinstance(value, str):
            start_str, end_str = value.split('/')
            # Canonicalize the string
            if start_str != "..":
                start_str = datetime_to_utc(isoparse(start_str)).isoformat()
            if end_str != "..":
                end_str = datetime_to_utc(isoparse(end_str)).isoformat()
        else:
            start, end = value
            if isinstance(start, str):
                if start == '..':
                    start_str = start
                else:
                    start_str = datetime_to_utc(isoparse(start)).isoformat()
            elif isinstance(start, datetime.datetime):
                start_str = datetime_to_utc(start).isoformat()
            elif isinstance(start, np.datetime64):
                start_str = np.datetime_as_string(start, timezone=pytz.UTC)
                start_str = isoparse(start_str).isoformat()
            elif start is None:
                start_str = '..'
            else:
                raise ValueError('error setting start datetime, invalid datetime format')

            if isinstance(end, str):
                if end == '..':
                    end_str = end
                else:
                    end_str = datetime_to_utc(isoparse(end)).isoformat()
            elif isinstance(end, datetime.datetime):
                end_str = datetime_to_utc(end).isoformat()
            elif isinstance(end, np.datetime64):
                end_str = np.datetime_as_string(end, timezone=pytz.UTC)
                end_str = isoparse(end_str).isoformat()
            elif end is None:
                end_str = '..'
            else:
                raise ValueError('error setting end datetime, invalid datetime format')

        self._set_object(obj, f'{start_str}/{end_str}')

    def _validate(self, obj: object, value: object) -> None:
        if isinstance(value, str):
            try:
                start_str, end_str = value.split('/')

                # Are they RFC3339?
                if not self.rfc3339_regex.match(start_str) and start_str != "..":
                    raise ValueError('start must be RFC3339 formatted')
                if not self.rfc3339_regex.match(end_str) and end_str != "..":
                    raise ValueError('end must be RFC3339 formatted')
            except Exception as e:
                raise ValueError('datetime as a string must be of the form <start>/<end>') from e

        elif isinstance(value, (tuple, list)):
            if len(value) != 2:
                raise ValueError("Must provide a start and end datetime. "
                                 "Provide None or '..' string if one end is open")
            for i, t in enumerate(value):
                if isinstance(t, str):
                    if t == "":
                        raise ValueError("string must be either '..' or a valid RFC3339 datetime")
                    if t != ".." and not self.rfc3339_regex.match(t):
                        if i == 0:
                            name = 'start'
                        else:
                            name = 'end'
                        raise ValueError(f'{name} must be RFC3339 formatted')

                elif not (isinstance(t, datetime.datetime) or t is None or isinstance(t, np.datetime64)):
                    raise ValueError("not a recognized datetime format. must be either "
                                     "python datetime, numpy.datetime64, pandas.Timestamp or string")
        else:
            raise ValueError(f"invalid datetime interval format {type(value)}")


class DTypeDescr(BaseDescr):
    """a descriptor for numpy style dtypes

    DTypeDescr is a np.dtype field, raises attribute error if dtype is not set

    __get__ returns the np.dtype
    __set__ sets the dtype after validating that it is a dtype, holds internally by its str representation
    """

    def _get(self, obj: object, objtype=None) -> np.dtype:
        try:
            dt = self._get_object(obj)
            dt = np.dtype(dt)
            return dt
        except KeyError:
            if self.default is None:
                self._attribute_error(objtype)
            return self.default

    def _set(self, obj: object, value: bool):
        dt = np.dtype(value)
        dtype_str = dt.descr[0][1]

        self._set_object(obj, dtype_str)

    def _validate(self, obj: object, value: np.dtype) -> None:
        if isinstance(value, np.dtype):
            return
        else:
            try:
                np.dtype(value)
            except Exception:
                raise ValueError('dtype must be a np.dtype, python numeric dtype, or valid dtype string/descriptor')


class TypeConstrainedDescr(BaseDescr):
    """TypeConstrainedDescr creates an arbitrary field that must be constrained to a specific type

    Args:
        type(type): the type you want to constrain this too

    __get__ returns the object as is, AttributeError if missing
    __set__ sets the object as is, validating against the specified type constraint
    """
    def __init__(self, type, **kwargs):
        super().__init__(**kwargs)
        self._type = type

    def _get(self, obj: object, objtype=None) -> float:
        try:
            return self._get_object(obj)
        except KeyError:
            if self.default is None:
                self._attribute_error(objtype)
            return self.default

    def _set(self, obj: object, value: object):
        self._set_object(obj, value)

    def _validate(self, obj: object, value: object) -> None:
        if not isinstance(value, self._type):
            raise ValueError(f"value must be a {self._type}, got {type(value)}")


supported_schemes = ("http", "https")


class URLDescr(StringDescr):
    def _validate(self, obj: object, value: str) -> None:
        super()._validate(obj, value)

        parsed = urlparse(value)
        if parsed.scheme not in supported_schemes:
            raise ValueError(f"only schemes {', '.join(supported_schemes)} are supported, got {parsed.scheme}")

        if parsed.netloc == "":
            raise ValueError(f"url {value} had an empty network location")
