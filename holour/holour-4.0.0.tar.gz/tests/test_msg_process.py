from unittest import TestCase

from holour import json_encode, json_decode
from holour.msg import Process, ProcessMessage


class Test(TestCase):

    def test_process(self):
        process = Process('uuid_1', 'build house', ['task_1', 'task_2'], "Build a beautiful house.")
        process_string = json_encode(process)
        expected_string = '{"_type": "process", "uuid": "uuid_1", "name": "build house", ' \
                          '"tasks": ["task_1", "task_2"], "description": "Build a beautiful house."}'

        self.assertIsInstance(process_string, str)
        self.assertEqual(process_string, expected_string, f"Expected {expected_string}, got: {process_string}")

        process_decoded = json_decode(process_string)
        assert type(process_decoded) == Process, f"Got: {type(process_decoded)}. Expected {Process}"
        assert process_decoded == process, "The decoded object must be equal to the encoded"

    def test_task_equals(self):
        t1 = Process('uuid_1', 'build house', ['task_1', 'task_1'], "Build a beautiful house.")
        t2 = Process('uuid_1', 'build house', ['task_1', 'task_1'], "Build a beautiful house.")
        t3 = Process('uuid_2', 'build house', ['task_1', 'task_1'])

        assert t1 == t2
        assert t1 != t3
        assert t1 != "not status"

    def test_task_repr(self):
        process = Process('uuid_1', 'build house', ['task_1', 'task_1'], "Build a beautiful house.")
        expected, got = 'Build a beautiful house.', f'{process}'

        assert expected in got, f"Expected {expected} in got: {got}"

    def test_sub_tasks_or_operations(self):
        with self.assertRaises(ValueError):
            Process('uuid_1', 'task_1', [])


class TestProcessMessage(TestCase):

    def test_process_message(self):
        process_message = ProcessMessage('uuid', 'hej')
        process_message_string = json_encode(process_message)
        expected_string = '{"_type": "process_message", "process_uuid": "uuid", "message": "hej"}'

        assert type(process_message_string) == str
        assert process_message_string == expected_string, f"Expected {expected_string}, got: {process_message_string}"

        process_message_decoded = json_decode(process_message_string)
        assert type(process_message_decoded) == ProcessMessage, f"Got: {type(process_message_decoded)}. Expected {ProcessMessage}"
        assert process_message_decoded == process_message, "The decoded object must be equal to the encoded"

    def test_process_message_equals(self):
        at1 = ProcessMessage('uuid', 'hej')
        at2 = ProcessMessage('uuid', 'hej')
        at3 = ProcessMessage('uuid2', '')

        assert at1 == at2
        assert at1 != at3
        assert at1 != "not status"

    def test_process_message_repr(self):
        add_task = ProcessMessage('uuid', '')
        expected, got = 'uuid', f'{add_task}'

        assert expected in got, f"Expected {expected} in got: {got}"
