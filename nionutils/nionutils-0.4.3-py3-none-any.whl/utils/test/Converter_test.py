# standard libraries
import logging
import unittest

# local libraries
from nion.utils import Converter


class TestConverter(unittest.TestCase):

    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    def test_float_to_scaled_integer_with_negative_min(self) -> None:
        converter = Converter.FloatToScaledIntegerConverter(1000, -100, 100)
        self.assertAlmostEqual(converter.convert(0) or 0, 500)
        self.assertAlmostEqual(converter.convert(-100) or 0, 0)
        self.assertAlmostEqual(converter.convert(100) or 0, 1000)
        self.assertAlmostEqual(converter.convert_back(converter.convert(0)) or 0.0, 0)
        self.assertAlmostEqual(converter.convert_back(converter.convert(-100)) or 0.0, -100)
        self.assertAlmostEqual(converter.convert_back(converter.convert(100)) or 0.0, 100)

    def test_integer_to_string_converter(self) -> None:
        converter = Converter.IntegerToStringConverter()
        self.assertEqual(converter.convert_back("-1"), -1)
        self.assertEqual(converter.convert_back("2.45653"), 2)
        self.assertEqual(converter.convert_back("-adcv-2.15sa56aas"), -2)
        self.assertEqual(converter.convert_back("xx4."), 4)


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
