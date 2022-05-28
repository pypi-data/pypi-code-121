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


import decimal
import enum
from collections import Counter
from collections import deque
from collections import namedtuple
from decimal import Decimal
import textwrap
import uuid
import unittest

from turberfield.utils.assembly import Assembly


class Wheelbarrow:

    Bucket = namedtuple("Bucket", ["capacity"])
    Brick = namedtuple("Brick", ["colour"])
    Grip = namedtuple("Grip", ["length", "colour"])
    Handle = namedtuple("Handle", ["length", "grip"])
    Rim = namedtuple("Rim", ["dia"])
    Tyre = namedtuple("Tyre", ["dia", "pressure"])
    Wheel = namedtuple("Wheel", ["rim", "tyre"])

    class Colour(enum.Enum):
        red = (255, 0 , 0)
        green = (0, 255 , 0)
        blue = (0, 0 , 255)

        @classmethod
        def factory(cls, name=None, **kwargs):
            return cls[name]


    def __init__(self, bucket=None, wheel=None, handles=[], contents=[]):
        self.bucket = bucket
        self.wheel = wheel
        self.handles = deque(handles, maxlen=2)
        self.contents = Counter(dict(contents))

class AssemblyTester(unittest.TestCase):

    data = textwrap.dedent("""
    {
        "_type": "turberfield.utils.test.test_assembly.Wheelbarrow",
        "bucket": {
            "_type": "turberfield.utils.test.test_assembly.Bucket",
            "capacity": 45
        },
        "wheel": {
            "_type": "turberfield.utils.test.test_assembly.Wheel",
            "rim": {
                "_type": "turberfield.utils.test.test_assembly.Rim",
                "dia": 22.85
            },
            "tyre": {
                "_type": "turberfield.utils.test.test_assembly.Tyre",
                "dia": 22.85,
                "pressure": 30
            }
        },
        "contents": [
            [
                {
                    "_type": "turberfield.utils.test.test_assembly.Brick",
                    "colour": "red"
                },
                60
            ],
            [
                {
                    "_type": "turberfield.utils.test.test_assembly.Brick",
                    "colour": "yellow"
                },
                40
            ]
        ],
        "handles": [
            {
                "_type": "turberfield.utils.test.test_assembly.Handle",
                "length": 80,
                "grip": {
                    "_type": "turberfield.utils.test.test_assembly.Grip",
                    "length": 15,
                    "colour": {
                        "_type": "turberfield.utils.test.test_assembly.Colour",
                        "name": "green",
                        "value": [
                            0,
                            255,
                            0
                        ]
                    }
                }
            },
            {
                "_type": "turberfield.utils.test.test_assembly.Handle",
                "length": 80,
                "grip": {
                    "_type": "turberfield.utils.test.test_assembly.Grip",
                    "length": 15,
                    "colour": {
                        "_type": "turberfield.utils.test.test_assembly.Colour",
                        "name": "green",
                        "value": [
                            0,
                            255,
                            0
                        ]
                    }
                }
            }
        ]
    }""")

    def setUp(self):
        types = Assembly.register(
            Wheelbarrow,
            Wheelbarrow.Brick,
            Wheelbarrow.Bucket,
            Wheelbarrow.Colour,
            Wheelbarrow.Grip,
            Wheelbarrow.Handle,
            Wheelbarrow.Rim,
            Wheelbarrow.Tyre,
            Wheelbarrow.Wheel,
            namespace="turberfield"
        )
        self.assertEqual(9, len(types))

    def test_uuid(self):
        # From Python 3.8 a UUID object has no __dict__
        self.assertNotIn(uuid.UUID, Assembly.encoding)
        self.assertNotIn(uuid.UUID, Assembly.decoding)
        Assembly.register(uuid.UUID)
        obj = uuid.uuid4()
        rv = Assembly.dumps(obj)
        self.assertIn(uuid.UUID, Assembly.encoding)
        self.assertIn("uuid.UUID", Assembly.decoding)

    def test_numeric_types(self):
        val = decimal.Decimal("3.14")
        rv = Assembly.dumps(val)
        self.assertEqual("3.14", rv)
        self.assertEqual(val, Assembly.loads(rv))

        val = complex("3+14j")
        rv = Assembly.dumps(val)
        self.assertEqual('"(3+14j)"', rv)
        self.assertEqual(val, complex(Assembly.loads(rv).replace('"', "")))

    def test_nested_object_dumps(self):
        obj = Assembly.loads(AssemblyTester.data)
        text = Assembly.dumps(obj, indent=4)
        self.assertEqual(
            len(AssemblyTester.data.strip()),
            len(text.strip())
        )
            
    def test_nested_object_loads(self):
        rv = Assembly.loads(AssemblyTester.data)
        self.assertIsInstance(rv, Wheelbarrow)
        self.assertEqual(45, rv.bucket.capacity)
        self.assertIsInstance(rv.wheel.rim.dia, Decimal)
        self.assertEqual(30, rv.wheel.tyre.pressure)
        self.assertIsInstance(rv.handles, deque)
        self.assertEqual(2, len(rv.handles))
        self.assertEqual(Wheelbarrow.Colour.green, rv.handles[0].grip.colour)

    def test_nested_object_extraloads(self):
        data = AssemblyTester.data[:-3] + textwrap.dedent("""
        ,{
            "_type": "turberfield.utils.test.test_assembly.Handle",
            "length": 80,
            "grip": {
                "_type": "turberfield.utils.test.test_assembly.Grip",
                "length": 15,
                "colour": {
                    "_type": "turberfield.utils.test.test_assembly.Colour",
                    "name": "red",
                    "value": [
                        0,
                        255,
                        0
                    ]
                }
            }
        }
        ]}""")
        rv = Assembly.loads(data)
        self.assertIsInstance(rv, Wheelbarrow)
        self.assertIsInstance(rv.handles, deque)
        self.assertEqual(2, len(rv.handles))
        self.assertEqual(Wheelbarrow.Colour.green, rv.handles[0].grip.colour)
        self.assertEqual(Wheelbarrow.Colour.red, rv.handles[1].grip.colour)

    def test_nested_object_roundtrip(self):
        obj = Assembly.loads(AssemblyTester.data)
        text = textwrap.dedent(Assembly.dumps(obj))
        rv = Assembly.loads(text)
        self.assertEqual(obj.bucket, rv.bucket)
        self.assertEqual(obj.wheel, rv.wheel)
        self.assertEqual(obj.handles, rv.handles)
