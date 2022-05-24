from io import BytesIO
from unittest import TestCase
from unittest.mock import patch

import requests_mock

from rebotics_sdk.providers import RetailerProvider, ProviderHTTPServiceException


@patch('time.sleep', new=lambda *args, **kwargs: None)
class ProcessingUpload(TestCase):
    def setUp(self) -> None:
        self.file_io = BytesIO()
        self.provider = RetailerProvider(host='http://test.com')

    @patch('rebotics_sdk.providers.base.ProviderRequestProxy.format_return_data')
    def test_processing_upload(self, mock_func):
        with requests_mock.Mocker() as m:
            m.post('http://test.com/api/v4/processing/upload/')
            with patch.object(self.file_io, 'seek') as mock_file:
                self.provider.processing_upload(store_id=1, input_file=self.file_io)
                self.assertEqual(2, mock_file.call_count)

    @patch('rebotics_sdk.providers.base.ProviderRequestProxy.format_return_data')
    def test_processing_upload_with_empty_files(self, mock_func):
        with requests_mock.Mocker() as m:
            m.post('http://test.com/api/v4/processing/upload/', status_code=502)
            with patch.object(self.file_io, 'seek') as mock_file:
                with self.assertRaises(ProviderHTTPServiceException) as error:
                    self.provider.processing_upload(store_id=1, input_file=self.file_io)
            self.assertEqual(7, mock_file.call_count)
            self.assertTrue('Failed to do request after ' in error.exception.args[0])
