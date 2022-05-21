#cheese

from Cheese.testError import TestError

class UnitTest:

    @staticmethod
    def assertEqual(value, template, comment):
        if (value != template):
            raise TestError(value, template, comment)

    @staticmethod
    def assertTrue(value, comment):
        UnitTest.assertEqual(value, True, comment)

    @staticmethod
    def assertFalse(value, comment):
        UnitTest.assertEqual(value, False, comment)