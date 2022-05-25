from unittest import TestCase

from holour import json_encode, json_decode
from holour.msg import Status


class Test(TestCase):

    def test_status(self):
        status = Status('data_objects', '127.0.0.1', Status.OFFLINE)
        status_string = json_encode(status)
        expected_string = '{"_type": "status", "id": "data_objects", "ip": "127.0.0.1", "status": "offline"}'

        assert type(status_string) == str
        assert status_string == expected_string, f"Expected {expected_string}, got: {status_string}"

        status_decoded = json_decode(status_string)
        assert type(status_decoded) == Status, f"Got: {type(status_decoded)}. Expected {Status}"
        assert status_decoded == status, "The decoded object must be equal to the encoded"

    def test_status_equals(self):
        s1 = Status('data_objects', '127.0.0.1', Status.OFFLINE)
        s2 = Status('data_objects', '127.0.0.1', Status.OFFLINE)
        s3 = Status('data_objects', '127.0.0.1', Status.ONLINE)

        assert s1 == s2
        assert s1 != s3
        assert s1 != "not status"

    def test_status_repr(self):
        status = Status('data_objects', '127.0.0.1', Status.OFFLINE)
        expected, got = '127.0.0.1', f'{status}'

        assert expected in got, f"Expected {expected} in got: {got}"
