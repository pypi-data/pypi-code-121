import unittest

from cc_py_commons.utils.temperature_utils import to_celsius


class TestTemperatureUtils(unittest.TestCase):

	def test_when_value_is_null(self):
		try:
			temp_in_celsius = to_celsius(None)
			self.assertIsNone(temp_in_celsius)
		except Exception as e:
			self.fail('test_when_value_is_null: Failed by throwing unexpected exception')

	def test_when_value_is_not_null(self):
		temp_in_celsius = to_celsius(65.0)

		self.assertEqual(18.33, temp_in_celsius)
