import unittest

from conversions import convert, representations, master


class ConversionTestCase(unittest.TestCase):

    def setUp(self):
        self.convert_from_base_10 = convert.convert_from_base_10
        self.convert_to_base_10 = convert.convert_to_base_10
        self.convert_from_base_10_float = convert.convert_float_from_base_10
        self.convert_to_base_10_float = convert.convert_float_to_base_10
        self.represent = representations.convert_to_representation
        self.un_represent = representations.convert_from_representation
        self.master = master.convert_number

    def test_conversion_from(self):
        self.assertEqual([1, 14], self.un_represent('1E'))
        self.assertEqual([1, 1, 0], self.un_represent('110'))
        self.assertEqual([1, 7, 2], self.un_represent('172'))
        self.assertEqual([2, 18, 15], self.un_represent('2IF'))

    def test_conversion_to(self):
        self.assertEqual('1E', self.represent([1, 14]))
        self.assertEqual('110', self.represent([1, 1, 0]))
        self.assertEqual('172', self.represent([1, 7, 2]))
        self.assertEqual('2I', self.represent([2, 18]))

    def test_convert_from_base_10(self):
        self.assertRaises(TypeError, self.convert_from_base_10, '10', 2)
        self.assertRaises(TypeError, self.convert_from_base_10, 10, '2')
        self.assertEqual(self.convert_from_base_10(200, 11), ['172', 11])
        self.assertEqual(self.convert_from_base_10(20, 2), ['10100', 2])
        self.assertEqual(self.convert_from_base_10(16, 16), ['10', 16])
        self.assertEqual(self.convert_from_base_10(30, 16), ['1E', 16])

    def test_convert_from_base_10_independent(self):
        self.assertEqual(['1C8', 16], self.convert_from_base_10(456, 16))
        self.assertEqual(['GO', 27], self.convert_from_base_10(456, 27))
        self.assertEqual(['D1', 35], self.convert_from_base_10(456, 35))
        self.assertEqual(['385', 11], self.convert_from_base_10(456, 11))
        self.assertEqual(['DR', 33], self.convert_from_base_10(456, 33))
        self.assertEqual(['E8', 32], self.convert_from_base_10(456, 32))

    def test_convert_from_float_base_10(self):
        self.assertRaises(AssertionError, self.convert_from_base_10_float, 10, 2)
        self.assertRaises(AssertionError, self.convert_from_base_10_float, -1, 2)
        self.assertRaises(TypeError, self.convert_from_base_10_float, '0.2', 2)
        self.assertRaises(TypeError, self.convert_from_base_10_float, 0.2, '2')
        self.assertEqual(['0.AB851EB851EB851E', 16], self.convert_from_base_10_float(0.67, 16))
        self.assertEqual(['0.8', 20], self.convert_from_base_10_float(0.4, 20))
        self.assertEqual(['0.01', 2], self.convert_from_base_10_float(0.25, 2))
        self.assertEqual(['0.444444444444444', 17], self.convert_from_base_10_float(0.25, 17))
        self.assertEqual(['0.2', 8], self.convert_from_base_10_float(0.25, 8))
        self.assertEqual(['0.4', 16], self.convert_from_base_10_float(0.25, 16))
        self.assertEqual(['0.5', 20], self.convert_from_base_10_float(0.25, 20))

    def test_convert_to_base_10(self):
        self.assertRaises(TypeError, self.convert_to_base_10, 23, 5)
        self.assertRaises(TypeError, self.convert_to_base_10, '23', '5')
        self.assertEqual(200, self.convert_to_base_10('172', 11))
        self.assertEqual(20, self.convert_to_base_10('10100', 2))
        self.assertEqual(16, self.convert_to_base_10('10', 16))
        self.assertEqual(30, self.convert_to_base_10('1E', 16))

    def test_convert_to_base_10_independent(self):
        self.assertEqual(456, self.convert_to_base_10('1C8', 16))
        self.assertEqual(456, self.convert_to_base_10('GO', 27))
        self.assertEqual(456, self.convert_to_base_10('D1', 35))
        self.assertEqual(456, self.convert_to_base_10('385', 11))
        self.assertEqual(456, self.convert_to_base_10('DR', 33))
        self.assertEqual(456, self.convert_to_base_10('E8', 32))

    def test_convert_to_base_10_float(self):
        self.assertRaises(TypeError, self.convert_to_base_10_float, 0.3, 4)
        self.assertRaises(TypeError, self.convert_to_base_10_float, '0.3', '4')
        self.assertEqual(0.67, self.convert_to_base_10_float('0.AB851EB851EB851E', 16))
        self.assertEqual(0.4, self.convert_to_base_10_float('0.8', 20))
        self.assertEqual(0.25, self.convert_to_base_10_float('0.01', 2))
        self.assertEqual(0.25, self.convert_to_base_10_float('0.444444444444444', 17))
        self.assertEqual(0.25, self.convert_to_base_10_float('0.2', 8))
        self.assertEqual(0.25, self.convert_to_base_10_float('0.4', 16))
        self.assertEqual(0.25, self.convert_to_base_10_float('0.5', 20))

    def test_master_convert(self):
        self.assertRaises(TypeError, self.master, 12, 10, 2)
        self.assertRaises(TypeError, self.master, '12', '10', 2)
        self.assertRaises(TypeError, self.master, '12', 10, '2')
        self.assertEqual('11001000.001', self.master('C8.2', 16, 2))
        self.assertEqual('C8.2', self.master('11001000.001', 2, 16))
        self.assertEqual('7', self.master('111', 2, 10))


if __name__ == '__main__':
    unittest.main()
