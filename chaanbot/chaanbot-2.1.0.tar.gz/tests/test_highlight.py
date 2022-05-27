from unittest import IsolatedAsyncioTestCase
from unittest.mock import Mock, AsyncMock

from chaanbot.matrix import Matrix
from chaanbot.modules.highlight import Highlight


class TestHighlight(IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        database = Mock()
        self.matrix = AsyncMock(Matrix)
        self.room = AsyncMock()
        self.event = Mock()
        self.event.sender = "sender_user_id"
        self.highlight = Highlight(None, self.matrix, database, None)

    async def test_not_ran_if_wrong_command(self):
        ran = await self.highlight.run(self.room, None, "highlight")
        self.assertFalse(ran)

    def test_config_has_properties(self):
        self.assertLess(0, len(self.highlight.operations))
        self.assertFalse(self.highlight.always_run)

    async def test_highlight_all_without_text(self):
        user = Mock()
        user.user_id = "user1"
        self.room.users = {user.user_id: user}

        expected_send_message = "user1"

        await self.highlight.run(self.room, self.event, "!hlall")

        self.matrix.send_text_to_room.assert_called_with(expected_send_message, self.room.room_id)

    async def test_highlight_all_with_text(self):
        user = Mock()
        user.user_id = "user1"
        self.room.users = {user.user_id: user}

        argument = "helloes"
        expected_send_message = "user1: helloes"

        await self.highlight.run(self.room, self.event, "!hlall " + argument)

        self.matrix.send_text_to_room.assert_called_with(expected_send_message, self.room.room_id)

    async def test_dont_highlight_all_if_none_to_highlight(self):
        self.room.users = {}

        argument = "helloes"
        expected_send_message = "No users to highlight"

        await self.highlight.run(self.room, self.event, "!hlall " + argument)

        self.matrix.send_text_to_room.assert_called_with(expected_send_message, self.room.room_id)

    async def test_dont_highlight_sender_in_highlight_all(self):
        user = Mock()
        user.user_id = self.event.sender
        self.room.users = {user.user_id: user}

        argument = "helloes"
        expected_send_message = "No users to highlight"

        await self.highlight.run(self.room, self.event, "!hlall " + argument)

        self.matrix.send_text_to_room.assert_called_with(expected_send_message, self.room.room_id)

    async def test_highlight_without_text(self):
        conn = Mock()
        self._mock_get_member(conn, [["user1"]])
        self._mock_get_user("user1")

        expected_send_message = "user1"

        await self.highlight.run(self.room, self.event, "!hl group")

        self.matrix.send_text_to_room.assert_called_with(expected_send_message, self.room.room_id)
        conn.execute.assert_called_once()

    async def test_should_not_run_highlight_operation_if_missing_group_argument(self):
        conn = Mock()
        self._mock_get_member(conn, [["user1"]])
        self._mock_get_user("user1")

        await self.highlight.run(self.room, self.event, "!hl")

        self.matrix.send_text_to_room.assert_not_called()
        conn.execute.assert_not_called()

    async def test_highlight_with_text(self):
        conn = Mock()
        self._mock_get_member(conn, [["user1"]])
        self._mock_get_user("user1")

        expected_send_message = "user1: helloes"

        await self.highlight.run(self.room, self.event, "!hl group helloes")

        self.matrix.send_text_to_room.assert_called_with(expected_send_message, self.room.room_id)
        conn.execute.assert_called_once()

    def _get_user_side_effect(*args, **kwargs):
        online_user = Mock()
        online_user.user_id = "online_user"
        offline_user = Mock()
        offline_user.user_id = "offline_user"
        if args[2] == "online_user":
            return online_user
        elif args[2] == "offline_user":
            return offline_user

    async def test_no_members_for_highlight(self):
        conn = Mock()
        self._mock_get_member(conn, [])

        expected_send_message = "Group \"group\" does not have any members to highlight"

        await self.highlight.run(self.room, self.event, "!hl group")

        self.matrix.send_text_to_room.assert_called_with(expected_send_message, self.room.room_id)
        conn.execute.assert_called_once()

    async def test_dont_highlight_sender_in_highlight(self):
        conn = Mock()
        self._mock_get_member(conn, [self.event.sender])
        self._mock_get_user(self.event.sender)

        expected_send_message = "Group \"group\" does not have any members to highlight"

        await self.highlight.run(self.room, self.event, "!hl group")

        self.matrix.send_text_to_room.assert_called_with(expected_send_message, self.room.room_id)
        conn.execute.assert_called_once()

    async def test_successfully_adding_members_to_case_insensitive_group(self):
        conn = Mock()
        self._mock_is_in_group(conn, None)
        self._mock_get_user("user1")

        expected_send_message = "Added \"user1\" to group \"group\""

        await self.highlight.run(self.room, self.event, "!hla GRouP user1")

        self.matrix.send_text_to_room.assert_called_with(expected_send_message, self.room.room_id)

    async def test_dont_add_to_group_if_already_member(self):
        conn = Mock()
        self._mock_is_in_group(conn, "user1")
        self._mock_get_user("user1")

        expected_send_message = "Could not add \"user1\" to group \"group\""

        await self.highlight.run(self.room, self.event, "!hla group user1")

        self.matrix.send_text_to_room.assert_called_with(expected_send_message, self.room.room_id)

    async def test_dont_add_to_group_if_not_in_room(self):
        self.highlight.matrix.get_user.return_value = None

        expected_send_message = "User: \"user1\" is not in room"

        await self.highlight.run(self.room, self.event, "!hla group user1")

        self.matrix.send_text_to_room.assert_called_with(expected_send_message, self.room.room_id)

    async def test_successfully_deleting_members_from_case_insensitive_group(self):
        conn = Mock()
        self._mock_is_in_group(conn, "user1")
        self._mock_get_user("user1")

        expected_send_message = "Removed \"user1\" from group \"group\""

        await self.highlight.run(self.room, self.event, "!hld gROUp user1")

        self.matrix.send_text_to_room.assert_called_with(expected_send_message, self.room.room_id)

    async def test_dont_delete_from_group_if_not_member(self):
        conn = Mock()
        self._mock_is_in_group(conn, None)
        self._mock_get_user("user1")

        expected_send_message = "Could not remove \"user1\" from group \"group\""

        await self.highlight.run(self.room, self.event, "!hld group user1")

        self.matrix.send_text_to_room.assert_called_with(expected_send_message, self.room.room_id)

    def _mock_get_user(self, user_id):
        user = Mock()
        user.user_id = user_id
        self.highlight.matrix.get_user.return_value = user

    def _mock_is_in_group(self, conn, return_value):
        self.highlight.database.connect.return_value = conn
        conn.__enter__ = Mock(return_value=conn)
        conn.__exit__ = Mock(return_value=None)
        result = Mock()
        conn.execute.return_value = result
        result.fetchone.return_value = return_value

    def _mock_get_member(self, conn, members):
        self.highlight.database.connect.return_value = conn

        rows = Mock()
        conn.execute.return_value = rows
        rows.fetchall.return_value = members
