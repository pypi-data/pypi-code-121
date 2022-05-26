import json
import os
import pathlib
from unittest import TestCase
from unittest.mock import Mock, patch

from montecarlodata.common.data import MonolithResponse
from montecarlodata.iac.mc_config_service import MonteCarloConfigService
from montecarlodata.queries.iac import CREATE_OR_UPDATE_MONTE_CARLO_CONFIG_TEMPLATE
from montecarlodata.utils import GqlWrapper
from tests.test_common_user import _SAMPLE_CONFIG


class MonteCarloConfigServiceTest(TestCase):
    def setUp(self) -> None:
        self._request_wrapper_mock = Mock(autospec=GqlWrapper)

    @patch('os.getcwd')
    def test_standalone_configs(self, getcwd):
        project_dir = self._get_project_dir('standalone_configs')
        getcwd.return_value = project_dir
        service = MonteCarloConfigService(_SAMPLE_CONFIG, self._request_wrapper_mock)
        files, template, _ = service.compile()
        self.assertEqual(len(files), 3)
        self.assertEqual(
            template,
            {
                'field_health': [{
                    'table': 'analytics:prod.client_hub',
                    'fields': ['account_id']
                }],
                'dimension_tracking': [{
                    'table': 'analytics:prod.customer_360',
                    'field': 'account_id'
                }]
            }
        )

    @patch('os.getcwd')
    def test_embedded_dbt_configs(self, getcwd):
        getcwd.return_value = self._get_project_dir('embedded_dbt_configs')
        service = MonteCarloConfigService(_SAMPLE_CONFIG, self._request_wrapper_mock)
        files, template, _ = service.compile()

        self.assertEqual(len(files), 4)
        self.assertEqual(
            template,
            {
                'field_health': [{
                    'table': 'analytics:prod_lineage.lineage_nodes',
                    'timestamp_field': 'created'
                }, {
                    'table': 'analytics:prod.abc'
                }, {
                    'table': 'analytics:prod.client_hub',
                    'fields': ['account_id']
                }],
                'freshness': [{
                    'table': 'analytics:prod.abc',
                    'freshness_threshold': 30,
                    'schedule': {
                        'type': 'fixed',
                        'interval_minutes': 30,
                        'start_time': '2021-07-27T19:51:00'
                    }
                }],
                'dimension_tracking': [{
                    'table': 'analytics:prod.customer_360',
                    'field': 'account_id'
                }]
            }
        )

    @patch('os.getcwd')
    def test_invalid_configs(self, getcwd):
        project_dir = self._get_project_dir('invalid_configs')
        getcwd.return_value = project_dir
        service = MonteCarloConfigService(_SAMPLE_CONFIG, self._request_wrapper_mock)
        service._abort_on_error = False

        files, template, errors_by_file = service.compile(abort_on_error=False)
        errors = sorted(list(errors_by_file.items()), key=lambda x: x[0])

        file, error = errors[0]
        self.assertTrue(file.endswith('dir1/dir2/monitors.yml'))
        self.assertEqual(error, ['"custom_sql" property should be a list.'])
        file, error = errors[1]
        self.assertTrue(file.endswith('dir1/monitors.yml'))
        self.assertEqual(error, ['"field_health" property should be a list.'])

    @patch('os.getcwd')
    def test_apply(self, getcwd):
        project_dir = self._get_project_dir('standalone_configs')
        getcwd.return_value = project_dir
        namespace = 'foo'
        service = MonteCarloConfigService(_SAMPLE_CONFIG, self._request_wrapper_mock)

        self._request_wrapper_mock.make_request_v2.return_value = MonolithResponse(
            data={
                'response': {
                    'resourceModifications': [
                        {
                            'type': 'ResourceModificationType.UPDATE',
                            'description': 'Monitor: type=stats, table=analytics:prod.client_hub',
                            'resourceAsJson': '{"uuid": "ed4d07c3-58fd-44d0-8b2d-c1b020f45a69", "resource": null, "name": "monitor|type=stats|table=analytics:prod.client_hub|timestamp_field=<<NULL>>|where_condition=<<NULL>>", "table": "analytics:prod.customer_360", "type": "stats", "fields": [], "timestamp_field": null, "where_condition": null}'
                        }, {
                            'type': 'ResourceModificationType.UPDATE',
                            'description': 'Monitor: type=categories, table=analytics:prod.customer_360',
                            'resourceAsJson': '{"uuid": "ec3b0a80-d088-4dbe-acf5-150caf041574", "resource": null, "name": "monitor|type=categories|table=analytics:prod.customer_360|timestamp_field=<<NULL>>|where_condition=<<NULL>>|fields=account_id", "table": "analytics:prod.customer_360", "type": "categories", "fields": ["account_id"], "timestamp_field": null, "where_condition": null}'
                        }
                    ],
                    'changesApplied': True,
                    'errorsAsJson': '{}'
                }
            }
        )

        response = service.apply(namespace)

        config_template_as_dict = {
            'field_health': [{
                'table': 'analytics:prod.client_hub',
                'fields': ['account_id']
            }],
            'dimension_tracking': [{
                'table': 'analytics:prod.customer_360',
                'field': 'account_id'
            }]
        }

        self._request_wrapper_mock.make_request_v2.assert_called_once_with(
            query=CREATE_OR_UPDATE_MONTE_CARLO_CONFIG_TEMPLATE,
            operation='createOrUpdateMonteCarloConfigTemplate',
            variables=dict(
                namespace=namespace,
                configTemplateJson=json.dumps(config_template_as_dict),
                dryRun=False,
                resource=None
            )
        )

        self.assertEqual(response.errors, {})
        self.assertEqual(len(response.resource_modifications), 2)

    @patch('os.getcwd')
    def test_apply_with_errors(self, getcwd):
        project_dir = self._get_project_dir('standalone_configs')
        getcwd.return_value = project_dir
        namespace = 'foo'
        service = MonteCarloConfigService(_SAMPLE_CONFIG, self._request_wrapper_mock)

        self._request_wrapper_mock.make_request_v2.return_value = MonolithResponse(
            data={
                'response': {
                    'resourceModifications': [],
                    'changesApplied': False,
                    'errorsAsJson': '{"validation_errors": {"monitors": {"0": {"type": ["Unknown field."]}}}}'
                }
            })

        response = service.apply(namespace, abort_on_error=False)

        config_template_as_dict = {
            'field_health': [{
                'table': 'analytics:prod.client_hub',
                'fields': ['account_id']
            }],
            'dimension_tracking': [{
                'table': 'analytics:prod.customer_360',
                'field': 'account_id'
            }]
        }

        self._request_wrapper_mock.make_request_v2.assert_called_once_with(
            query=CREATE_OR_UPDATE_MONTE_CARLO_CONFIG_TEMPLATE,
            operation='createOrUpdateMonteCarloConfigTemplate',
            variables=dict(
                namespace=namespace,
                configTemplateJson=json.dumps(config_template_as_dict),
                dryRun=False,
                resource=None
            )
        )

        self.assertEqual(response.errors, {'validation_errors': {'monitors': {'0': {'type': ['Unknown field.']}}}})
        self.assertEqual(len(response.resource_modifications), 0)

    def _get_project_dir(self, dir_name: str):
        return os.path.join(pathlib.Path(__file__).parent.resolve(), 'test_resources', dir_name)
