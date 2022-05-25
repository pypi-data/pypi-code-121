from unittest import TestCase

from holour import json_encode, json_decode
from holour.msg import RobotState, RobotStateChange, JointAngles, GripperPosition


class TestRobotState(TestCase):

    def test_robot_state(self):
        robot_state = RobotState("Playing", True, True, 0.5, 1)
        robot_state_string = json_encode(robot_state)
        expected_string = '{"_type": "robot_state", "state": "Playing", "moving": true, "active": true, "target_speed": 0.5, "actual_speed": 1}'

        self.assertIs(type(robot_state_string), str, f"Got: {type(robot_state_string)}. Expected {str}")
        self.assertEqual(robot_state_string, expected_string, f"Expected {expected_string}, got: {robot_state_string}")

        robot_state_string_decoded = json_decode(robot_state_string)
        assert type(robot_state_string_decoded) == RobotState, f"Got: {type(robot_state_string_decoded)}. Expected {RobotState}"
        assert robot_state_string_decoded == robot_state, "The decoded object must be equal to the encoded"

    def test_robot_state_equals(self):
        ps1 = RobotState("Paused", False, False, 1, 1)
        ps2 = RobotState("Paused", False, False, 1, 1)
        ps3 = RobotState("Pausing", True, False, 1, 1)

        assert ps1 == ps2
        assert ps1 != ps3
        assert ps1 != "not status"

    def test_robot_state_repr(self):
        ps = RobotState("Stopping", True, False, 1, 1)
        expected, got = 'actual', f'{ps}'

        assert expected in got, f"Expected {expected} in got: {got}"


class TestRobotStateChange(TestCase):

    def test_robot_state_change(self):
        robot_state_change = RobotStateChange(RobotStateChange.START, 1)
        robot_state_string = json_encode(robot_state_change)
        expected_string = '{"_type": "robot_state_change", "state": "start", "speed": 1}'

        self.assertIs(type(robot_state_string), str, f"Got: {type(robot_state_string)}. Expected {str}")
        self.assertEqual(robot_state_string, expected_string, f"Expected {expected_string}, got: {robot_state_string}")

        string_decoded = json_decode(robot_state_string)
        assert type(string_decoded) == RobotStateChange, f"Got: {type(string_decoded)}. Expected {RobotStateChange}"
        assert string_decoded == robot_state_change, "The decoded object must be equal to the encoded"


class TestJointAngles(TestCase):

    def test_joint_angles(self):
        joint_angles = JointAngles(1, 2, 3, 4, 5, 6, 7)
        joint_angles_string = json_encode(joint_angles)
        expected_string = '{"_type": "joint_angles", "joint1": 1, "joint2": 2, "joint3": 3, "joint4": 4, "joint5": 5, "joint6": 6, "joint7": 7}'

        self.assertIs(type(joint_angles_string), str, f"Got: {type(joint_angles_string)}. Expected {str}")
        self.assertEqual(joint_angles_string, expected_string, f"Expected {expected_string}, got: {joint_angles_string}")

        string_decoded = json_decode(joint_angles_string)
        assert type(string_decoded) == JointAngles, f"Got: {type(string_decoded)}. Expected {JointAngles}"
        assert string_decoded == joint_angles, "The decoded object must be equal to the encoded"


class TestGripperPosition(TestCase):

    def test_gripper_position(self):
        gripper_position = GripperPosition(0.5)
        gp_string = json_encode(gripper_position)
        expected_string = '{"_type": "gripper_position", "position": 0.5}'

        self.assertIs(type(gp_string), str, f"Got: {type(gp_string)}. Expected {str}")
        self.assertEqual(gp_string, expected_string, f"Expected {expected_string}, got: {gp_string}")

        string_decoded = json_decode(gp_string)
        assert type(string_decoded) == GripperPosition, f"Got: {type(string_decoded)}. Expected {GripperPosition}"
        assert string_decoded == gripper_position, "The decoded object must be equal to the encoded"
