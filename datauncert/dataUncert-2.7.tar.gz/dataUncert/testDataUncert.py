import logging
logging.disable(logging.CRITICAL)
import unittest
from dataUncert.testFit import test as testFit
from dataUncert.testReadData import test as testReadData
from dataUncert.testUnitSystem import test as testUnitSystem
from dataUncert.testVariable import test as testVariable


def main():
    tests = [
        testFit,
        testReadData,
        testUnitSystem,
        testVariable
    ]

    suites = []
    for test in tests:
        suites.append(unittest.TestLoader().loadTestsFromTestCase(test))

    suite = unittest.TestSuite(suites)
    runner = unittest.TextTestRunner()
    runner.run(suite)


if __name__ == '__main__':
    main()
