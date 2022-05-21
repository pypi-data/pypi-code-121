import unittest

from fluentcheck import Is
from fluentcheck.exceptions import CheckError


class TestIsListsAssertions(unittest.TestCase):

    def test_is_contains_list_chars_only_pass(self):
        obj = ["goodbye","apple"]
        char = "apple"
        with self.assertRaises(CheckError):
            Is(obj).contains_char(char)
