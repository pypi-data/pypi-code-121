import sys
from io import StringIO
import unittest

from findhelp.finder import go_search
from setup_files import setup_tests
from tear_down import tear_down_tests


def main(out=sys.stderr, verbosity=2):
    loader = unittest.TestLoader()

    suite = loader.loadTestsFromModule(sys.modules[__name__])
    unittest.TextTestRunner(out, verbosity=verbosity).run(suite)


class ConsoleTests(unittest.TestCase):
    capturedOutput = StringIO()
    sys.stdout = capturedOutput

    # sys.stdout = sys.__stdout__
    # print("Captured", capturedOutput.getvalue())
    @classmethod
    def setUpClass(cls):
        setup_tests()

    @classmethod
    def tearDownClass(cls):
        tear_down_tests()

    def test_search_one(self):
        base_dict = {
            "stringsearch": "one",
        }
        result = go_search(base_dict)
        self.assertEqual(result, 5)

    def test_search_nothing(self):

        base_dict = {
            "stringsearch": "nothing_to_match",
        }
        result = go_search(base_dict)
        self.assertEqual(result, 0)


if __name__ == "__main__":
    with open('test_console_results.txt', 'w') as f:
        main(f)
