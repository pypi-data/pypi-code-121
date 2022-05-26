import copy
from unittest import TestCase
from unittest.mock import Mock

import click

from montecarlodata.common.user import UserService, User
from montecarlodata.config import Config
from montecarlodata.queries.user import GET_USER_QUERY
from montecarlodata.utils import GqlWrapper, AwsClientWrapper

_SAMPLE_CONFIG = Config(
    mcd_id='1234',
    mcd_token='5678',
    mcd_api_endpoint='https://api.getmontecarlo.com/graphql',
    aws_profile='testing',
    aws_region='us-east-1'
)

_SAMPLE_USER = User(
    first_name='foo',
    last_name='bar'
)

_SAMPLE_DW_ID = '42'
_SAMPLE_USER_RESPONSE = {'getUser': {'firstName': _SAMPLE_USER.first_name, 'lastName': _SAMPLE_USER.last_name,
                                     'account': {'uuid': '12345', 'warehouses': [{'uuid': _SAMPLE_DW_ID}],
                                                 'dataCollectors': [{'uuid': '5678', 'stackArn': 'arn', 'active': True}]}}}


class UserServiceTest(TestCase):
    def setUp(self) -> None:
        self._request_wrapper_mock = Mock(autospec=GqlWrapper)
        self._aws_wrapper_mock = Mock(autospec=AwsClientWrapper)

        self._request_wrapper_mock.make_request.return_value = _SAMPLE_USER_RESPONSE
        self._service = UserService(
            _SAMPLE_CONFIG,
            request_wrapper=self._request_wrapper_mock,
        )
        self._request_wrapper_mock.reset_mock()

    def test_user(self):
        self.assertEqual(self._service.user.first_name, _SAMPLE_USER.first_name)
        self.assertEqual(self._service.user.last_name, _SAMPLE_USER.last_name)

    def test_initialization(self):
        user = UserService(_SAMPLE_CONFIG, request_wrapper=self._request_wrapper_mock)
        self._request_wrapper_mock.make_request.assert_called_once_with(GET_USER_QUERY)

        self.assertEqual(user._user, _SAMPLE_USER_RESPONSE)
        self.assertEqual(user.warehouses[0]['uuid'], _SAMPLE_DW_ID)

    def test_no_active_collectors(self):
        no_dc_user = copy.deepcopy(_SAMPLE_USER_RESPONSE)
        no_dc_user['getUser']['account']['dataCollectors'] = []

        self._request_wrapper_mock.make_request.return_value = no_dc_user
        with self.assertRaises(click.exceptions.Abort):
            UserService(_SAMPLE_CONFIG, request_wrapper=self._request_wrapper_mock).active_collector

    def test_get_collector(self):
        self.assertEqual(
            self._service.get_collector(),
            {'uuid': '5678', 'stackArn': 'arn', 'active': True}
        )

    def test_get_collector_multi(self):
        multi_dc_user = copy.deepcopy(_SAMPLE_USER_RESPONSE)
        multi_dc_user['getUser']['account']['dataCollectors'] = [
            {'uuid': '1234', 'stackArn': 'arn', 'active': True},
            {'uuid': '5678', 'stackArn': 'arn', 'active': True}
        ]
        self._request_wrapper_mock.make_request.return_value = multi_dc_user

        with self.assertRaises(click.exceptions.Abort):
            UserService(_SAMPLE_CONFIG, request_wrapper=self._request_wrapper_mock).get_collector()

        self.assertEqual(
            UserService(_SAMPLE_CONFIG, request_wrapper=self._request_wrapper_mock).get_collector(dc_id='1234'),
            multi_dc_user['getUser']['account']['dataCollectors'][0]
        )

    def test_get_collector_with_no_collectors(self):
        no_dc_user = copy.deepcopy(_SAMPLE_USER_RESPONSE)
        no_dc_user['getUser']['account']['dataCollectors'] = []
        self._request_wrapper_mock.make_request.return_value = no_dc_user
        with self.assertRaises(click.exceptions.Abort):
            UserService(_SAMPLE_CONFIG, request_wrapper=self._request_wrapper_mock).get_collector()
