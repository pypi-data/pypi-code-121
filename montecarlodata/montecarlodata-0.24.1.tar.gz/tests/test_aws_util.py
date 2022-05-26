from typing import Any, List, Dict
from unittest import TestCase
from unittest.mock import Mock, patch, call

import click

from montecarlodata.utils import AwsClientWrapper

_SAMPLE_FILE_PATH = 'file'
_SAMPLE_BUCKET_NAME = 'bucket'
_SAMPLE_OBJECT_NAME = 'obj'
_SAMPLE_REGION = 'bar'
_SAMPLE_PROFILE_NAME = 'foo'
_SAMPLE_STACK_ID = 'arn:aws:stack'
_SAMPLE_STACK_LINK = 'link'
_SAMPLE_STACK_PARAMS = [{'foo': 'bar'}]
_SAMPLE_STACK_CAPABILITIES = 'CAPABILITY_IAM'
_SAMPLE_STACK_WAIT_CONFIG = {'Delay': 5, 'MaxAttempts': 720}
_SAMPLE_GATEWAY_ID = 'id'
_SAMPLE_GATEWAY_STAGE = 'stage'
_SAMPLE_STACK = {'Stacks': [{'Outputs': [0, 1, 2]}]}
_SAMPLE_TERM_PROTECT = False


class MockClient:
    # Arguments, classes and functions use AWS casing...

    @staticmethod
    def describe_stacks(StackName: str) -> Any:
        assert StackName == _SAMPLE_STACK_ID
        return _SAMPLE_STACK

    @staticmethod
    def upload_file(file_path: str, bucket_name: str, object_name: str):
        assert _SAMPLE_FILE_PATH == file_path
        assert _SAMPLE_BUCKET_NAME == bucket_name
        assert _SAMPLE_OBJECT_NAME == object_name

    @staticmethod
    def update_stack(StackName: str, TemplateURL: str, Parameters: List[Dict], Capabilities: List[str]):
        assert StackName == _SAMPLE_STACK_ID
        assert TemplateURL == _SAMPLE_STACK_LINK
        assert Parameters == _SAMPLE_STACK_PARAMS
        assert Capabilities == [_SAMPLE_STACK_CAPABILITIES]

    @staticmethod
    def create_stack(StackName: str, TemplateURL: str, Parameters: List[Dict], Capabilities: List[str], **kwargs):
        assert StackName == _SAMPLE_STACK_ID
        assert TemplateURL == _SAMPLE_STACK_LINK
        assert Parameters == _SAMPLE_STACK_PARAMS[0]
        assert Capabilities == [_SAMPLE_STACK_CAPABILITIES]
        return {'StackId': StackName}

    @staticmethod
    def create_deployment(restApiId: str, stageName: str):
        assert restApiId == _SAMPLE_GATEWAY_ID
        assert stageName == _SAMPLE_GATEWAY_STAGE

    class get_waiter:
        def __init__(self, waiter):
            self.wait = self._wait

        def _wait(self, StackName, WaiterConfig):
            assert StackName == _SAMPLE_STACK_ID
            assert WaiterConfig == _SAMPLE_STACK_WAIT_CONFIG


class AwsUtilTest(TestCase):
    def setUp(self) -> None:
        self._session_mock = Mock()

        self._service = self._setup()
        self._session_mock.reset_mock()

        self._session_mock.client.return_value = MockClient

    def test_setup(self):
        self._setup()

    def test_get_stack_outputs(self):
        self._service.get_stack_outputs(_SAMPLE_STACK_ID)
        self._session_mock.client.assert_called_once_with('cloudformation')

    def test_get_stack_parameters(self):
        self._service.get_stack_parameters(_SAMPLE_STACK_ID)
        self._session_mock.client.assert_called_once_with('cloudformation')

    @patch.object(AwsClientWrapper, 'get_stack_details')
    def test_upgrade_stack(self, mock_get_stack_details):
        mock_get_stack_details.return_value = {'Stacks': [{'StackStatus': 'UPDATE_COMPLETE'}]}
        self.assertTrue(self._service.upgrade_stack(_SAMPLE_STACK_ID, _SAMPLE_STACK_LINK, _SAMPLE_STACK_PARAMS))
        self._session_mock.client.assert_has_calls = [call('cloudformation') * 2]

    @patch.object(AwsClientWrapper, 'get_stack_details')
    def test_upgrade_stack_failed(self, mock_get_stack_details):
        mock_get_stack_details.return_value = {'Stacks': [{'StackStatus': 'UPDATE_FAILED'}]}
        self.assertFalse(self._service.upgrade_stack(_SAMPLE_STACK_ID, _SAMPLE_STACK_LINK, _SAMPLE_STACK_PARAMS))
        self._session_mock.client.assert_has_calls = [call('cloudformation') * 2]

    @patch.object(AwsClientWrapper, 'get_stack_details')
    def test_create_stack(self, mock_get_stack_details):
        mock_get_stack_details.return_value = {'Stacks': [{'StackStatus': 'CREATE_COMPLETE'}]}
        self.assertTrue(self._service.create_stack(_SAMPLE_STACK_ID, _SAMPLE_STACK_LINK, False, _SAMPLE_STACK_PARAMS[0]))
        self._session_mock.client.assert_has_calls = [call('cloudformation') * 2]

    @patch.object(AwsClientWrapper, 'get_stack_details')
    def test_create_stack_failed(self, mock_get_stack_details):
        mock_get_stack_details.return_value = {'Stacks': [{'StackStatus': 'CREATE_FAILED'}]}
        self.assertFalse(self._service.create_stack(_SAMPLE_STACK_ID, _SAMPLE_STACK_LINK, False, _SAMPLE_STACK_PARAMS[0]))
        self._session_mock.client.assert_has_calls = [call('cloudformation') * 2]

    def test_deploy_gateway(self):
        self._service.deploy_gateway(_SAMPLE_GATEWAY_ID, _SAMPLE_GATEWAY_STAGE)
        self._session_mock.client.assert_called_once_with('apigateway')

    def test_upload_file(self):
        self._service.upload_file(file_path=_SAMPLE_FILE_PATH,
                                  bucket_name=_SAMPLE_BUCKET_NAME,
                                  object_name=_SAMPLE_OBJECT_NAME)
        self._session_mock.client.assert_called_once_with('s3')

    def test_region_error(self):
        self._session_mock.client.side_effect = ValueError()
        with self.assertRaises(click.exceptions.Abort):
            self._setup()

    def _setup(self) -> AwsClientWrapper:
        client = AwsClientWrapper(_SAMPLE_PROFILE_NAME, _SAMPLE_REGION, session=self._session_mock)

        self._session_mock.client.assert_called_once_with('cloudformation')
        return client
