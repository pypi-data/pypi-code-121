import logging
logging.disable(logging.CRITICAL)
import unittest
from dataUncert.unitSystem import unit


class test(unittest.TestCase):

    def testCombineUpperAndLower(self):
        A = unit()
        a = A._combineUpperAndLower(['hej', 'med'], ['dig'])
        self.assertEqual(a, 'hej-med/dig')

    def testCancleUnits(self):
        A = unit()
        a, b = A._cancleUnits(['hej', 'med', 'dig'], ['dig', 'med', 'asf'])
        self.assertEqual(a, ['hej'])
        self.assertEqual(b, ['asf'])

    def testPower(self):
        A = unit()
        with self.assertRaises(Exception) as context:
            a = A._power('L-kg/min', 1.5)
        self.assertEqual('The power has to be an integer', str(context.exception))
        a = A._power('L-kg/min', 2)
        self.assertEqual(a, 'L2-kg2/min2')

        a = A._power('m/s2', 0)
        self.assertEqual(a, '1')

    def testMultiply(self):
        A = unit()
        a = 'L/min'
        b = 'kg-m/L'
        c = A._multiply(a, b)
        self.assertEqual(c, 'kg-m/min')

        a = 'L/min'
        b = 'L/min'
        c = A._multiply(a, b)
        self.assertEqual(c, 'L2/min2')

    def testDivide(self):
        A = unit()
        a = 'L/min'
        b = 'kg-m/L'

        """
        L/min / (kg-m/L)
        L/min * L/kg-m
        L2 / min-kg-m
        """

        c = A._divide(a, b)
        self.assertEqual(c, 'L2/min-kg-m')

        a = 'L/min'
        b = 'L/min'
        c = A._divide(a, b)
        self.assertEqual(c, '1')

    def testAdd(self):
        A = unit()
        a = 'L/min'
        b = 'kg-m/L'
        c = A.assertEqual(a, b)
        self.assertEqual(c, False)
        a = 'L/min'
        b = 'L/min'
        c = A.assertEqual(a, b)
        self.assertEqual(c, True)

    def testSub(self):
        A = unit()
        a = 'L/min'
        b = 'kg-m/L'
        c = A.assertEqual(a, b)
        self.assertEqual(c, False)
        a = 'L/min'
        b = 'L/min'
        c = A.assertEqual(a, b)
        self.assertEqual(c, True)

    def testConvertToSI(self):
        A = unit()
        a, b = A.convertToSI(1, 'L/min')
        self.assertEqual(a, 1 / 1000 / 60)
        self.assertEqual(b, 'm3/s')

        a, b = A.convertToSI(1, 'bar-kg/h2-L3')
        self.assertAlmostEqual(a, 1 * 100000 * 1 * 1 / (60 * 60)**2 * (1000)**3)
        self.assertEqual(A.assertEqual(b, 'kg2/s4-m10'), True)
        'pa-kg/s2-(m3)3'
        '(N/m2)-kg/s2-m9'
        'N-kg/s2-m11'
        '(kg/m-s2)-kg/(s2-m11)'
        'kg2/(s4-m12)'
        with self.assertRaises(Exception) as context:
            a, b = A.convertToSI(1, 'aL')
        self.assertEqual(f'The unit (aL) was not found. Therefore it was interpreted as a prefix and a unit. However the prefix (a) was not found', str(context.exception))

        with self.assertRaises(Exception) as context:
            a, b = A.convertToSI(1, 'mD')
        self.assertEqual(f'The unit (mD) was not found. Therefore it was interpreted as a prefix and a unit. However the unit (D) was not found', str(context.exception))

    def testConvertFromSI(self):
        A = unit()
        a, b = A.convertFromSI(1, 'L/min')
        self.assertEqual(a, 1 * 1000 * 60)
        self.assertEqual(b, 'L/min')

        a, b = A.convertFromSI(1, 'bar-kg/h2-L3')
        self.assertAlmostEqual(a, 1 / 100000 / 1 / 1 * (60 * 60)**2 / (1000)**3)
        self.assertEqual(A.assertEqual(b, 'bar-kg/h2-L3'), True)

        with self.assertRaises(Exception) as context:
            a, b = A.convertFromSI(1, 'aL')
        self.assertEqual(f'The unit (aL) was not found. Therefore it was interpreted as a prefix and a unit. However the prefix (a) was not found', str(context.exception))

        with self.assertRaises(Exception) as context:
            a, b = A.convertFromSI(1, 'mD')
        self.assertEqual(f'The unit (mD) was not found. Therefore it was interpreted as a prefix and a unit. However the unit (D) was not found', str(context.exception))

    def testRemoveExponentFromUnit(self):
        A = unit()
        a = 'L2'
        a, b = A._removeExponentFromUnit(a)
        self.assertEqual(a, 'L')
        self.assertEqual(b, 2)

        with self.assertRaises(Exception) as context:
            A._removeExponentFromUnit('3L')
        self.assertEqual('Any number has to be placed at the end of the unit', str(context.exception))

        with self.assertRaises(Exception) as context:
            A._removeExponentFromUnit('3L2')
        self.assertEqual('All numbers in the unit has to be grouped together', str(context.exception))

    def testSplitCompositeUnit(self):
        A = unit()
        a = 'L2-kg/s-m3'
        b, c = A._splitCompositeUnit(a)
        self.assertEqual(b, ['L2', 'kg'])
        self.assertEqual(c, ['s', 'm3'])

        with self.assertRaises(Exception) as context:
            A._splitCompositeUnit('L-kg./min')
        self.assertEqual('The unit can only contain slashes (/), hyphens (-)', str(context.exception))

        with self.assertRaises(Exception) as context:
            A._splitCompositeUnit('L/kg/min')
        self.assertEqual('A unit can only have a single slash (/)', str(context.exception))

    def testCancleDifferentiUnits(self):
        A = unit()
        self.assertTrue(A.assertUnitsSI('m3/h-mm2', 'm/s'))


if __name__ == '__main__':
    unittest.main()
