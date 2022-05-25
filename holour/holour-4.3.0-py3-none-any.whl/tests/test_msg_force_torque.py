from unittest import TestCase

from holour import json_encode, json_decode
from holour.msg import ForceTorque, Vector3


class Test(TestCase):

    def test_force_torque(self):
        force = Vector3(1, 2, 3)
        torque = Vector3(-1.1, -1.2, 1.3)
        ft = ForceTorque(force, torque)
        ft_string = json_encode(ft)

        expected_string = '{"_type": "force_torque", "force": {"_type": "vector3", "x": 1, "y": 2, "z": 3}, "torque": '\
                          '{"_type": "vector3", "x": -1.1, "y": -1.2, "z": 1.3}}'
        assert type(ft_string) == str
        assert ft_string == expected_string, f"Expected: {expected_string}, got: {ft_string}"

        ft_decoded: ForceTorque = json_decode(ft_string)
        assert type(ft_decoded) == ForceTorque, f"Expected object of type {ForceTorque}"
        assert ft_decoded.force == force
        assert ft_decoded.torque == torque
        assert ft_decoded == ft

    def test_equals(self):
        ft1 = ForceTorque(Vector3(1, 2, 3), Vector3(-1.1, -1.2, 1.3))
        ft2 = ForceTorque(Vector3(1, 2, 3), Vector3(-1.1, -1.2, 1.3))
        ft3 = ForceTorque(Vector3(3000, 2, 3), Vector3(-1.1, -1.2, 1.3))

        assert ft1 == ft2
        assert ft1 != ft3
        assert ft1 != "hej"

    def test_ft_repr(self):
        ft = ForceTorque(Vector3(1, 2, 3), Vector3(-1.1, -1.2, 1.3))
        expected, got = f'x=1', f'{ft}'
        assert expected in got, f"Expected {expected} in got: {got}"
