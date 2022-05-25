from unittest import TestCase

from holour import json_encode, json_decode
from holour.msg import ProgramState


class Test(TestCase):

    def test_program_state(self):
        program_state = ProgramState(ProgramState.START)
        program_state_string = json_encode(program_state)
        expected_string = '{"_type": "program_state", "program_state": "start"}'

        self.assertIs(type(program_state_string), str, f"Got: {type(program_state_string)}. Expected {str}")
        self.assertEqual(program_state_string, expected_string, f"Expected {expected_string}, got: {program_state_string}")

        program_string_decoded = json_decode(program_state_string)
        assert type(program_string_decoded) == ProgramState, f"Got: {type(program_string_decoded)}. Expected {ProgramState}"
        assert program_string_decoded == program_state, "The decoded object must be equal to the encoded"

    def test_program_state_equals(self):
        ps1 = ProgramState(ProgramState.START)
        ps2 = ProgramState(ProgramState.START)
        ps3 = ProgramState(ProgramState.PAUSE)

        assert ps1 == ps2
        assert ps1 != ps3
        assert ps1 != "not status"

    def test_program_state_repr(self):
        ps = ProgramState(ProgramState.START)
        expected, got = 'start', f'{ps}'

        assert expected in got, f"Expected {expected} in got: {got}"

