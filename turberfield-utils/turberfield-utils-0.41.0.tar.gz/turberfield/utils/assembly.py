#!/usr/bin/env python3
# encoding: UTF-8

# This file is part of turberfield.
#
# Turberfield is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Turberfield is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with turberfield.  If not, see <http://www.gnu.org/licenses/>.


from collections import Counter
from collections import deque
from collections import OrderedDict
from decimal import Decimal
from enum import Enum
from inspect import getmembers
import json
import re
from uuid import UUID

from turberfield.utils.encoder import JSONEncoder

class Assembly:

    decoding = {}
    encoding = {}

    class Encoder(JSONEncoder):

        def default(self, obj):
            tag = Assembly.encoding.get(type(obj), None)
            if tag is not None:
                rv = dict(_type=tag)
                try:
                    attribs = obj._asdict()
                except AttributeError:
                    if isinstance(obj, Enum):
                        attribs = {"name": obj.name, "value": obj.value}
                    elif isinstance(obj, UUID):
                        attribs = {"int": obj.int}
                    else:
                        attribs = vars(obj)
                rv.update(attribs)
                return rv

            if isinstance(obj, (Counter, OrderedDict)):
                return list(obj.items())

            try:
                return JSONEncoder.default(self, obj)
            except TypeError as e:
                try:
                    return obj.strftime("%Y-%m-%d %H:%M:%S")
                except AttributeError:
                    if isinstance(obj, (complex, )):
                        return str(obj)
                    elif isinstance(obj, (deque,)):
                        return list(obj)
                    elif isinstance(obj, (Decimal, )):
                        return float(obj)
                    elif isinstance(obj, type(re.compile(""))):
                        return obj.pattern
                    else:
                        raise Exception(
                            "{0} not registered with Assembly".format(
                                type(obj)
                            )
                        )

    @staticmethod
    def register(*args, namespace=None):
        """
        Call this function to register your classes for Assembly.

        Returns a list of the types so far registered.

        In order to create objects from JSON, your types must support
        construction semantics with keyword arguments
        (ie: ``MyClass(**kwargs)``).

        If this is not possible (as in the case of Enums), then define
        a classmethod called `factory` which will be used instead, eg::

            class Colour(enum.Enum):
                red = (255, 0 , 0)
                green = (0, 255 , 0)
                blue = (0, 0 , 255)

                @classmethod
                def factory(cls, name=None, **kwargs):
                    return cls[name]


            Assembly.register(Colour)

        """
        tmplt = "{module}.{name}" if namespace is None else "{namespace}.{module}.{name}"
        for arg in args:
            module = dict(getmembers(arg)).get("__module__")
            tag = tmplt.format(
                namespace=namespace,
                module=module,
                name=arg.__name__
            )
            Assembly.decoding[tag] = arg
            Assembly.encoding[arg] = tag

        return list(Assembly.encoding.keys())

    @staticmethod
    def object_hook(obj):
        typ = obj.pop("_type", None)
        cls = Assembly.decoding.get(typ, None)
        try:
            factory = getattr(cls, "factory", cls)
            return factory(**obj)
        except TypeError:
            return obj

    @staticmethod
    def dump(
        obj, fp, skipkeys=False, ensure_ascii=True, check_circular=True,
        allow_nan=True, cls=None, indent=None, separators=None,
        default=None, sort_keys=False, **kwargs
    ):
        """
        Serialize `obj` as a JSON formatted stream to `fp`.

        This function is compatible with `json.dump`_ from Python's
        standard library, and accepts the same arguments.

        .. _json.dump: https://docs.python.org/3/library/json.html#json.dump
        """
        dumper = Assembly.Encoder(
            skipkeys=skipkeys, ensure_ascii=ensure_ascii,
            check_circular=check_circular, allow_nan=allow_nan,
            indent=indent, separators=separators, default=default,
            sort_keys=sort_keys, **kwargs
        ).iterencode(obj)
        for chunk in dumper:
            fp.write(chunk)

    @staticmethod
    def dumps(
        obj, skipkeys=False, ensure_ascii=True, check_circular=True,
        allow_nan=True, cls=None, indent=None, separators=None,
        default=None, sort_keys=False, **kwargs
    ):
        """
        Serialize `obj` to a JSON formatted string.

        This function is compatible with `json.dumps`_ from Python's
        standard library, and accepts the same arguments.

        .. _json.dumps: https://docs.python.org/3/library/json.html#json.dumps
        """
        return Assembly.Encoder(
            skipkeys=skipkeys, ensure_ascii=ensure_ascii,
            check_circular=check_circular, allow_nan=allow_nan,
            indent=indent, separators=separators, default=default,
            sort_keys=sort_keys, **kwargs
        ).encode(obj)

    @staticmethod
    def loads(s):
        """
        Deserialize a JSON string to Python object(s). Those types you
        have registered will be recognised and used to create the
        deserialised objects.

        """
        return json.loads(
            s,
            object_hook=Assembly.object_hook,
            # object_pairs_hook=OrderedDict,
            parse_float=Decimal
        )
