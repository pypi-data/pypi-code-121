from unittest import TestCase

from holour import json_encode, json_decode
from holour.msg import Task, Pose, Vector3, TaskMessage


class Test(TestCase):

    def test_task(self):

        task = Task('uuid', 'name', 'product_uuid', Pose(Vector3(0.0, 0.0, 0.0), Vector3(0.0, 0.0, 0.0)),
                    [Task.ASSIGNED_TO_HUMAN], Task.ASSIGNED_TO_HUMAN)
        task_string = json_encode(task)
        expected_string = '{"_type": "task", "uuid": "uuid", "name": "name", "product_uuid": "product_uuid", ' \
                          '"pose": {"_type": "pose", "name": "", "position": {"_type": "vector3", "x": 0.0, ' \
                          '"y": 0.0, "z": 0.0}, "rotation": {"_type": "vector3", "x": 0.0, "y": 0.0, "z": 0.0}' \
                          ', "axis_angle": {"_type": "axis_angle", "angle": 0.0, "x": 1, "y": 0, "z": 0}}, ' \
                          '"agents": ["human"], "assigned_to": "human", "conditions": [], ' \
                          '"conditions_fulfilled": true, "can_undo": false, "description": "", "status": "waiting"}'

        self.assertIs(type(task_string), str, f"Got: {type(task_string)}. Expected {str}")
        self.assertEqual(task_string, expected_string, f"Expected {expected_string}, got: {task_string}")

        task_decoded = json_decode(task_string)
        assert type(task_decoded) == Task, f"Got: {type(task_decoded)}. Expected {Task}"
        assert task_decoded == task, "The decoded object must be equal to the encoded"

    def test_task_equals(self):
        task1 = Task('uuid', 'name', 'product_uuid', Pose(Vector3(0.0, 0.0, 0.0), Vector3(0.0, 0.0, 0.0)),
                     [Task.ASSIGNED_TO_HUMAN], Task.ASSIGNED_TO_HUMAN)
        task2 = Task('uuid', 'name', 'product_uuid', Pose(Vector3(0.0, 0.0, 0.0), Vector3(0.0, 0.0, 0.0)),
                     [Task.ASSIGNED_TO_HUMAN], Task.ASSIGNED_TO_HUMAN)
        task3 = Task('other', 'name', 'product_uuid', Pose(Vector3(0.0, 0.0, 0.0), Vector3(0.0, 0.0, 0.0)),
                     [Task.ASSIGNED_TO_HUMAN], Task.ASSIGNED_TO_HUMAN)

        assert task1 == task2
        assert task1 != task3
        assert task1 != "not status"

    def test_task_repr(self):
        task = Task('uuid', 'name', 'product_uuid', Pose(Vector3(0.0, 0.0, 0.0), Vector3(0.0, 0.0, 0.0)),
                    [Task.ASSIGNED_TO_HUMAN], Task.ASSIGNED_TO_HUMAN, description="Hard task!")
        expected, got = 'Hard task!', f'{task}'

        assert expected in got, f"Expected {expected} in got: {got}"


class TestTaskMessage(TestCase):

    def test_task_message(self):
        task_message = TaskMessage('uuid', 'hej')
        task_message_string = json_encode(task_message)
        expected_string = '{"_type": "task_message", "task_uuid": "uuid", "message": "hej"}'

        assert type(task_message_string) == str
        assert task_message_string == expected_string, f"Expected {expected_string}, got: {task_message_string}"

        task_message_decoded = json_decode(task_message_string)
        assert type(task_message_decoded) == TaskMessage, f"Got: {type(task_message_decoded)}. Expected {TaskMessage}"
        assert task_message_decoded == task_message, "The decoded object must be equal to the encoded"

    def test_task_message_equals(self):
        at1 = TaskMessage('uuid', 'hej')
        at2 = TaskMessage('uuid', 'hej')
        at3 = TaskMessage('uuid2', '')

        assert at1 == at2
        assert at1 != at3
        assert at1 != "not status"

    def test_task_message_repr(self):
        add_task = TaskMessage('uuid', '')
        expected, got = 'uuid', f'{add_task}'

        assert expected in got, f"Expected {expected} in got: {got}"
