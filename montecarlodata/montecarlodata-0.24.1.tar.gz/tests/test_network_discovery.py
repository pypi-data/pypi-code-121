import copy
from unittest import TestCase
from unittest.mock import Mock, patch

import click
from box import Box

from montecarlodata.common.data import DcResourceProperties, AWSArn
from montecarlodata.common.resources import CloudResourceService
from montecarlodata.discovery.networking import NetworkDiscoveryService

SAMPLE_RESOURCE_ID = 'spensa'
SAMPLE_DC_PROPS = DcResourceProperties(
    collector_arn=AWSArn('arn:aws:cloudformation:us-east-1:1234:stack/foo/bar'),
    collector_props=Box({
        'stackArn': 'arn:aws:cloudformation:us-east-1:1234:stack/foo/bar',
        'templateVersion': '42',
        'codeVersion': '2340',
        'lastUpdated': None,
        'outputs': {
            'public_route_table': 'rtb-1234',
            'private_route_table': 'rtb-456',
            'vpc_id': 'vpc-1234',
            'public_ip': '127.0.0.1',
            'cloud_watch_log_vpc_endpoint': 'vpce-1234',
            'template_version': '2340',
            'api_gateway_id': 'foo',
            'private_s3_bucket_arn': 'arn:aws:s3:::bucket',
            'security_group': 'sg-1234'
        },
        'parameters': {
            'enable_gateway_access_logging': 'False',
            'create_event_infra': 'False',
            'existing_s3_vpce': 'N/A',
            'worker_lambda_concurrent_executions': '42',
            'subnet_cid_rs': '10.30.0.0/24,10.30.1.0/24,10.30.2.0/24,10.30.3.0/24',
            'existing_vpc_id': 'N/A',
            'create_cross_account_role': 'True',
            'existing_subnet_ids': 'N/A',
            'vpc_cidr': '10.30.0.0/16'
        }
    }),
    collection_region='us-east-1',
    resources_region='us-east-1',
    collection_client=Mock(),
    resources_client=Mock()
)
SAMPLE_RESOURCE_PROPS = Box(
    {
        'cluster_identifier': 'test-cluster-pc',
        'cluster_namespace_arn': 'arn:aws:redshift:us-east-1:1234:namespace:5678',
        'node_type': 'dc2.large',
        'endpoint': {
            'address': 'foo.com',
            'port': 5439
        },
        'vpc_security_groups': [{
            'vpc_security_group_id': 'sg-0987',
            'status': 'active'
        }, {
            'vpc_security_group_id': 'sg-6543',
            'status': 'active'
        }],
        'cluster_security_groups': [],
        'publicly_accessible': True,
        'vpc_id': 'vpc-5678'
    }
)


class NetworkDiscoveryTest(TestCase):
    def setUp(self) -> None:
        self.maxDiff = None
        self._cloud_resource_service_mock = Mock(autospec=CloudResourceService)

        self._service = NetworkDiscoveryService(cloud_resource_service=self._cloud_resource_service_mock)

    def tearDown(self) -> None:
        SAMPLE_DC_PROPS.collection_client.reset_mock()
        SAMPLE_DC_PROPS.resources_client.reset_mock()

    @patch.object(NetworkDiscoveryService, 'rs_network_recommender')
    def test_recommend_network_dispatcher(self, rs_network_recommender_mock):
        resource_type, dc_id = 'redshift', '42'
        collector_props = dc_resource_props = Box({'foo': 'bar'})

        self._cloud_resource_service_mock.get_and_validate_active_collector.return_value = collector_props
        self._cloud_resource_service_mock.get_dc_resource_props.return_value = collector_props

        self._service.recommend_network_dispatcher(resource_type=resource_type, dc_id=dc_id)
        self._cloud_resource_service_mock.get_and_validate_active_collector.assert_called_once_with(dc_id=dc_id)
        self._cloud_resource_service_mock.get_dc_resource_props.assert_called_once_with(collector_props=collector_props)

        rs_network_recommender_mock.assert_called_once_with(dc_resource_props=dc_resource_props)

    @patch.object(NetworkDiscoveryService, 'rs_network_recommender')
    @patch('montecarlodata.discovery.networking.complain_and_abort')
    def test_recommend_network_dispatcher_with_invalid_resource_type(self, abort_mock, rs_network_recommender_mock):
        self._service.recommend_network_dispatcher(resource_type='foo')
        abort_mock.assert_called_once_with("Unsupported resource type - 'foo'.")
        rs_network_recommender_mock.assert_not_called()

    @patch.object(NetworkDiscoveryService, '_get_rs_sg')
    @patch.object(NetworkDiscoveryService, '_echo_recommendation')
    @patch.object(NetworkDiscoveryService, '_get_ip_filtering_verbiage')
    def test_rs_network_recommender_with_filtering(self, ip_filtering_mock, echo_mock, sg_mock):
        filtering_body, sg = ['foo', 'bar', 'qux'], ['sg-1234', 'sg-5678']
        SAMPLE_DC_PROPS.resources_client.describe_vpc.return_value = Box(cidr_block='127.0.0.1/32')

        SAMPLE_DC_PROPS.resources_client.describe_redshift_cluster.return_value = SAMPLE_RESOURCE_PROPS
        ip_filtering_mock.return_value = filtering_body
        sg_mock.return_value = sg, True
        self._service.rs_network_recommender(dc_resource_props=SAMPLE_DC_PROPS, resource_identifier=SAMPLE_RESOURCE_ID)

        ip_filtering_mock.assert_called_once_with(SAMPLE_DC_PROPS, sg)
        sg_mock.assert_called_once_with(SAMPLE_DC_PROPS)
        echo_mock.assert_called_once_with(
            filtering_body,
            header_col='The redshift cluster \'spensa\' is publicly accessible.'
        )
        SAMPLE_DC_PROPS.resources_client.describe_vpc.assert_called_once_with(SAMPLE_RESOURCE_PROPS.vpc_id)
        SAMPLE_DC_PROPS.resources_client.describe_redshift_cluster.assert_called_once_with(
            cluster_id=SAMPLE_RESOURCE_ID)

    @patch.object(NetworkDiscoveryService, '_echo_recommendation')
    @patch('montecarlodata.discovery.networking.complain_and_abort')
    @patch.object(NetworkDiscoveryService, '_get_rs_sg')
    def test_rs_network_with_invalid_vpc_type(self, sg_mock, abort_mock, echo_mock):
        resource_props = SAMPLE_RESOURCE_PROPS
        resource_props.publicly_accessible = False

        SAMPLE_DC_PROPS.resources_client.describe_redshift_cluster.return_value = resource_props
        sg_mock.return_value = [], False
        abort_mock.side_effect = click.Abort()

        with self.assertRaises(click.exceptions.Abort):
            self._service.rs_network_recommender(dc_resource_props=SAMPLE_DC_PROPS,
                                                 resource_identifier=SAMPLE_RESOURCE_ID)
        SAMPLE_DC_PROPS.resources_client.describe_redshift_cluster.assert_called_once_with(
            cluster_id=SAMPLE_RESOURCE_ID)
        SAMPLE_DC_PROPS.resources_client.describe_vpc.assert_called_once_with(SAMPLE_RESOURCE_PROPS.vpc_id)

        abort_mock.assert_called_once_with('Recommender does not support non-public clusters deployed outside a VPC.')
        echo_mock.assert_not_called()
        sg_mock.assert_called_once_with(SAMPLE_DC_PROPS)

    @patch.object(NetworkDiscoveryService, '_get_peering_intro_verbiage')
    @patch.object(NetworkDiscoveryService, '_get_rs_sg')
    @patch.object(NetworkDiscoveryService, '_echo_recommendation')
    @patch.object(NetworkDiscoveryService, '_get_overlap_verbiage')
    @patch('montecarlodata.discovery.networking.is_overlap')
    def test_rs_network_with_with_overlap(self, is_overlap_mock, overlap_verbiage_mock, echo_mock, sg_mock, intro_mock):
        rs_cidr = '127.0.0.1/32'
        overlap_verbiage, intro_verbiage = ['foo', 'bar'], ['qux', 'baz']
        resource_props = SAMPLE_RESOURCE_PROPS
        resource_props.publicly_accessible = False

        SAMPLE_DC_PROPS.resources_client.describe_redshift_cluster.return_value = resource_props
        sg_mock.return_value = [], True
        is_overlap_mock.return_value = True
        overlap_verbiage_mock.return_value = overlap_verbiage
        intro_mock.return_value = intro_verbiage
        SAMPLE_DC_PROPS.resources_client.describe_vpc.return_value = Box(cidr_block=rs_cidr)

        self._service.rs_network_recommender(dc_resource_props=SAMPLE_DC_PROPS, resource_identifier=SAMPLE_RESOURCE_ID)

        SAMPLE_DC_PROPS.resources_client.describe_redshift_cluster.assert_called_once_with(
            cluster_id=SAMPLE_RESOURCE_ID)
        SAMPLE_DC_PROPS.resources_client.describe_vpc.assert_called_once_with(SAMPLE_RESOURCE_PROPS.vpc_id)
        is_overlap_mock.assert_called_once_with(rs_cidr, SAMPLE_DC_PROPS.collector_props.parameters.vpc_cidr)
        overlap_verbiage_mock.assert_called_once_with(SAMPLE_DC_PROPS.collector_props.parameters.vpc_cidr, rs_cidr)
        sg_mock.assert_called_once_with(SAMPLE_DC_PROPS)
        intro_mock.assert_called_once_with(True)
        echo_mock.assert_called_once_with(
            [*intro_verbiage, overlap_verbiage],
            header_col='The redshift cluster \'spensa\' is not publicly accessible.'
        )

    @patch.object(NetworkDiscoveryService, '_get_rs_routes')
    @patch.object(NetworkDiscoveryService, '_echo_recommendation')
    @patch.object(NetworkDiscoveryService, '_get_extra_verbiage')
    @patch.object(NetworkDiscoveryService, '_get_rs_accepter_verbiage')
    @patch.object(NetworkDiscoveryService, '_get_rs_requester_verbiage')
    @patch.object(NetworkDiscoveryService, '_get_rs_cross_account_verbiage')
    @patch.object(NetworkDiscoveryService, '_get_peering_intro_verbiage')
    @patch.object(NetworkDiscoveryService, '_get_rs_sg')
    @patch('montecarlodata.discovery.networking.is_overlap')
    def test_rs_network_with_peering(self, is_overlap_mock, sg_mock, intro_mock, cross_mock, req_mock, acc_mock,
                                     extra_mock, echo_mock, rs_mock):
        rs_cidr = '127.0.0.1/32'
        resource_props = SAMPLE_RESOURCE_PROPS
        resource_props.publicly_accessible = False

        sg_mock.return_value = ['foo'], True
        is_overlap_mock.return_value = False
        intro_mock.return_value = ['a']
        cross_mock.return_value = ['b']
        req_mock.return_value = ['c']
        acc_mock.return_value = ['d']
        extra_mock.return_value = ['e']
        rs_mock.return_value = ['bar']
        SAMPLE_DC_PROPS.resources_client.describe_vpc.return_value = Box(cidr_block=rs_cidr)
        SAMPLE_DC_PROPS.resources_client.describe_redshift_cluster.return_value = resource_props

        self._service.rs_network_recommender(dc_resource_props=SAMPLE_DC_PROPS, resource_identifier=SAMPLE_RESOURCE_ID)

        SAMPLE_DC_PROPS.resources_client.describe_redshift_cluster.assert_called_once_with(
            cluster_id=SAMPLE_RESOURCE_ID)
        SAMPLE_DC_PROPS.resources_client.describe_vpc.assert_called_once_with(SAMPLE_RESOURCE_PROPS.vpc_id)
        is_overlap_mock.assert_called_once_with(rs_cidr, SAMPLE_DC_PROPS.collector_props.parameters.vpc_cidr)
        sg_mock.assert_called_once_with(SAMPLE_DC_PROPS)

        echo_mock.assert_called_once_with(
            ['a', 'b', 'c', 'd', 'e'],
            header_col='The redshift cluster \'spensa\' is not publicly accessible.'
        )
        intro_mock.assert_called_once_with(True)
        cross_mock.assert_called_once_with(SAMPLE_DC_PROPS, True)
        req_mock.assert_called_once_with(SAMPLE_DC_PROPS, True, rs_cidr)
        acc_mock.assert_called_once_with(SAMPLE_DC_PROPS, ['foo'], ['bar'])
        extra_mock.assert_called_once_with()

    @patch('montecarlodata.discovery.networking.complain_and_abort')
    def test_check_collector_validity(self, abort_mock):
        self.assertIsNone(self._service._check_collector_validity(SAMPLE_DC_PROPS))
        abort_mock.assert_not_called()

    @patch('montecarlodata.discovery.networking.complain_and_abort')
    def test_check_collector_validity_existing_vpc(self, abort_mock):
        props = copy.deepcopy(SAMPLE_DC_PROPS)
        props.collector_props.parameters.existing_vpc_id = 'vpc-foo'

        self._service._check_collector_validity(props)
        abort_mock.assert_called_once_with('Recommender does not support collectors deployed in customer managed VPCs.')

    def test_get_get_rs_sg_with_vpc(self):
        props = copy.deepcopy(SAMPLE_DC_PROPS)
        props.resource_props = SAMPLE_RESOURCE_PROPS

        sg, in_vpc = self._service._get_rs_sg(props)
        self.assertEqual(sg, ['sg-0987', 'sg-6543'])
        self.assertTrue(in_vpc)

    @patch('montecarlodata.discovery.networking.complain_and_abort')
    def test_get_rs_sg_invalid(self, abort_mock):
        props = copy.deepcopy(SAMPLE_DC_PROPS)
        props.resource_props = SAMPLE_RESOURCE_PROPS
        props.resource_props.cluster_security_groups = ['foo']

        self._service._get_rs_sg(props)
        abort_mock.assert_called_once_with('Recommender does not support clusters with ambiguous hosting. '
                                           'Cluster cannot have security groups both inside and outside a VPC.')

    def test_get_rs_routes(self):
        props = copy.deepcopy(SAMPLE_DC_PROPS)
        props.resource_props = SAMPLE_RESOURCE_PROPS
        props.resource_props.cluster_subnet_group_name = 'foo'

        props.resources_client.describe_cluster_subnet_groups.return_value = Box(subnets=[{'subnet_identifier': 'bar'}])
        props.resources_client.describe_routes.return_value = Box(route_tables=[{'route_table_id': 'qux'}])

        self.assertEqual(list(self._service._get_rs_routes(props)), ['qux'])
        props.resources_client.describe_routes.assert_called_once_with(filter_vals=['bar'])
        props.resources_client.describe_cluster_subnet_groups.assert_called_once_with(subnet_group='foo')

    def test_get_ip_filtering_verbiage(self):
        sg = ['foo', 'bar']
        props = copy.deepcopy(SAMPLE_DC_PROPS)
        props.resource_props = SAMPLE_RESOURCE_PROPS

        self.assertEqual(
            self._service._get_ip_filtering_verbiage(props, sg),
            [
                'IP filtering is recommended. See steps below.',
                '',
                "Whitelist port '5439' for '127.0.0.1/32' in any of the following redshift "
                f"security groups - {sg}.",
                'https://docs.getmontecarlo.com/docs/network-connectivity#ip-filtering'
            ]
        )

    def test_get_rs_cross_account_verbiage(self):
        props = copy.deepcopy(SAMPLE_DC_PROPS)
        props.resource_props = SAMPLE_RESOURCE_PROPS
        self.assertEqual(
            self._service._get_rs_cross_account_verbiage(props, False),
            [
                "- Deploy the 'Create Peering Cross Account assumable role CloudFormation "
                "stack' with the following values -",
                '1. Data Collector AWS Account ID: 1234',
                'https://docs.getmontecarlo.com/docs/peering-templates#create-peering-cross-account-assumable-role-cloudformation-stack',
                ''
            ]
        )

    def test_get_rs_cross_account_verbiage_in_same_account(self):
        props = copy.deepcopy(SAMPLE_DC_PROPS)
        props.resource_props = SAMPLE_RESOURCE_PROPS
        self.assertEqual(self._service._get_rs_cross_account_verbiage(props, True), [])

    def test_get_rs_requester_verbiage(self):
        props = copy.deepcopy(SAMPLE_DC_PROPS)
        props.resource_props = SAMPLE_RESOURCE_PROPS
        props.resource_arn = AWSArn(SAMPLE_RESOURCE_PROPS.cluster_namespace_arn)

        self.assertEqual(
            self._service._get_rs_requester_verbiage(props, False, '127.0.0.1/32'),
            [
                "- Deploy the  'Create Requester CloudFormation stack' with the following "
                'values -',
                "1. Monte Carlo Data Collector VPC ID: 'vpc-1234'",
                "2. Monte Carlo Data Collector Security Group ID: 'sg-1234'",
                "3. Monte Carlo Data Collector Route Table ID: 'rtb-456'",
                "4. Warehouse/resource VPC ID: 'vpc-5678'",
                "5. Warehouse/resource AWS Account ID: '1234'",
                "6. Warehouse/resource AWS Region: 'us-east-1'",
                "7. Warehouse/resource CIDR Block: '127.0.0.1/32'",
                '8. VPC peer role for cross AWS account connections: <PeeringRole from the '
                'output of the previous stack>',
                'https://docs.getmontecarlo.com/docs/peering-templates#create-requester-cloudformation-stack',
                ''
            ]
        )

    def test_get_rs_accepter_verbiage(self):
        sg, routes = ['a'], ['b']
        props = copy.deepcopy(SAMPLE_DC_PROPS)
        props.resource_props = SAMPLE_RESOURCE_PROPS
        props.resource_arn = AWSArn(SAMPLE_RESOURCE_PROPS.cluster_namespace_arn)

        self.assertEqual(
            self._service._get_rs_accepter_verbiage(props, sg, routes),
            [
                "- Deploy the  'Create Accepter CloudFormation stack' with the following "
                'values -',
                "1. Monte Carlo Data Collector CIDR Block: '10.30.0.0/16'",
                '2. Monte Carlo Data Collector Peering Connection: <PeeringConnection from '
                'the output of the previous stack>',
                "3. Resource / Warehouse Security Group: 'a'",
                "4. Resource / Warehouse Route Table #1: 'b'",
                'https://docs.getmontecarlo.com/docs/peering-templates#create-accepter-cloudformation-stack',
                ''
            ]
        )

    def test_get_overlap_verbiage(self):
        self.assertEqual(
            self._service._get_overlap_verbiage('a', 'b'),
            'Collector range (a) overlaps with resource (b). Peering is not possible when peered VPCs use overlapping '
            'CIDR blocks. Please redeploy the collector with a custom CIDR block then rerun recommender.'
        )

    def test_get_peering_intro_verbiage(self):
        self.assertEqual(
            self._service._get_peering_intro_verbiage(True),
            [
                'VPC Peering is recommended. See the outlined steps for each of the 2 '
                'sections below.',
                '',
                'The CloudFormation template can be found by following the link at the end of '
                'each section.',
                'Please complete all 2 sections, and for any additional help, reach out to '
                'your Monte Carlo representative.',
                ''
            ]
        )

    def test_get_extra_verbiage(self):
        self.assertEqual(
            self._service._get_extra_verbiage(),
            [
                'If the cluster\'s subnets use a non-default ACL the collector '
                'CIDR Block also likely need to be whitelisted.'
            ]
        )

    def test_get_friendly_sg_verbiage(self):
        self.assertEqual(self._service._get_friendly_sg_verbiage(['a']), "'a'")

    def test_get_friendly_sg_verbiage_multi(self):
        self.assertEqual(self._service._get_friendly_sg_verbiage(['a', 'b']), "Any of the following - a,b")

    @patch('montecarlodata.discovery.networking.click')
    def test_echo_recommendation(self, click_mock):
        self._service._echo_recommendation(['a', 'b'], table_format='plain')
        click_mock.echo.assert_called_once_with('Recommendations\na\nb')
