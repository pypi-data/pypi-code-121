import base64
import copy
from unittest import TestCase
from unittest.mock import Mock, patch, call

import click
from box import Box

from montecarlodata.common.data import MonolithResponse
from montecarlodata.common.user import UserService
from montecarlodata.integrations.onboarding.bi.reports import ReportsOnboardingService
from montecarlodata.queries.onboarding import TEST_TABLEAU_CRED_MUTATION, ADD_TABLEAU_CONNECTION_MUTATION, \
    TEST_LOOKER_METADATA_CRED_MUTATION, ADD_BI_CONNECTION_MUTATION, TEST_LOOKER_GIT_CLONE_CRED_MUTATION
from montecarlodata.utils import GqlWrapper, AwsClientWrapper
from tests.test_base_onboarding import _SAMPLE_BASE_OPTIONS
from tests.test_common_user import _SAMPLE_CONFIG

_SAMPLE_OPTIONS = {'foo': 'bar'}


class ReportOnboardingTest(TestCase):
    def setUp(self) -> None:
        self._user_service_mock = Mock(autospec=UserService)
        self._request_wrapper_mock = Mock(autospec=GqlWrapper)
        self._aws_wrapper_mock = Mock(autospec=AwsClientWrapper)

        self._service = ReportsOnboardingService(
            _SAMPLE_CONFIG,
            request_wrapper=self._request_wrapper_mock,
            aws_wrapper=self._aws_wrapper_mock,
            user_service=self._user_service_mock,
        )

    @patch('montecarlodata.integrations.onboarding.bi.reports.click')
    @patch('montecarlodata.integrations.onboarding.bi.reports.prompt_connection')
    def test_add_tableau(self, prompt_connection_mock, click_mock):
        self._request_wrapper_mock.make_request_v2.side_effect = [
            MonolithResponse(data=Box({'success': True})),
            MonolithResponse(data=Box({'tableauAccount': {'uuid': True}}))
        ]

        self._service.onboard_tableau(**_SAMPLE_OPTIONS)
        self._request_wrapper_mock.assert_has_calls(
            [
                call.make_request_v2(
                    query=TEST_TABLEAU_CRED_MUTATION,
                    operation='testTableauCredentials',
                    variables=_SAMPLE_OPTIONS
                ),
                call.make_request_v2(
                    query=ADD_TABLEAU_CONNECTION_MUTATION,
                    operation='addTableauAccount',
                    variables=_SAMPLE_OPTIONS
                )
            ]
        )
        prompt_connection_mock.assert_called_once_with(
            message='Please confirm you want to add this connection',
            skip_prompt=False
        )
        click_mock.echo.assert_has_calls(
            [
                call('Connection test was successful!'),
                call('Success! Added connection for tableau.')
            ]
        )

    @patch('montecarlodata.integrations.onboarding.bi.reports.click')
    @patch('montecarlodata.integrations.onboarding.bi.reports.prompt_connection')
    def test_add_tableau_with_validation_failure(self, prompt_connection_mock, click_mock):
        self._request_wrapper_mock.make_request_v2.return_value = MonolithResponse(data=Box({'success': False}))

        with self.assertRaises(click.exceptions.Abort):
            self._service.onboard_tableau(**_SAMPLE_OPTIONS)
        self._request_wrapper_mock.make_request_v2.assert_called_once_with(
            query=TEST_TABLEAU_CRED_MUTATION,
            operation='testTableauCredentials',
            variables=_SAMPLE_OPTIONS
        )
        prompt_connection_mock.assert_not_called()
        click_mock.echo.assert_not_called()

    @patch('montecarlodata.integrations.onboarding.bi.reports.click')
    @patch('montecarlodata.integrations.onboarding.bi.reports.prompt_connection')
    def test_add_tableau_with_validate_only(self, prompt_connection_mock, click_mock):
        options = copy.deepcopy(_SAMPLE_OPTIONS)
        options['validate_only'] = True
        self._request_wrapper_mock.make_request_v2.return_value = MonolithResponse(data=Box({'success': True}))

        self._service.onboard_tableau(**options)
        self._request_wrapper_mock.make_request_v2.assert_called_once_with(
            query=TEST_TABLEAU_CRED_MUTATION,
            operation='testTableauCredentials',
            variables=_SAMPLE_OPTIONS
        )
        prompt_connection_mock.assert_not_called()
        click_mock.echo.assert_has_calls(
            [
                call('Connection test was successful!'),
                call('Skipping adding the connection.')
            ]
        )

    @patch.object(ReportsOnboardingService, 'onboard')
    def test_looker_metadata_flow(self, onboard_mock):
        self._service.onboard_looker_metadata(**_SAMPLE_BASE_OPTIONS)
        onboard_mock.assert_called_once_with(
            validation_query=TEST_LOOKER_METADATA_CRED_MUTATION,
            connection_query=ADD_BI_CONNECTION_MUTATION,
            validation_response='testLookerCredentials',
            connection_response='addBiConnection',
            connection_type='looker',
            **_SAMPLE_BASE_OPTIONS
        )

    @patch.object(ReportsOnboardingService, 'onboard')
    @patch('montecarlodata.integrations.onboarding.bi.reports.read_as_base64')
    def test_looker_git_flow(self, read_as_base64_mock, onboard_mock):
        file_path, service_json = 'foo', 'bar'
        base64_key = base64.b64encode(service_json.encode('utf-8'))

        input_options = {'ssh_key': file_path, **_SAMPLE_BASE_OPTIONS}
        expected_options = {**{'ssh_key': base64_key.decode()}, **_SAMPLE_BASE_OPTIONS}

        read_as_base64_mock.return_value = base64_key

        self._service.onboard_looker_git(**input_options)
        read_as_base64_mock.assert_called_once_with(file_path)
        onboard_mock.assert_called_once_with(
            validation_query=TEST_LOOKER_GIT_CLONE_CRED_MUTATION,
            connection_query=ADD_BI_CONNECTION_MUTATION,
            validation_response='testLookerGitCloneCredentials',
            connection_response='addBiConnection',
            connection_type='looker-git-clone',
            **expected_options
        )
