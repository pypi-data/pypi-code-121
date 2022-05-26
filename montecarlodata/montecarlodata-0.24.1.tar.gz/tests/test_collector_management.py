import copy
from unittest import TestCase
from unittest.mock import Mock, patch

import click
from box import Box

from montecarlodata.collector.fields import ADD_DC_PROMPT_VERBIAGE
from montecarlodata.collector.management import CollectorManagementService
from montecarlodata.common.data import MonolithResponse
from montecarlodata.common.user import UserService
from montecarlodata.queries.collector import ADD_COLLECTOR_RECORD
from montecarlodata.utils import GqlWrapper, AwsClientWrapper
from tests.helpers import capture_function
from tests.test_common_user import _SAMPLE_CONFIG

_SAMPLE_STACK_ARN = 'stack_arn'
_SAMPLE_GATEWAY_ID = 'gateway_id'
_SAMPLE_TEMPLATE_URI = 'https://s3.amazonaws.com/bucket/public/customer_templates/id.json'
_SAMPLE_INVALID_LAUNCH_URL = f'https://test.com/cf/home?region=us-east-1#/stacks/create/review?stackName=monte-carlo&malformed'
_SAMPLE_VALID_LAUNCH_URL = f'https://test.com/cf/home?region=us-east-1#/stacks/create/review?stackName=monte-carlo&templateURL={_SAMPLE_TEMPLATE_URI}'
_SAMPLE_COLLECTOR_RESPONSE = {
    'generateCollectorTemplate': {
        'dc': {
            'templateLaunchUrl': _SAMPLE_VALID_LAUNCH_URL,
            'stackArn': _SAMPLE_STACK_ARN,
            'active': True,
            'apiGatewayId': _SAMPLE_GATEWAY_ID
        }
    }
}
_SAMPLE_EXTRACTED_COLLECTOR_RESPONSE = _SAMPLE_COLLECTOR_RESPONSE['generateCollectorTemplate']
_SAMPLE_MONOLITH_RESPONSE = MonolithResponse(data=_SAMPLE_EXTRACTED_COLLECTOR_RESPONSE)
_SAMPLE_COLLECTORS_RESPONSE = [
    {
        'uuid': '1234',
        'stackArn': 'aws-loki',
        'active': True,
        'customerAwsAccountId': 'test',
        'templateProvider': 'cloudformation',
        'templateVariant': 'dionysus',
        'templateVersion': '42',
        'codeVersion': '2042',
        'lastUpdated': None
    },
    {
        'uuid': '5678',
        'stackArn': 'aws-thor',
        'active': True,
        'templateProvider': 'terraform',
        'templateVariant': 'foo',
        'templateVersion': '42',
        'codeVersion': '2042',
        'lastUpdated': None
    },
    {
        'uuid': '0912',
        'stackArn': 'aws-odin',
        'active': False,
        'templateProvider': None,
        'templateVariant': None,
        'templateVersion': '42',
        'codeVersion': '2042',
        'lastUpdated': None
    }
]


class CollectorManagementTest(TestCase):
    def setUp(self) -> None:
        self._request_wrapper_mock = Mock(autospec=GqlWrapper)
        self._aws_wrapper_mock = Mock(autospec=AwsClientWrapper)
        self._user_service_mock = Mock(autospec=UserService)

        self._service = CollectorManagementService(
            _SAMPLE_CONFIG,
            request_wrapper=self._request_wrapper_mock,
            aws_wrapper=self._aws_wrapper_mock,
            user_service=self._user_service_mock
        )

    def test_get_template_with_response(self):
        self._request_wrapper_mock.make_request_v2.return_value = None
        with self.assertRaises(click.exceptions.Abort):
            self._service.echo_template()

    def test_get_template_with_invalid_link(self):
        self._request_wrapper_mock.make_request_v2.return_value = MonolithResponse(
            data={'dc': {'templateLaunchUrl': _SAMPLE_INVALID_LAUNCH_URL}}
        )

        with self.assertRaises(click.exceptions.Abort):
            self._service.echo_template()

    def test_get_template_with_valid_link(self):
        self._request_wrapper_mock.make_request_v2.return_value = MonolithResponse(
            data={'dc': {'templateLaunchUrl': _SAMPLE_VALID_LAUNCH_URL}}
        )

        std_out = capture_function(function=self._service.echo_template).std_out
        self.assertEqual(std_out.getvalue().strip(), _SAMPLE_TEMPLATE_URI)

    def test_upgrade_with_inactive_collector(self):
        sample_collector_response = copy.deepcopy(_SAMPLE_COLLECTOR_RESPONSE)
        sample_collector_response['generateCollectorTemplate']['dc']['active'] = False

        self._request_wrapper_mock.make_request.return_value = sample_collector_response
        with self.assertRaises(click.exceptions.Abort):
            self._service.upgrade_template()

    def test_upgrade_with_missing_fields(self):
        self._request_wrapper_mock.make_request.return_value = {'generateCollectorTemplate': {'dc': {}}}
        with self.assertRaises(click.exceptions.Abort):
            self._service.upgrade_template()

    def test_upgrade(self):
        self._aws_wrapper_mock.get_stack_parameters.return_value = None
        self._aws_wrapper_mock.upgrade_stack.return_value = True

        self._request_wrapper_mock.make_request_v2.return_value = _SAMPLE_MONOLITH_RESPONSE
        self._service.upgrade_template()

        self._aws_wrapper_mock.get_stack_parameters.assert_called_once_with(stack_id=_SAMPLE_STACK_ARN)
        self._aws_wrapper_mock.upgrade_stack.assert_called_once_with(stack_id=_SAMPLE_STACK_ARN,
                                                                     template_link=_SAMPLE_TEMPLATE_URI,
                                                                     parameters=None)
        self._aws_wrapper_mock.deploy_gateway.assert_called_once_with(gateway_id=_SAMPLE_GATEWAY_ID)

    def test_failed_stack_upgrade(self):
        self._aws_wrapper_mock.get_stack_parameters.return_value = None
        self._aws_wrapper_mock.upgrade_stack.return_value = False

        self._request_wrapper_mock.make_request_v2.return_value = _SAMPLE_MONOLITH_RESPONSE
        with self.assertRaises(click.exceptions.Abort):
            self._service.upgrade_template()

        self._aws_wrapper_mock.get_stack_parameters.assert_called_once_with(stack_id=_SAMPLE_STACK_ARN)
        self._aws_wrapper_mock.upgrade_stack.assert_called_once_with(stack_id=_SAMPLE_STACK_ARN,
                                                                     template_link=_SAMPLE_TEMPLATE_URI,
                                                                     parameters=None)
        self._aws_wrapper_mock.deploy_gateway.assert_not_called()

    def test_deploy(self):
        stack_name, termination_protection = 'foo', False
        collector_response = copy.deepcopy(_SAMPLE_COLLECTOR_RESPONSE)
        collector_response['generateCollectorTemplate']['dc']['active'] = False
        monolith_response = MonolithResponse(data=collector_response['generateCollectorTemplate'])

        self._aws_wrapper_mock.create_stack.return_value = True

        self._request_wrapper_mock.make_request_v2.return_value = monolith_response
        self._service.deploy_template(stack_name=stack_name, termination_protection=termination_protection)

        self._aws_wrapper_mock.create_stack.assert_called_once_with(stack_name=stack_name,
                                                                    template_link=_SAMPLE_TEMPLATE_URI,
                                                                    termination_protection=termination_protection,
                                                                    parameters=[])

    def test_deploy_with_an_active_collector(self):
        stack_name, termination_protection = 'foo', True
        self._request_wrapper_mock.make_request_v2.return_value = _SAMPLE_MONOLITH_RESPONSE
        with self.assertRaises(click.exceptions.Abort):
            self._service.deploy_template(stack_name=stack_name, termination_protection=termination_protection)

    def test_replace_params(self):
        existing_params, new_params = [{'ParameterKey': 'foo', 'ParameterValue': '6'}], {'foo': '42'}
        parameters = self._service._build_param_list(existing_params=existing_params, new_params=new_params)
        self.assertEqual(parameters, [{'ParameterKey': 'foo', 'ParameterValue': '42', 'UsePreviousValue': False}])

    def test_only_existing_params(self):
        existing_params = [{'ParameterKey': 'foo', 'ParameterValue': '42'}]
        parameters = self._service._build_param_list(existing_params=existing_params, new_params=None)
        self.assertEqual(parameters, [{'ParameterKey': 'foo', 'UsePreviousValue': True}])

    def test_completely_new_params(self):
        parameters = self._service._build_param_list(existing_params=[], new_params={'foo': '42'})
        self.assertEqual(parameters, [{'ParameterKey': 'foo', 'ParameterValue': '42'}])

    @patch('montecarlodata.collector.management.click')
    def test_get_launch_link(self, click_mock):
        self._request_wrapper_mock.make_request_v2.return_value = _SAMPLE_MONOLITH_RESPONSE
        self._service.launch_quick_create_link(dry=False)

        click_mock.launch.assert_called_once_with(_SAMPLE_VALID_LAUNCH_URL)
        click_mock.echo.assert_not_called()

    @patch('montecarlodata.collector.management.click')
    def test_get_launch_link_dry_run(self, click_mock):
        self._request_wrapper_mock.make_request_v2.return_value = _SAMPLE_MONOLITH_RESPONSE
        self._service.launch_quick_create_link(dry=True)

        click_mock.echo.assert_called_once_with(_SAMPLE_VALID_LAUNCH_URL)
        click_mock.launch.assert_not_called()

    def test_set_region(self):
        region = 'loki'
        service = CollectorManagementService(
            _SAMPLE_CONFIG,
            request_wrapper=self._request_wrapper_mock,
            aws_wrapper=self._aws_wrapper_mock,
            aws_region_override=region
        )
        self.assertEqual(service._collector_region, region)
        self.assertEqual(self._service._collector_region, 'us-east-1')
        self.assertEqual(self._service._collector_region, _SAMPLE_CONFIG.aws_region)

    @patch('montecarlodata.collector.management.click')
    def test_echo_collectors(self, click_mock):
        self._user_service_mock.collectors = _SAMPLE_COLLECTORS_RESPONSE

        self._service.echo_collectors(table_format='plain')
        click_mock.echo.assert_called_once_with(
            'AWS Stack ARN      ID    Version  Template                    Last updated    Active\n'
            'aws-loki         1234       2042  cloudformation:dionysus:42  -               True\n'
            'aws-thor         5678       2042  terraform:foo:42            -               True\n'
            'aws-odin         0912       2042  cloudformation:July-2019    -               False')

    @patch('montecarlodata.collector.management.click')
    def test_echo_collectors_with_only_active(self, click_mock):
        self._user_service_mock.collectors = _SAMPLE_COLLECTORS_RESPONSE

        self._service.echo_collectors(table_format='plain', active_only=True)
        click_mock.echo.assert_called_once_with(
            'AWS Stack ARN      ID    Version  Template                    Last updated    Active\n'
            'aws-loki         1234       2042  cloudformation:dionysus:42  -               True\n'
            'aws-thor         5678       2042  terraform:foo:42            -               True')

    @patch.object(CollectorManagementService, 'launch_quick_create_link')
    @patch('montecarlodata.collector.management.prompt_connection')
    @patch('montecarlodata.collector.management.click')
    def test_add_collector(self, click_mock, prompt_connection_mock, launch_quick_create_link_mock):
        template_provider = 'provider'
        template_variant = 'variant'
        mocked_region = 'us-east-1'
        click_mock.prompt.return_value = mocked_region
        self._request_wrapper_mock.make_request_v2.return_value = MonolithResponse(data=Box({'dc': {'uuid': '1234'}}))

        self._service.add_collector(
            template_provider=template_provider,
            template_variant=template_variant
        )

        self._request_wrapper_mock.make_request_v2.assert_called_once_with(
            query=ADD_COLLECTOR_RECORD,
            operation='createCollectorRecord',
            variables = {
                'template_provider': template_provider,
                'template_variant': template_variant
            }
        )
        click_mock.echo.assert_called_once_with("Created collector record with ID '1234'")
        prompt_connection_mock.assert_called_once_with(message=ADD_DC_PROMPT_VERBIAGE)
        launch_quick_create_link_mock.assert_called_once_with(
            dry=False,
            dc_id='1234',
            collection_region=mocked_region
        )

    @patch('montecarlodata.collector.management.click')
    def test_add_collector_no_prompt(self, click_mock):
        template_provider = 'provider'
        template_variant = 'variant'

        self._request_wrapper_mock.make_request_v2.return_value = MonolithResponse(data=Box({'dc': {'uuid': '1234'}}))

        self._service.add_collector(template_provider=template_provider,
                                    template_variant=template_variant,
                                    no_prompt=True)

        self._request_wrapper_mock.make_request_v2.assert_called_once_with(
            query=ADD_COLLECTOR_RECORD,
            operation='createCollectorRecord',
            variables = {
                'template_provider': template_provider,
                'template_variant': template_variant
            }
        )
        click_mock.echo.assert_called_once_with("Created collector record with ID '1234'")
