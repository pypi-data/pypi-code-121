from unittest import TestCase

from holour import json_encode, json_decode
from holour.msg import Script, WaypointConfig


class Test(TestCase):

    def setUp(self) -> None:
        self.script = Script('test.script', "/")
        self.wp = WaypointConfig(show_waypoints=True, show_current_waypoint=True)

    def test_script_encode(self):
        script_string = json_encode(self.script)
        expected_string = '{"_type": "script", "filename": "test.script", "path": "/"}'

        assert type(script_string) == str, f"Got: {type(script_string)}. Expected {str}"
        assert script_string == expected_string, f"Expected {expected_string}, got: {script_string}"

    def test_script_decode(self):
        script_string = json_encode(self.script)
        script_decoded = json_decode(script_string)

        assert type(script_decoded) == Script, f"Got: {type(script_decoded)}. Expected {Script}"
        assert script_decoded == self.script, "Should be equal"

    def test_script_equals(self):
        same_script = Script('test.script', "/")
        diff_script = Script('test.script', "/new path")

        assert self.script == same_script
        assert self.script != diff_script
        assert self.script != "just a string"

    def test_script_repr(self):
        expected, got = 'test.script', f'{self.script}'
        assert expected in got, f"Expected {expected} in got: {got}"

    def test_waypoint_config_encode(self):
        wp_string = json_encode(self.wp)
        expected_string = '{"_type": "waypoint_config", "show_waypoints": true, "show_current_waypoint": true}'

        assert type(wp_string) == str, f"Got: {type(wp_string)}. Expected {str}"
        assert wp_string == expected_string, f"Expected {expected_string}, got: {wp_string}"

    def test_waypoint_config_decode(self):
        wp_string = json_encode(self.wp)
        wp_decoded = json_decode(wp_string)

        assert type(wp_decoded) == WaypointConfig, f"Got: {type(wp_decoded)}. Expected {WaypointConfig}"
        assert wp_decoded == self.wp, "Should be equal"

    def test_waypoint_config_equals(self):
        same_wp = WaypointConfig(True, True)
        diff_wp = WaypointConfig(False, True)

        assert self.wp == same_wp
        assert self.wp != diff_wp
        assert self.wp != "just a string"

    def test_waypoint_config_repr(self):
        expected, got = 'show_waypoints', f'{self.wp}'
        assert expected in got, f"Expected {expected} in got: {got}"
