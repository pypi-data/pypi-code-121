import unittest

from py_dot.core.strings import to_kebab


class TestStrings(unittest.TestCase):
    def test_kebab_case(self):

        self.assertEqual(to_kebab('camelCase'), 'camel-case')
        self.assertEqual(to_kebab('spinal-case'), 'spinal-case')
        self.assertEqual(to_kebab('snake_case'), 'snake-case')
        self.assertEqual(to_kebab('PascalCase'), 'pascal-case')