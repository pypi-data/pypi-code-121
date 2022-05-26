import copy
import json
from unittest import TestCase
from unittest.mock import Mock, patch

import click

from montecarlodata.common.data import MonolithResponse, OnboardingConfiguration, ConnectionOptions
from montecarlodata.common.user import UserService
from montecarlodata.integrations.onboarding.base import BaseOnboardingService
from montecarlodata.common.data import ValidationResult
from montecarlodata.integrations.onboarding.fields import DATA_LAKE_WAREHOUSE_TYPE
from montecarlodata.queries.onboarding import ADD_CONNECTION_MUTATION
from montecarlodata.utils import GqlWrapper, AwsClientWrapper
from tests.test_common_user import _SAMPLE_USER_RESPONSE, _SAMPLE_CONFIG, _SAMPLE_DW_ID

_SAMPLE_BUCKET_NAME = 'bucket'
_SAMPLE_BASE_OPTIONS = {'foo': 'bar'}
_SAMPLE_DC_OUTPUT = [{'OutputKey': 'PrivateS3BucketArn', 'OutputValue': f'arn:aws:s3:::{_SAMPLE_BUCKET_NAME}'}]
_SAMPLE_CONNECTION_PATH = 'test'


class BaseOnboardingTest(TestCase):
    def setUp(self) -> None:
        self._user_service_mock = Mock(autospec=UserService)
        self._request_wrapper_mock = Mock(autospec=GqlWrapper)
        self._aws_wrapper_mock = Mock(autospec=AwsClientWrapper)

        self._user_service_mock.collectors = _SAMPLE_USER_RESPONSE['getUser']['account']['dataCollectors']
        self._user_service_mock.active_collector = self._user_service_mock.collectors[0]
        self._user_service_mock.warehouses = [{'uuid': _SAMPLE_DW_ID, 'connectionType': 'data-lake'}]

        self._service = BaseOnboardingService(
            _SAMPLE_CONFIG,
            request_wrapper=self._request_wrapper_mock,
            aws_wrapper=self._aws_wrapper_mock,
            user_service=self._user_service_mock
        )

    @patch.object(BaseOnboardingService, '_validate_connection')
    @patch.object(BaseOnboardingService, '_add_connection')
    @patch('montecarlodata.integrations.onboarding.base.prompt_connection')
    def test_onboard_wrapper(self, prompt_mock, connection_mock, validation_mock):
        # Test the convenience wrapper makes the expected validation and connection calls
        validation_query, validation_response, connection_type, job_types = 'foo', 'bar', 'qux', ['test']
        options, v_return = {'hello': 'world'}, ValidationResult(has_warnings=False, credentials_key='path')
        job_limits = {'tables_batch_size': 10}

        validation_mock.return_value = v_return

        self._service.onboard(
            validation_query=validation_query,
            validation_response=validation_response,
            connection_type=connection_type,
            job_types=job_types,
            job_limits=job_limits,
            **options
        )

        validation_mock.assert_called_once_with(
            query=validation_query,
            response_field=validation_response,
            **options
        )

        expected_onboarding_config = OnboardingConfiguration(
            connection_type=connection_type,
            job_types=job_types,
            job_limits=job_limits,
            warehouse_type=DATA_LAKE_WAREHOUSE_TYPE,
            warehouse_name=None,
            validation_query=validation_query,
            validation_response=validation_response,
            **{}
        )
        expected_onboarding_config.connection_options = ConnectionOptions(
            monolith_base_payload=options,
            dc_id=None,
            validate_only=False,
            skip_validation=False,
            skip_permission_tests=False,
            auto_yes=False
        )

        connection_mock.assert_called_once_with(
            temp_path=v_return.credentials_key,
            onboarding_config=expected_onboarding_config
        )
        prompt_mock.assert_called_once_with(message='Please confirm you want to add this connection', skip_prompt=False)

    @patch.object(BaseOnboardingService, '_validate_connection')
    @patch.object(BaseOnboardingService, '_add_connection')
    @patch('montecarlodata.integrations.onboarding.base.prompt_connection')
    def test_onboard_wrapper_with_options(self, prompt_mock, connection_mock, validation_mock):
        validation_query, validation_response, connection_type, job_types, dc_id = 'foo', 'bar', 'qux', ['test'], '123'
        input_options = {'hello': 'world', 'dc_id': dc_id, 'auto_yes': True, 'skip_validation': True}
        v_return = ValidationResult(has_warnings=False, credentials_key='path')

        monolith_connection_payload = {'dcId': '123', 'skipValidation': True}

        validator_options = copy.deepcopy(input_options)
        validator_options['connectionOptions'] = {'dcId': dc_id, 'skipValidation': True}
        [validator_options.pop(i) for i in ['dc_id', 'auto_yes', 'skip_validation']]

        validation_mock.return_value = v_return

        self._service.onboard(
            validation_query=validation_query,
            validation_response=validation_response,
            connection_type=connection_type,
            job_types=job_types,
            **input_options
        )

        validation_mock.assert_called_once_with(
            query=validation_query,
            response_field=validation_response,
            **validator_options
        )

        expected_onboarding_config = OnboardingConfiguration(
            connection_type=connection_type,
            job_types=job_types,
            warehouse_type=DATA_LAKE_WAREHOUSE_TYPE,
            warehouse_name=None,
            validation_query=validation_query,
            validation_response=validation_response,
            **{}
        )
        expected_onboarding_config.connection_options = ConnectionOptions(
            monolith_base_payload={'hello': 'world', 'connectionOptions': monolith_connection_payload},
            dc_id=dc_id,
            validate_only=False,
            skip_validation=True,
            skip_permission_tests=False,
            auto_yes=True
        )
        expected_onboarding_config.connection_options.monolith_connection_payload = monolith_connection_payload

        connection_mock.assert_called_once_with(
            temp_path=v_return.credentials_key,
            onboarding_config=expected_onboarding_config
        )
        prompt_mock.assert_called_once_with(message='Please confirm you want to add this connection', skip_prompt=True)

    def test_handle_no_cert(self):
        original_options = copy.deepcopy(_SAMPLE_BASE_OPTIONS)
        self._service.handle_cert('test', _SAMPLE_BASE_OPTIONS)

        self.assertDictEqual(original_options, _SAMPLE_BASE_OPTIONS)
        self._aws_wrapper_mock.upload_file.assert_not_called()

    def test_handle_cert_in_s3(self):
        s3_key = 'testing/test'
        options = {'cert_s3': s3_key, **_SAMPLE_BASE_OPTIONS}
        self._service.handle_cert('test', options)

        self.assertDictEqual(options, {'ssl_options': {'cert': s3_key, 'mechanism': 'dc-s3'}, **_SAMPLE_BASE_OPTIONS})
        self._aws_wrapper_mock.upload_file.assert_not_called()

    def test_handle_cert_from_file(self):
        file_path = './test/test.txt'
        s3_key = 'test/test.txt'
        options = {'cert_file': file_path, **_SAMPLE_BASE_OPTIONS}

        self._aws_wrapper_mock.get_stack_outputs.return_value = _SAMPLE_DC_OUTPUT
        self._service.handle_cert('test', options)

        self._aws_wrapper_mock.upload_file.assert_called_once_with(
            bucket_name=_SAMPLE_BUCKET_NAME,
            object_name=s3_key,
            file_path=file_path
        )
        self.assertDictEqual(options, {'ssl_options': {'cert': s3_key, 'mechanism': 'dc-s3'}, **_SAMPLE_BASE_OPTIONS})

    @patch('montecarlodata.errors.click')
    def test_failed_validation(self, click_mock):
        click_mock.Abort.return_value = click.exceptions.Abort()
        expected_echo = 'Error - Connection test failed!'

        query, response_field = 'foo', 'bar'
        self._request_wrapper_mock.make_request_v2.return_value = MonolithResponse(data={response_field: {}})
        with self.assertRaises(click.exceptions.Abort):
            self._service._validate_connection(query, response_field, **_SAMPLE_BASE_OPTIONS)
        self._request_wrapper_mock.make_request_v2.assert_called_once_with(
            query=query,
            operation=response_field,
            variables=_SAMPLE_BASE_OPTIONS)

        click_mock.echo.assert_called_with(expected_echo, err=True)

    @patch('montecarlodata.errors.click')
    def test_failed_validation_with_details(self, click_mock):
        click_mock.Abort.return_value = click.exceptions.Abort()
        expected_echo = 'Error - Connection test failed!\n' \
                        '╒═══════════════╤══════════╤═════════════════════════════════════════════╕\n' \
                        '│ Validation    │ Result   │ Details                                     │\n' \
                        '╞═══════════════╪══════════╪═════════════════════════════════════════════╡\n' \
                        '│ Able to dance │ Passed   │                                             │\n' \
                        '├───────────────┼──────────┼─────────────────────────────────────────────┤\n' \
                        '│ Able to sing  │ Failed   │ Turns out I cannot carry a tune in a bucket │\n' \
                        '╘═══════════════╧══════════╧═════════════════════════════════════════════╛'

        query, response_field = 'foo', 'bar'
        self._request_wrapper_mock.make_request_v2.return_value = MonolithResponse(data={
            'success': False,
            'validations': [{
                'type': 'skills',
                'message': 'Able to dance'
            }],
            'warnings': [{
                'type': 'metadata',
                'message': 'Able to sing',
                'data': {
                    'error': 'Turns out I cannot carry a tune in a bucket'
                }
            }]
        })
        with self.assertRaises(click.exceptions.Abort):
            self._service._validate_connection(query, response_field, **_SAMPLE_BASE_OPTIONS)
        self._request_wrapper_mock.make_request_v2.assert_called_once_with(
            query=query,
            operation=response_field,
            variables=_SAMPLE_BASE_OPTIONS)

        click_mock.echo.assert_called_with(expected_echo, err=True)

    @patch('montecarlodata.integrations.onboarding.base.click')
    def test_successful_validation(self, click_mock):
        expected_echo = 'Connection test was successful!'

        query, response_field, temp_path = 'foo', 'bar', 'qux'
        self._request_wrapper_mock.make_request_v2.return_value = MonolithResponse(data={'key': temp_path})

        result = self._service._validate_connection(query, response_field, **_SAMPLE_BASE_OPTIONS)
        self.assertFalse(result.has_warnings)
        self.assertEqual(temp_path, result.credentials_key)

        self._request_wrapper_mock.make_request_v2.assert_called_once_with(
            query=query,
            operation=response_field,
            variables=_SAMPLE_BASE_OPTIONS)

        click_mock.echo.assert_called_with(expected_echo)

    @patch('montecarlodata.integrations.onboarding.base.click')
    def test_successful_validation_with_warnings(self, click_mock):
        expected_echo = 'Connection test was successful!\n' \
                        '╒═══════════════╤══════════╤═════════════════════════════════════════════╕\n' \
                        '│ Validation    │ Result   │ Details                                     │\n' \
                        '╞═══════════════╪══════════╪═════════════════════════════════════════════╡\n' \
                        '│ Able to dance │ Passed   │                                             │\n' \
                        '├───────────────┼──────────┼─────────────────────────────────────────────┤\n' \
                        '│ Able to sing  │ Failed   │ Turns out I cannot carry a tune in a bucket │\n' \
                        '╘═══════════════╧══════════╧═════════════════════════════════════════════╛'

        query, response_field, temp_path = 'foo', 'bar', 'qux'
        self._request_wrapper_mock.make_request_v2.return_value = MonolithResponse(data={
            'success': True,
            'key': temp_path,
            'validations': [{
                'type': 'skills',
                'message': 'Able to dance'
            }],
            'warnings': [{
                'type': 'metadata',
                'message': 'Able to sing',
                'data': {
                    'error': 'Turns out I cannot carry a tune in a bucket'
                }
            }]
        })

        result = self._service._validate_connection(query, response_field, **_SAMPLE_BASE_OPTIONS)
        self.assertTrue(result.has_warnings)
        self.assertEqual(temp_path, result.credentials_key)

        self._request_wrapper_mock.make_request_v2.assert_called_once_with(
            query=query,
            operation=response_field,
            variables=_SAMPLE_BASE_OPTIONS)

        click_mock.echo.assert_called_with(expected_echo)

    def test_connection_with_one_warehouse(self):
        key, conn_id = 'foo', 'bar'
        self._user_service_mock.warehouses = [{'uuid': _SAMPLE_DW_ID, 'connectionType': 'DATA_LAKE'}]
        self._request_wrapper_mock.make_request_v2.return_value = MonolithResponse(data={'connection': {'uuid': conn_id}})
        self.assertTrue(self._service._add_connection(key, OnboardingConfiguration(connection_type=_SAMPLE_CONNECTION_PATH, **{})))

        self._request_wrapper_mock.make_request_v2.assert_called_once_with(
            query=ADD_CONNECTION_MUTATION,
            operation='addConnection',
            variables={'key': key, 'connectionType': _SAMPLE_CONNECTION_PATH, 'dwId': _SAMPLE_DW_ID}
        )

    def test_connection_with_no_warehouses(self):
        key, conn_id = 'foo', 'bar'
        self._user_service_mock.warehouses = []
        service = BaseOnboardingService(
            _SAMPLE_CONFIG,
            request_wrapper=self._request_wrapper_mock,
            aws_wrapper=self._aws_wrapper_mock,
            user_service=self._user_service_mock
        )
        self._request_wrapper_mock.make_request_v2.return_value = MonolithResponse(data={'connection': {'uuid': conn_id}})
        self.assertTrue(service._add_connection(key, OnboardingConfiguration(connection_type=_SAMPLE_CONNECTION_PATH, **{})))

        self._request_wrapper_mock.make_request_v2.assert_called_once_with(
            query=ADD_CONNECTION_MUTATION,
            operation='addConnection',
            variables={'key': key, 'connectionType': _SAMPLE_CONNECTION_PATH, 'createWarehouseType': 'data-lake'}
        )

    def test_connection_with_multiple_warehouses(self):
        key, conn_id, name, dw_type = 'foo', 'bar', 'test', 'redshift'
        self._user_service_mock.warehouses = [
            {'uuid': '123', 'connectionType': 'redshift'},
            {'uuid': '456', 'connectionType': 'snowflake'}
        ]
        config = OnboardingConfiguration(connection_type=_SAMPLE_CONNECTION_PATH, **{})
        config.warehouse_type = dw_type
        config.warehouse_name = name

        self._request_wrapper_mock.make_request_v2.return_value = MonolithResponse(data={'connection': {'uuid': conn_id}})
        self.assertTrue(
            self._service._add_connection(key, config))

        self._request_wrapper_mock.make_request_v2.assert_called_once_with(
            query=ADD_CONNECTION_MUTATION,
            operation='addConnection',
            variables={
                'key': key,
                'connectionType': _SAMPLE_CONNECTION_PATH,
                'createWarehouseType': dw_type,
                'name': name
            }
        )

    def test_connection_with_multiple_warehouses_and_a_lake(self):
        key, conn_id, dw_id = 'foo', 'bar', '456'
        self._user_service_mock.warehouses = [
            {'uuid': '123', 'connectionType': 'redshift'},
            {'uuid': dw_id, 'connectionType': 'data-lake'}
        ]

        self._request_wrapper_mock.make_request_v2.return_value = MonolithResponse(data={'connection': {'uuid': conn_id}})
        self.assertTrue(self._service._add_connection(key, OnboardingConfiguration(connection_type=_SAMPLE_CONNECTION_PATH, **{})))

        self._request_wrapper_mock.make_request_v2.assert_called_once_with(
            query=ADD_CONNECTION_MUTATION,
            operation='addConnection',
            variables={
                'key': key,
                'connectionType': _SAMPLE_CONNECTION_PATH,
                'dwId': dw_id
            }
        )

    def test_connection_with_job_types(self):
        key, conn_id, jobs = 'foo', 'bar', ['qux']
        config = OnboardingConfiguration(connection_type=_SAMPLE_CONNECTION_PATH, **{})
        config.job_types = jobs

        self._request_wrapper_mock.make_request_v2.return_value = MonolithResponse(data={'connection': {'uuid': conn_id}})
        self.assertTrue(self._service._add_connection(key, config))

        self._request_wrapper_mock.make_request_v2.assert_called_once_with(
            query=ADD_CONNECTION_MUTATION,
            operation='addConnection',
            variables={'key': key, 'connectionType': _SAMPLE_CONNECTION_PATH, 'dwId': _SAMPLE_DW_ID, 'jobTypes': jobs}
        )

    def test_connection_with_job_limits(self):
        key, conn_id, job_limits = 'foo', 'bar', {'hello': 'world'}
        config = OnboardingConfiguration(connection_type=_SAMPLE_CONNECTION_PATH, **{})
        config.job_limits = job_limits

        self._request_wrapper_mock.make_request_v2.return_value = MonolithResponse(data={'connection': {'uuid': conn_id}})
        self.assertTrue(self._service._add_connection(key, config))

        self._request_wrapper_mock.make_request_v2.assert_called_once_with(
            query=ADD_CONNECTION_MUTATION,
            operation='addConnection',
            variables={
                'key': key,
                'connectionType': _SAMPLE_CONNECTION_PATH,
                'dwId': _SAMPLE_DW_ID,
                'jobLimits': json.dumps(job_limits)
            }
        )
