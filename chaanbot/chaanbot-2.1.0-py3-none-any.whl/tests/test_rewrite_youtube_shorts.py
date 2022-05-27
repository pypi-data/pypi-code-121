import os
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, Mock

from chaanbot.modules.rewrite_youtube_shorts import RewriteYoutubeShorts


class TestAlive(IsolatedAsyncioTestCase):
    config_prefix_message = "prefix "

    def setUp(self) -> None:
        config = Mock()
        config.get.return_value = self.config_prefix_message
        self.event = Mock()
        self.event.sender = "user_id"
        self.room = AsyncMock()
        self.room.room_id = 1234
        self.matrix = AsyncMock()
        self.module = RewriteYoutubeShorts(config, self.matrix, Mock(), None)

    async def test_rewrite_normal_short(self):
        ran = await self.module.run(self.room, None, "Check this out: https://www.youtube.com/shorts/6j6ksOu1231")

        self.assertFalse(ran)
        self.matrix.send_text_to_room.assert_any_call(
            self.config_prefix_message + "https://www.youtube.com/watch?v=6j6ksOu1231",
            self.room.room_id)

    async def test_rewrite_several_shorts(self):
        ran = await self.module.run(self.room, None,
                                    "Check these out: http://www.youtube.com/shorts/6j6ksOu1231 "
                                    "and https://youtube.com/shorts/6j6ksOu1232 great huh?")

        self.assertFalse(ran)
        self.matrix.send_text_to_room.assert_any_call(
            self.config_prefix_message + "http://www.youtube.com/watch?v=6j6ksOu1231"
            + os.linesep + "https://youtube.com/watch?v=6j6ksOu1232",
            self.room.room_id)

    async def test_dont_rewrite_non_youtube(self):
        ran = await self.module.run(self.room, None, "Check this out: https://www.othertube.com/shorts/6j6ksOu1231")

        self.assertFalse(ran)
        self.matrix.send_text_to_room.assert_not_called()
