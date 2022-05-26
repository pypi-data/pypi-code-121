import os
import unittest

def run_pytest():
    import pytest
    path = os.path.join(os.path.dirname(__file__), "..")
    return pytest.main([path, ])


class TestAll(unittest.TestCase):
    
    def test_pytest(self):
        self.assertEqual(run_pytest(), 0)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestAll('test_pytest'))
    return suite


if __name__ == "__main__":
    # Be sure to be on the top level directory of cosapp package

    # Optional dependency
    import coverage

    cover = coverage.Coverage()
    cover.start()
    result = run_pytest()
    cover.stop()
    cover.save()

    if result == 0:
        try:
            cover.report()
            cover.html_report()
        except coverage.misc.CoverageException as err:
            print(repr(err))
    else:
        exit(1)
