from unittest import TestCase
from unittest.mock import Mock, patch

from box import Box

from montecarlodata.collector.network_tests import CollectorNetworkTestService
from montecarlodata.common.data import MonolithResponse
from montecarlodata.queries.collector import TEST_TELNET_CONNECTION, TEST_TCP_OPEN_CONNECTION
from montecarlodata.utils import GqlWrapper
from tests.test_common_user import _SAMPLE_CONFIG

SAMPLE_OPTIONS = {'loki': 'thor'}
SAMPLE_MESSAGE = 'Telnet connection for getmontecarlo.com:443 is usable.'
SAMPLE_RESPONSE = MonolithResponse(
    data=Box(
        {
            'success': True,
            'validations': [{'type': 'network', 'message': SAMPLE_MESSAGE}]}
    ),
    errors=None
)


class CollectorNetworkTest(TestCase):
    def setUp(self) -> None:
        self._request_wrapper_mock = Mock(autospec=GqlWrapper)

        self._service = CollectorNetworkTestService(_SAMPLE_CONFIG, request_wrapper=self._request_wrapper_mock)

    @patch('montecarlodata.collector.network_tests.click')
    def test_echo_telnet(self, click_mock):
        self._request_wrapper_mock.make_request_v2.return_value = SAMPLE_RESPONSE
        self._service.echo_telnet_test(**SAMPLE_OPTIONS)
        self._request_wrapper_mock.make_request_v2.assert_called_once_with(
            query=TEST_TELNET_CONNECTION,
            operation='testTelnetConnection',
            variables=SAMPLE_OPTIONS
        )
        click_mock.echo.assert_called_once_with(SAMPLE_MESSAGE)

    @patch('montecarlodata.collector.network_tests.click')
    def test_echo_tcp_open(self, click_mock):
        self._request_wrapper_mock.make_request_v2.return_value = SAMPLE_RESPONSE
        self._service.echo_tcp_open_test()
        self._request_wrapper_mock.make_request_v2.assert_called_once_with(
            query=TEST_TCP_OPEN_CONNECTION,
            operation='testTcpOpenConnection',
            variables={}
        )
        click_mock.echo.assert_called_once_with(SAMPLE_MESSAGE)
