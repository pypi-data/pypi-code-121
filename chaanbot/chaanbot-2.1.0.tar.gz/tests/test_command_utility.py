import re
from unittest import TestCase

from chaanbot import command_utility


class TestCommandUtility(TestCase):

    def test_match_command_input_and_ignores_case(self):
        operations = {
            "cmd1": {
                "commands": ["!cmd1", "!cmd11"],
                "argument_regex": re.compile("hello", re.IGNORECASE)
            },
            "cmd2": {
                "commands": ["!cmd2", "!cmd22"],
                "argument_regex": re.compile("test", re.IGNORECASE)
            }
        }

        self.assertTrue(command_utility.matches(operations, "!cmd1 hello"))
        self.assertTrue(command_utility.matches(operations, "!cmd11 hello"))
        self.assertTrue(command_utility.matches(operations, "!cmd2 test"))
        self.assertTrue(command_utility.matches(operations, "!cmd22 test"))
        self.assertTrue(command_utility.matches(operations, "!cmD1 hello"))
        self.assertTrue(command_utility.matches(operations, "!CMD11 hello"))
        self.assertTrue(command_utility.matches(operations, "!Cmd2 test"))
        self.assertTrue(command_utility.matches(operations, "!cMd22 test"))

    def test_match_operation_input_and_ignores_case(self):
        operation = {
            "commands": ["!cmd1", "!cmd11"],
            "argument_regex": re.compile("hello", re.IGNORECASE)
        }

        self.assertTrue(command_utility.matches(operation, "!cmd1 hello"))
        self.assertTrue(command_utility.matches(operation, "!cmd11 hello"))
        self.assertTrue(command_utility.matches(operation, "!cMd1 hello"))
        self.assertTrue(command_utility.matches(operation, "!CMD11 hello"))

    def test_not_match_command_input(self):
        operations = {
            "operation": {
                "commands": ["!cmd1"],
                "argument_regex": "hello"
            }
        }

        self.assertFalse(command_utility.matches(operations, "!cmd2"))  # Should not match operation
        self.assertFalse(command_utility.matches(operations, "!cmd"))  # Should not partial match operation
        self.assertFalse(command_utility.matches(operations, "!cmd11"))  # Should not match longer operation
        self.assertFalse(command_utility.matches(None, "!cmd1"))  # Should not match None
        self.assertFalse(command_utility.matches(operations, None))  # Should not match None

    def test_get_command_and_argument(self):
        expected_command = "!command"
        expected_argument = "argument for command"
        message = expected_command + " " + expected_argument
        (command, argument) = command_utility.get_command_and_argument(message)
        self.assertEqual(expected_command, command)
        self.assertEqual(expected_argument, argument)
        self.assertEqual(expected_command, command_utility.get_command(message))
        self.assertEqual(expected_argument, command_utility.get_argument(message))

    def test_get_empty_string_if_no_argument(self):
        message_without_argument = "!test"
        self.assertEqual("", command_utility.get_argument(message_without_argument))
