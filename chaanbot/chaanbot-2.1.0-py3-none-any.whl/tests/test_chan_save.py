from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch, mock_open, AsyncMock, Mock

from chaanbot.modules.chan_save import ChanSave


class TestChanSave(IsolatedAsyncioTestCase):
    url_to_access_saved_files = "https://location/i/"
    save_dirpath = "/dir/to/save"
    event = {"sender": "user_id"}
    link = "https://4chan.org/g/stallman.jpg"
    sha1_hash_of_link = "5e323b28aa4445bf42f9359ce7b66cbcb12f3c89"

    @patch('os.access', return_value=True)
    async def asyncSetUp(self, mock_os_access) -> None:
        config = Mock()
        config.get.side_effect = self.get_config_side_effect
        self.requests = Mock()
        self.room = AsyncMock()
        self.matrix = AsyncMock()
        self.chan_save = ChanSave(config, self.matrix, AsyncMock(), self.requests)

    async def test_config_has_properties(self):
        self.assertTrue(self.chan_save.always_run)
        self.assertIsNotNone(self.chan_save.url_to_access_saved_files)
        self.assertIsNotNone(self.chan_save.save_dirpath)
        self.assertFalse(hasattr(self.chan_save, "disabled"))

    @patch('os.access', return_value=True)
    async def test_disabled_if_no_save_dirpath(self, mock_os_access):
        config = Mock()
        config.get.side_effect = self.get_config_side_effect_without_save_dirpath
        chan_save = ChanSave(config, AsyncMock(), AsyncMock(), self.requests)
        self.assertTrue(chan_save.disabled)

    @patch('os.access', return_value=True)
    async def test_enabled_if_no_url_to_access_saved_files(self, mock_os_access):
        config = Mock()
        config.get.side_effect = self.get_config_side_effect_without_url_to_access_saved_files
        chan_save = ChanSave(config, AsyncMock(), AsyncMock(), self.requests)
        self.assertFalse(hasattr(chan_save, "disabled"))

    @patch('os.access', return_value=False)  # No write access
    async def test_disabled_if_no_write_access(self, mock_os_access):
        config = Mock()
        config.get.side_effect = self.get_config_side_effect
        chan_save = ChanSave(config, AsyncMock(), AsyncMock(), self.requests)
        self.assertTrue(chan_save.disabled)

    @patch("builtins.open", new_callable=mock_open)
    async def test_save_4chan_media_and_send_URL(self, mock_open):
        await self.chan_save.run(self.room, self.event, self.link)

        expected_message = "File saved to {}{}{} .".format(self.chan_save.url_to_access_saved_files,
                                                           self.sha1_hash_of_link, ".jpg")
        self.matrix.send_text_to_room.assert_called_with(expected_message, self.room.room_id)
        self.requests.get.assert_called_once()
        mock_open().write.assert_called_once()

    @patch("builtins.open", new_callable=mock_open)
    @patch('os.access', return_value=True)
    async def test_save_4chan_media_and_dont_send_URL(self, mock_os_access, mock_open):
        config = Mock()
        config.get.side_effect = self.get_config_side_effect_without_url_to_access_saved_files
        chan_save = ChanSave(config, AsyncMock(), AsyncMock(), self.requests)

        await chan_save.run(self.room, self.event, self.link)

        self.requests.get.assert_called_once()
        mock_open().write.assert_called_once()
        self.room.send_text.assert_not_called()

    @patch('os.path.exists', return_value=True)  # Called when checking if the file exists
    @patch("builtins.open", new_callable=mock_open)
    @patch('os.access', return_value=True)
    async def test_dont_save_if_already_exists(self, mock_os_access, mock_open, mock_file_exists):
        config = Mock()
        config.get.side_effect = self.get_config_side_effect_without_url_to_access_saved_files
        chan_save = ChanSave(config, AsyncMock(), AsyncMock(), self.requests)

        await chan_save.run(self.room, self.event, self.link)

        self.requests.get.assert_not_called()
        mock_open().write.assert_not_called()
        self.room.send_text.assert_not_called()

    async def test_dont_save_media_if_unsupported_file_extension(self):
        await self.chan_save.run(self.room, self.event, "https://4chan.org/g/stallman.what")

        self.room.send_text.assert_not_called()
        self.requests.get.assert_not_called()

    async def test_dont_save_media_and_send_location_if_not_support_4chan_link(self):
        await self.chan_save.run(self.room, self.event, "https://4chun.org/g/stallman.jpg")

        self.room.send_text.assert_not_called()
        self.requests.get.assert_not_called()

    def get_config_side_effect(*args, **kwargs):
        if args[1] == "chan_save":
            if args[2] == "url_to_access_saved_files":
                return "url_to_access_saved_files"
            elif args[2] == "save_dirpath":
                return "save_dirpath"
        return None

    def get_config_side_effect_without_save_dirpath(*args, **kwargs):
        if args[1] == "chan_save":
            if args[2] == "url_to_access_saved_files":
                return "url_to_access_saved_files"
        return None

    def get_config_side_effect_without_url_to_access_saved_files(*args, **kwargs):
        if args[1] == "chan_save":
            if args[2] == "save_dirpath":
                return "save_dirpath"
        return None
