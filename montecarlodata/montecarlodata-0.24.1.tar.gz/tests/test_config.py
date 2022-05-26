import configparser
from collections import OrderedDict
from unittest import TestCase
from unittest.mock import Mock, patch, mock_open, call

from montecarlodata.config import Config, ConfigManager

_SAMPLE_PROFILE_NAME = 'foo'
_SAMPLE_BASE_PATH = 'bar'
_SAMPLE_FILE = f'{_SAMPLE_BASE_PATH}/profiles.ini'
_SAMPLE_OPTIONS = OrderedDict({
    'mcd_id': '1234',
    'mcd_token': 'a-test-token-with-fifty-six-characters-for-verifications',
    'mcd_api_endpoint': 'https://api.getmontecarlo.com/graphql',
    'aws_profile': 'foo',
    'aws_region': 'home'
})


class ConfigTest(TestCase):
    def setUp(self) -> None:
        self._parser_mock = Mock()

        self._service = ConfigManager(
            profile_name=_SAMPLE_PROFILE_NAME,
            base_path=_SAMPLE_BASE_PATH,
            config_parser=self._parser_mock
        )

    def test_setup(self):
        self._parser_mock.read.assert_called_once_with(_SAMPLE_FILE)

    @patch('montecarlodata.config.mkdirs')
    @patch('builtins.open', new_callable=mock_open, read_data='data')
    def test_write(self, mock_file, create_directory_mock):
        self._parser_mock.sections.return_value = []
        self._service.write(**_SAMPLE_OPTIONS)

        self._parser_mock.add_section.assert_called_once_with(_SAMPLE_PROFILE_NAME)

        self._parser_mock.set.assert_has_calls([
            call(_SAMPLE_PROFILE_NAME, k, v) for k, v in _SAMPLE_OPTIONS.items()
        ])

        mock_file.assert_called_once_with(_SAMPLE_FILE, 'w')
        create_directory_mock.assert_called_once_with(_SAMPLE_BASE_PATH)

    @patch('montecarlodata.errors.echo_error')
    @patch('montecarlodata.config.mkdirs')
    @patch('builtins.open', new_callable=mock_open, read_data='data')
    def test_write_invalid_token(self, mock_file, create_directory_mock, mock_echo):
        self._parser_mock.sections.return_value = []
        INVALID_SHORT_TOKEN = 'invalid-short-token'

        self._service.write(**{**_SAMPLE_OPTIONS, 'mcd_token': INVALID_SHORT_TOKEN})
        mock_echo.assert_called_once()

        self._parser_mock.add_section.assert_called_once_with(_SAMPLE_PROFILE_NAME)
        self._parser_mock.set.called_once_with(_SAMPLE_PROFILE_NAME, 'mcd_token', INVALID_SHORT_TOKEN)

        mock_file.assert_not_called()
        create_directory_mock.assert_not_called()

    def test_read(self):
        self._parser_mock.get.side_effect = _SAMPLE_OPTIONS.values()
        self.assertEqual(self._service.read(), Config(**_SAMPLE_OPTIONS))

    def test_read_with_no_section(self):
        self._parser_mock.get.side_effect = configparser.NoSectionError(_SAMPLE_PROFILE_NAME)
        self.assertIsNone(self._service.read())
