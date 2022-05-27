from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock

from chaanbot.modules.alive import Alive


class TestAlive(IsolatedAsyncioTestCase):

    async def test_send_alive_to_room(self):
        room = AsyncMock()
        room.room_id = 1234
        matrix = AsyncMock()
        matrix.matrix_client.rooms = {"room": "room1"}

        ran = await Alive(None, matrix, None, None).run(room, None, "!alive")

        self.assertTrue(ran)
        matrix.send_text_to_room.assert_any_call("Yes.", room.room_id)

    async def test_not_ran_if_wrong_command(self):
        room = AsyncMock()
        room.room_id = 1234
        matrix = AsyncMock()
        matrix.matrix_client.rooms = {"room": "room1"}

        ran = await Alive(None, matrix, None, None).run(room, None, "alive")
        self.assertFalse(ran)
        matrix.send_text_to_room.assert_not_called()

    async def test_config_has_properties(self):
        alive_class = Alive(None, None, None, None)
        self.assertLess(0, len(alive_class.operations))
        self.assertFalse(alive_class.always_run)

    async def test_should_run_returns_true_if_commands_match(self):
        alive_class = Alive(None, None, None, None)
        self.assertTrue(alive_class.should_run("!alive"))
        self.assertTrue(alive_class.should_run("!running"))

    async def test_should_run_returns_false_if_commands_do_not_match(self):
        alive_class = Alive(None, None, None, None)
        self.assertFalse(alive_class.should_run("alive!"))
