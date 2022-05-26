import json
import uuid
from typing import Dict
from unittest import TestCase
from unittest.mock import Mock, patch

from montecarlodata.common.data import MonolithResponse
from montecarlodata.common.user import UserService
from montecarlodata.integrations.onboarding.fields import EXPECTED_UPDATE_CREDENTIALS_RESPONSE_FIELD, \
    EXPECTED_REMOVE_CONNECTION_RESPONSE_FIELD, OPERATION_ERROR_VERBIAGE
from montecarlodata.integrations.onboarding.operations.connection_ops import ConnectionOperationsService
from montecarlodata.queries.onboarding import UPDATE_CREDENTIALS_MUTATION, REMOVE_CONNECTION_MUTATION, \
    TEST_EXISTING_CONNECTION_QUERY
from montecarlodata.utils import GqlWrapper, AwsClientWrapper
from tests.helpers import capture_function
from tests.test_common_user import _SAMPLE_CONFIG

_SAMPLE_UUID = uuid.uuid4()


class ConnectionOperationsTest(TestCase):
    def setUp(self) -> None:
        self._user_service_mock = Mock(autospec=UserService)
        self._request_wrapper_mock = Mock(autospec=GqlWrapper)
        self._aws_wrapper_mock = Mock(autospec=AwsClientWrapper)

        self._service = ConnectionOperationsService(
            _SAMPLE_CONFIG,
            request_wrapper=self._request_wrapper_mock,
            aws_wrapper=self._aws_wrapper_mock,
            user_service=self._user_service_mock
        )

    def test_update_credentials(self):
        changes = {'host': 'foo'}
        self._request_wrapper_mock.make_request_v2.return_value = MonolithResponse(data={'success': True})
        func = capture_function(self._service.update_credentials, dict(connection_id=_SAMPLE_UUID, changes=changes))

        self._request_wrapper_mock.make_request_v2.assert_called_once_with(
            query=UPDATE_CREDENTIALS_MUTATION,
            operation=EXPECTED_UPDATE_CREDENTIALS_RESPONSE_FIELD,
            variables=dict(connection_id=str(_SAMPLE_UUID), changes=json.dumps(changes), should_validate=True, should_replace=False)
        )
        self.assertEqual(func.std_out.getvalue().strip(), f"Success! Updated '{_SAMPLE_UUID}'.")

    def test_remove_connection(self):
        self._test_remove_connection(params=dict(connection_id=_SAMPLE_UUID, no_prompt=True))

    @patch('montecarlodata.integrations.onboarding.operations.connection_ops.click.confirm')
    def test_remove_connection_with_prompt(self, confirm):
        confirm.return_value = True
        self._test_remove_connection(params=dict(connection_id=_SAMPLE_UUID, no_prompt=False))

    def _test_remove_connection(self, params: Dict):
        self._request_wrapper_mock.make_request_v2.return_value = MonolithResponse(data={'success': True})
        func = capture_function(self._service.remove_connection, params)

        self._request_wrapper_mock.make_request_v2.assert_called_once_with(
            query=REMOVE_CONNECTION_MUTATION,
            operation=EXPECTED_REMOVE_CONNECTION_RESPONSE_FIELD,
            variables=dict(connection_id=str(_SAMPLE_UUID))
        )
        self.assertEqual(func.std_out.getvalue().strip(), f"Success! Removed '{_SAMPLE_UUID}'.")

    def test_echo_operation_status_with_errors(self):
        func = capture_function(
            function=self._service.echo_operation_status,
            params=dict(response=MonolithResponse(data={'success': False}), operation='foo')
        )  # Note - other tests capture the success state

        self.assertEqual(func.std_out.getvalue().strip(), OPERATION_ERROR_VERBIAGE)

    @patch('montecarlodata.integrations.onboarding.operations.connection_ops.click')
    def test_echo_test_existing(self, click_mock):
        connection_id = uuid.uuid4()
        self._request_wrapper_mock.make_request_v2.return_value = MonolithResponse(data={'success': True})
        self._service.echo_test_existing(connection_id=connection_id)
        self._request_wrapper_mock.make_request_v2.assert_called_once_with(
            query=TEST_EXISTING_CONNECTION_QUERY,
            operation='testExistingConnection',
            variables={'connection_id': connection_id}
        )
        click_mock.echo.assert_called_once_with('{\n    "success": true\n}')
