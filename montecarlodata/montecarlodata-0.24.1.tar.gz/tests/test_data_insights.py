from unittest import TestCase
from unittest.mock import Mock, patch, call

import click
from box import BoxList, Box

from montecarlodata.common.data import MonolithResponse
from montecarlodata.insights.data_insights import InsightsService
from montecarlodata.queries.insights import GET_INSIGHTS, GET_INSIGHT_REPORT
from montecarlodata.utils import GqlWrapper
from tests.test_common_user import _SAMPLE_CONFIG

SAMPLE_RAW = 'loki'
SAMPLE_INSIGHT = 'key_assets'
SAMPLE_INSIGHT_URL = 'https://montecarlodata.com'
SAMPLE_S3_DESTINATION = 's3://bucket/prefix/object'
SAMPLE_FS_DESTINATION = 'file://folder1/folder2/object'


class MockRequest:
    raw = SAMPLE_RAW


class InsightServiceTest(TestCase):
    def setUp(self) -> None:
        self._request_wrapper_mock = Mock(autospec=GqlWrapper)
        self._service = InsightsService(
            _SAMPLE_CONFIG,
            request_wrapper=self._request_wrapper_mock
        )

    @patch('montecarlodata.insights.data_insights.click')
    def test_echo_insights(self, click_mock):
        self._request_wrapper_mock.make_request_v2.return_value = MonolithResponse(
            data=BoxList([{'description': 'description', 'title': 'Key Assets', 'available': True}]),
            errors=None
        )

        self._service.echo_insights(table_format='plain')
        self._request_wrapper_mock.make_request_v2.assert_called_once_with(query=GET_INSIGHTS, operation='getInsights')
        click_mock.echo.assert_called_once_with('Insight     Description    Available\nKey Assets  description.   True')

    def test_get_insight_with_bad_scheme(self):
        with self.assertRaises(click.exceptions.Abort):
            self._service.get_insight(insight=SAMPLE_INSIGHT, destination='foo')

        with self.assertRaises(click.exceptions.Abort):
            self._service.get_insight(insight=SAMPLE_INSIGHT, destination='http://foo')

    @patch.object(InsightsService, '_save_insight_to_disk')
    @patch.object(InsightsService, '_save_insight_to_s3')
    def test_get_insight_routing_s3(self, save_to_s3_mock, save_to_disk_mock):
        self._test_get_insight_routing(destination=SAMPLE_S3_DESTINATION)

        save_to_disk_mock.assert_not_called()
        save_to_s3_mock.assert_called_once_with(
            insight_url=SAMPLE_INSIGHT_URL,
            destination='bucket/prefix/object',
            aws_profile=None
        )

    @patch.object(InsightsService, '_save_insight_to_disk')
    @patch.object(InsightsService, '_save_insight_to_s3')
    def test_get_insight_routing_fs(self, save_to_s3_mock, save_to_disk_mock):
        self._test_get_insight_routing(destination=SAMPLE_FS_DESTINATION)

        save_to_disk_mock.assert_called_once_with(
            insight_url=SAMPLE_INSIGHT_URL,
            destination='folder1/folder2/object',
            aws_profile=None
        )
        save_to_s3_mock.assert_not_called()

    @patch('montecarlodata.insights.data_insights.click')
    @patch.object(InsightsService, '_get_insight_url')
    @patch.object(InsightsService, '_save_insight_to_disk')
    @patch.object(InsightsService, '_save_insight_to_s3')
    def test_get_insight_dry(self, save_to_s3_mock, save_to_disk_mock, get_mock, mock_click):
        get_mock.return_value = SAMPLE_INSIGHT_URL

        service = InsightsService(_SAMPLE_CONFIG, request_wrapper=self._request_wrapper_mock)
        service.get_insight(insight=SAMPLE_INSIGHT, destination=SAMPLE_FS_DESTINATION, dry=True)
        get_mock.assert_called_once_with(insight=SAMPLE_INSIGHT)
        mock_click.echo.assert_called_once_with(SAMPLE_INSIGHT_URL)

        save_to_disk_mock.assert_not_called()
        save_to_s3_mock.assert_not_called()

    @patch('montecarlodata.insights.data_insights.click')
    @patch.object(InsightsService, '_get_insight_url')
    def _test_get_insight_routing(self, get_mock, click_mock, destination: str):
        get_mock.return_value = SAMPLE_INSIGHT_URL

        service = InsightsService(_SAMPLE_CONFIG, request_wrapper=self._request_wrapper_mock)
        service.get_insight(insight=SAMPLE_INSIGHT, destination=destination)
        get_mock.assert_called_once_with(insight=SAMPLE_INSIGHT)
        click_mock.echo.assert_has_calls(
            [
                call(f"Saving insight to '{destination}'."),
                call('Complete. Have a nice day!')
            ]
        )
        self.assertEqual(click_mock.echo.call_count, 2)

    def test_get_insights_url(self):
        self._request_wrapper_mock.make_request_v2.return_value = MonolithResponse(data=Box({'url': SAMPLE_INSIGHT_URL}))
        self.assertEqual(self._service._get_insight_url(insight=SAMPLE_INSIGHT), SAMPLE_INSIGHT_URL)

        self._request_wrapper_mock.make_request_v2.assert_called_once_with(
            query=GET_INSIGHT_REPORT,
            operation='getReportUrl',
            variables=dict(insight_name=SAMPLE_INSIGHT, report_name=f'{SAMPLE_INSIGHT}.csv')
        )

    def test_get_insights_url_not_available(self):
        self._request_wrapper_mock.make_request_v2.return_value = MonolithResponse(data=Box({'url': None}))

        with self.assertRaises(click.exceptions.Abort):
            self._service._get_insight_url(insight=SAMPLE_INSIGHT)

        self._request_wrapper_mock.make_request_v2.assert_called_once_with(
            query=GET_INSIGHT_REPORT,
            operation='getReportUrl',
            variables=dict(insight_name=SAMPLE_INSIGHT, report_name=f'{SAMPLE_INSIGHT}.csv')
        )

    @patch('montecarlodata.insights.data_insights.urllib')
    @patch('montecarlodata.insights.data_insights.mkdirs')
    def test_save_insight_to_disk(self, mkdir_mock, urllib_mock):
        destination = 'folder1/folder2/object'
        self._service._save_insight_to_disk(insight_url=SAMPLE_INSIGHT_URL, destination=destination)
        mkdir_mock.assert_called_once_with('folder1/folder2')
        urllib_mock.request.urlretrieve.assert_called_once_with(SAMPLE_INSIGHT_URL, destination)

    @patch('montecarlodata.insights.data_insights.urllib')
    @patch('montecarlodata.insights.data_insights.mkdirs')
    def test_save_insight_to_disk_with_no_destination(self, mkdir_mock, urllib_mock):
        with self.assertRaises(click.exceptions.Abort):
            self._service._save_insight_to_disk(insight_url=SAMPLE_INSIGHT_URL, destination=None)
        mkdir_mock.assert_not_called()
        urllib_mock.request.urlretrieve.assert_not_called()

    @patch('montecarlodata.insights.data_insights.AwsClientWrapper')
    @patch('montecarlodata.insights.data_insights.requests')
    def test_save_insight_to_s3(self, request_mock, utils_mock):
        destination = 'bucket/prefix/object'
        request_mock.get.return_value = MockRequest

        self._service._save_insight_to_s3(insight_url=SAMPLE_INSIGHT_URL, destination=destination)
        request_mock.get.assert_called_once_with(SAMPLE_INSIGHT_URL, stream=True)
        utils_mock().upload_stream_to_s3.assert_called_once_with(
            data=SAMPLE_RAW,
            bucket='bucket',
            key='prefix/object'
        )

    @patch('montecarlodata.insights.data_insights.AwsClientWrapper')
    @patch('montecarlodata.insights.data_insights.requests')
    def test_save_insight_to_s3_with_bad_destination(self, request_mock, utils_mock):
        with self.assertRaises(click.exceptions.Abort):
            self._service._save_insight_to_s3(insight_url=SAMPLE_INSIGHT_URL, destination='bucket')
        request_mock.assert_not_called()
        utils_mock.assert_not_called()

        request_mock.reset_mock()
        utils_mock.reset_mock()

        with self.assertRaises(click.exceptions.Abort):
            self._service._save_insight_to_s3(insight_url=SAMPLE_INSIGHT_URL, destination='bucket/')
        request_mock.assert_not_called()
        utils_mock.assert_not_called()
