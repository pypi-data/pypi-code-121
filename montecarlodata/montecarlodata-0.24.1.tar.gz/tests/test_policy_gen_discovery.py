import copy
from unittest import TestCase
from unittest.mock import Mock, patch, call

import click
from box import Box

from montecarlodata.common.data import AwsGlueAthenaResourceProperties
from montecarlodata.common.resources import CloudResourceService
from montecarlodata.discovery.policy_gen import PolicyDiscoveryService
from tests.test_network_discovery import SAMPLE_DC_PROPS

SAMPLE_BUCKET = 'foo'
SAMPLE_PATH = '/bar/qux'
SAMPLE_GET_TABLES = {
    'TableList': [{'StorageDescriptor': {'Location': f's3://{SAMPLE_BUCKET}{SAMPLE_PATH}'}}], 'NextToken': None}
SAMPLE_GET_WORKGROUP = {
    'Configuration': {'ResultConfiguration': {'OutputLocation': f's3://{SAMPLE_BUCKET}{SAMPLE_PATH}'}}}


class PolicyDiscoveryTest(TestCase):
    def setUp(self) -> None:
        self.maxDiff = None
        self._cloud_resource_service_mock = Mock(autospec=CloudResourceService)

        self._service = PolicyDiscoveryService(cloud_resource_service=self._cloud_resource_service_mock)

    @patch('montecarlodata.discovery.policy_gen.click')
    @patch('montecarlodata.discovery.policy_gen.generate_token')
    @patch('montecarlodata.discovery.policy_gen.read_files')
    @patch('montecarlodata.discovery.policy_gen.render_dumped_json')
    def test_generate_cf_role(self, render_mock, read_mock, generate_mock, click_mock):
        account, external_id, file_vals, template_vals = 'foo', '1234', {'foo': 'bar'}, {'template': {'foo': 'bar'}}
        files, collector_props = ['a', 'b', 'c'], Box({'stackArn': f'arn:partition:service:region:{account}:resource'})

        self._cloud_resource_service_mock.get_and_validate_active_collector.return_value = collector_props
        generate_mock.return_value = external_id
        read_mock.return_value = file_vals
        render_mock.return_value = template_vals

        self._service.generate_cf_role(policy_files=files)

        read_mock.assert_called_once_with(files)
        generate_mock.assert_called_once_with()
        render_mock.assert_called_once_with(
            path='../templates/aws_role.json',
            collector_account_id=account,
            collector_external_id=external_id,
            resource_policies=file_vals
        )
        click_mock.assert_has_calls(
            [
                call.echo('Generating CloudFormation template for creating a role resource.', err=True),
                call.echo(template_vals)
            ]
        )

    @patch('montecarlodata.discovery.policy_gen.complain_and_abort')
    def test_generate_cf_role_without_a_policy(self, complain_mock):
        complain_mock.side_effect = click.exceptions.Abort

        with self.assertRaises(click.exceptions.Abort):
            self._service.generate_cf_role(policy_files=[])
        complain_mock.assert_called_once_with('At least one policy is required.')

    @patch.object(PolicyDiscoveryService, '_get_common_glue_athena_props')
    @patch('montecarlodata.discovery.policy_gen.click')
    @patch('montecarlodata.discovery.policy_gen.render_dumped_json')
    def test_generate_glue_policy(self, render_mock, click_mock, common_mock):
        options, database_name, bucket_names, account_id = {'foo': 'bar'}, {'a', 'b'}, {'c', 'd'}, '1234'
        rendering = {'hello': 'world'}
        props = copy.deepcopy(SAMPLE_DC_PROPS)

        common_mock.return_value = AwsGlueAthenaResourceProperties(
            database_names=database_name,
            bucket_names=bucket_names,
            dc_resource_props=props
        )
        props.resources_client.get_caller_identity.return_value = account_id
        render_mock.return_value = rendering

        self._service.generate_glue_policy(**options)

        common_mock.assert_called_once_with(**options)
        render_mock.assert_called_once_with(
            path='../templates/glue_policy.json',
            region='us-east-1',
            account_id=account_id,
            database_names=database_name,
            data_buckets=bucket_names
        )
        click_mock.assert_has_calls(
            [
                call.echo('Generating policy for Glue.', err=True),
                call.echo(rendering)
            ]
        )

    @patch.object(PolicyDiscoveryService, '_get_workgroup_results')
    @patch.object(PolicyDiscoveryService, '_get_common_glue_athena_props')
    @patch('montecarlodata.discovery.policy_gen.click')
    @patch('montecarlodata.discovery.policy_gen.render_dumped_json')
    def test_generate_athena_policy(self, render_mock, click_mock, common_mock, workgroup_mock):
        workgroup_name = 'workgroup'
        options, bucket_name, path = {'foo': 'bar', 'workgroup_name': workgroup_name}, 'bucket', 'prefix/key'
        database_name, bucket_names, account_id, rendering = {'a', 'b'}, {'c', 'd'}, '1234', {'hello': 'world'}
        props = copy.deepcopy(SAMPLE_DC_PROPS)

        common_mock.return_value = AwsGlueAthenaResourceProperties(database_name, bucket_names, props)
        workgroup_mock.return_value = (bucket_name, path)
        props.resources_client.get_caller_identity.return_value = account_id
        render_mock.return_value = rendering

        self._service.generate_athena_policy(**options)

        common_mock.assert_called_once_with(foo='bar')
        workgroup_mock.assert_called_once_with(workgroup_name=workgroup_name, dc_resource_props=props)
        render_mock.assert_called_once_with(
            path='../templates/athena_policy.json',
            region='us-east-1',
            account_id=account_id,
            database_names=database_name,
            data_buckets=bucket_names,
            result_bucket=bucket_name,
            result_path=path,
            workgroup_name=workgroup_name
        )
        click_mock.assert_has_calls(
            [
                call.echo('Generating policy for Athena.', err=True),
                call.echo(rendering)
            ]
        )

    @patch.object(PolicyDiscoveryService, '_get_buckets')
    def test_get_common_glue_athena_props(self, bucket_mock):
        database_names, bucket_names = ['a', 'b', '*'], ['c', 'd', 'd']
        collector_props, dc_resource_props = Box({'foo': 'bar'}), copy.deepcopy(SAMPLE_DC_PROPS)

        self._cloud_resource_service_mock.get_and_validate_active_collector.return_value = collector_props
        self._cloud_resource_service_mock.get_dc_resource_props.return_value = dc_resource_props

        self.assertEqual(
            self._service._get_common_glue_athena_props(database_names=database_names, bucket_names=bucket_names),
            AwsGlueAthenaResourceProperties(
                database_names={'*'},
                bucket_names={'c', 'd'},
                dc_resource_props=dc_resource_props
            )
        )
        self._cloud_resource_service_mock.get_and_validate_active_collector.assert_called_once_with(dc_id=None)
        self._cloud_resource_service_mock.get_dc_resource_props.assert_called_once_with(
            collector_props=collector_props,
            get_stack_outputs=False,
            get_stack_params=False
        )
        bucket_mock.assert_not_called()

    @patch.object(PolicyDiscoveryService, '_get_buckets')
    def test_get_common_glue_athena_props_with_no_buckets(self, bucket_mock):
        database_names, bucket_names, dc_id = ['a', 'b', '*'], {'c', 'd'}, '1234'
        collector_props, dc_resource_props = Box({'foo': 'bar'}), copy.deepcopy(SAMPLE_DC_PROPS)

        bucket_mock.return_value = bucket_names

        self._cloud_resource_service_mock.get_and_validate_active_collector.return_value = collector_props
        self._cloud_resource_service_mock.get_dc_resource_props.return_value = dc_resource_props

        self.assertEqual(
            self._service._get_common_glue_athena_props(database_names=database_names, dc_id=dc_id),
            AwsGlueAthenaResourceProperties(
                database_names={'*'},
                bucket_names=bucket_names,
                dc_resource_props=dc_resource_props
            )
        )
        self._cloud_resource_service_mock.get_and_validate_active_collector.assert_called_once_with(dc_id=dc_id)
        self._cloud_resource_service_mock.get_dc_resource_props.assert_called_once_with(
            collector_props=collector_props,
            get_stack_outputs=False,
            get_stack_params=False
        )
        bucket_mock.assert_called_once_with(database_names={'*'}, dc_resource_props=dc_resource_props)

    @patch('montecarlodata.discovery.policy_gen.click.progressbar')
    @patch.object(PolicyDiscoveryService, '_get_table_locations')
    def test_get_buckets(self, table_location_mock, click_mock):
        class MockContext:
            def __enter__(self):
                return self

            def __iter__(self):
                for x in database_names:
                    yield x

            def __exit__(self, *args):
                pass

        tables = Box(SAMPLE_GET_TABLES, camel_killer_box=True)
        database_names, locations = {'foo', 'bar'}, {'bucket1', 'bucket2'}
        dc_resource_props = copy.deepcopy(SAMPLE_DC_PROPS)

        table_location_mock.return_value = locations
        click_mock.return_value = MockContext()

        dc_resource_props.resources_client.get_glue_tables.return_value = tables

        self.assertEqual(
            self._service._get_buckets(database_names=database_names, dc_resource_props=dc_resource_props),
            locations
        )
        table_location_mock.assert_has_calls([call(tables=tables.table_list), call(tables=tables.table_list)])
        dc_resource_props.resources_client.get_glue_tables.assert_has_calls(
            [
                call(database_name='bar', page_token=None),
                call(database_name='foo', page_token=None)
            ],
            any_order=True
        )

    def test_handle_wildcards(self):
        self.assertEqual(self._service._handle_wildcards(None), set())
        self.assertEqual(self._service._handle_wildcards([]), set())
        self.assertEqual(self._service._handle_wildcards(['foo', 'foo', 'foo']), {'foo'})
        self.assertEqual(self._service._handle_wildcards(['foo', 'foo', '*']), {'*'})

    @patch('montecarlodata.discovery.policy_gen.click.progressbar')
    def test_get_workgroup_results(self, click_mock):
        workgroup_name, dc_resource_props = 'foo', copy.deepcopy(SAMPLE_DC_PROPS)
        workgroup_details = Box(SAMPLE_GET_WORKGROUP, camel_killer_box=True)

        dc_resource_props.resources_client.get_athena_workgroup.return_value = workgroup_details
        self.assertEqual(
            self._service._get_workgroup_results(workgroup_name, dc_resource_props=dc_resource_props),
            (SAMPLE_BUCKET, SAMPLE_PATH)
        )
        dc_resource_props.resources_client.get_athena_workgroup.assert_called_once_with(workgroup=workgroup_name)

    def test_get_table_locations(self):
        tables = Box(SAMPLE_GET_TABLES, camel_killer_box=True)
        self.assertEqual(list(self._service._get_table_locations(tables=tables.table_list)), [SAMPLE_BUCKET])

    def test_get_table_locations_with_invalid_schemes(self):
        tables = Box(SAMPLE_GET_TABLES, camel_killer_box=True)
        tables.table_list[0].storage_descriptor.location = 'invalid'
        self.assertEqual(list(self._service._get_table_locations(tables=tables.table_list)), [])
