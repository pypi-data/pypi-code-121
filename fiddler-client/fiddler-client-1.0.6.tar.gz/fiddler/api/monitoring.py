import logging
from typing import Any, Dict, Optional

from fiddler.connection import Connection
from fiddler.project import Project

from ..core_objects import (
    InitMonitoringModifications,
    possible_init_monitoring_modifications,
)
from ..utils.general_checks import type_enforce

LOG = logging.getLogger()


class Monitoring:
    def __init__(self, connection: Connection, project_id: str, model_id: str) -> None:
        self.connection = connection
        self.project_id = project_id
        self.model_id = model_id

    def initialize_monitoring(  # noqa
        self,
        enable_modify: Optional[bool] = False,
        verbose: Optional[bool] = False,
    ):
        """
        Ensure that monitoring has been setup and Fiddler is ready to ingest events.

        :param enable_modify:       Grant the Fiddler backend permission to
                                    modify model related objects, schema, etc.

                                    Can be bool  `True`/`False`, indicating global
                                    write/read-only permission.

                                    Alternatively, can be a sequence of elements
                                    from `fiddler.core_objects.InitMonitoringModifications`,
                                    in which case all listed elements will be
                                    assumed to be modifiable, and omitted ones
                                    will be read-only.
        :param verbose:             Bool indicating whether to run in verbose
                                    mode with longer debug messages for errors.

        :returns bool indicating whether monitoring could be setup correctly.
        """
        # TODO: only trigger model predictions if they do not already exist
        model_info = None
        dataset_id = None
        try:
            # model_info = self.get_model_info(self.project_id, self.model_id)
            model_info = (
                Project(self.connection, self.project_id)
                .model(self.model_id)
                .get_info()
            )
        except Exception as e:
            LOG.exception(
                f'Did not find ModelInfo for project "{self.project_id}" and model "{self.model_id}".'
            )
            raise e
        try:
            assert model_info is not None and model_info.datasets is not None
            dataset_id = model_info.datasets[0]
            assert dataset_id is not None
        except Exception as e:  # TODO: don't catch all exceptions.
            LOG.exception(
                f'Unable to infer dataset from model_info for given project_id={self.project_id} and model_id={self.model_id}. Did your model_info specify a dataset?'
            )
            if verbose:
                LOG.exception(
                    f'The inferred dataset_id was:\n{dataset_id}\n\nThe inferred model_info was:\n{model_info}'
                )
            raise e
        self._check_and_trigger_predictions(dataset_id)
        default_modify = False
        if isinstance(enable_modify, bool):
            default_modify = enable_modify
        enable_backend_modifications = {
            check.value: default_modify
            for check in possible_init_monitoring_modifications
        }
        if isinstance(enable_modify, list) or isinstance(enable_modify, tuple):
            for mod in enable_modify:
                if type(mod) == InitMonitoringModifications:
                    mod = mod.value
                enable_backend_modifications[mod] = True
        elif type(enable_modify) == bool:
            pass
        else:
            raise NotImplementedError

        overall_result = True
        init_result = self._init_monitoring_api_call(
            verbose, enable_backend_modifications
        )
        overall_result = overall_result and init_result['success']
        # For now, we only permit precomputation if no failures are found # TODO: allow precomputations for incomplete schema?
        if init_result['success'] is False:
            return False
        if verbose:
            LOG.info('Precomputing Dataset Histograms')
        precompute_result = self._precompute_api_call(verbose)
        overall_result = overall_result and precompute_result['success']

        if verbose:
            LOG.info(
                f'overall_result: {overall_result},\n\t- init_result: {init_result},\n\t- precompute_result: {precompute_result}'
            )
        return overall_result

    def _precompute_api_call(self, verbose):
        precompute_result = None
        try:
            path = [
                'precompute',
                self.connection.org_id,
                self.project_id,
                self.model_id,
            ]
            payload = {
                # 'dataset': dataset_id,
            }
            precompute_result = self.connection.call(path, json_payload=payload)
        except Exception as e:
            LOG.exception('Failed to precompute histograms, error message: ')
            raise e
        if precompute_result is not None:
            if precompute_result['success']:
                if verbose:
                    LOG.info('Successfully precomputed histograms, details: ')
                    LOG.info(precompute_result['message'])
            else:
                LOG.info('Failed to precompute histograms, details: ')
                LOG.info(precompute_result['message'])
        else:
            LOG.info(
                'Failed to precompute histograms, could not parse server response.'
            )
            precompute_result = {'success': False}
        return precompute_result

    def _init_monitoring_api_call(self, verbose, enable_backend_modifications):
        init_result = None
        try:
            path = [
                'init_monitoring',
                self.connection.org_id,
                self.project_id,
                self.model_id,
            ]
            payload = {}
            payload['enable_modifications'] = enable_backend_modifications
            init_result = self.connection.call(path, json_payload=payload)
        except Exception as e:
            LOG.exception('Failed to setup monitoring, error message: ')
            raise e
        if init_result is not None:
            if init_result['success']:
                if verbose:
                    LOG.warning(f"ERRORS: {init_result['errors']}")
                    LOG.warning(f"MESSAGE: {init_result['message']}")
            else:
                LOG.warning(f"ERRORS: {init_result['errors']}")
                LOG.warning(f"MESSAGE: {init_result['message']}")
        else:
            LOG.warning('Failed to setup monitoring, could not parse server response.')
            init_result = {'success': False}
        return init_result

    def _check_and_trigger_predictions(self, dataset_id):
        predictions_exist = False
        try:
            path = ['model_predictions_exist', self.connection.org_id, self.project_id]
            payload: Dict[str, Any] = {
                'model': self.model_id,
                'dataset': dataset_id,
            }  # is dataset_id same as dataset_name?
            predictions_exist = self.connection.call(path, json_payload=payload)
        except Exception as e:
            LOG.warning('Failed to check for predictions, regenerating by default')
            LOG.warning(str(e))
        if not predictions_exist:
            Project(self.connection, self.project_id).model(
                self.model_id
            )._trigger_model_predictions(dataset_id)
        else:
            LOG.info(
                f'Predictions already exist for model={self.model_id}, dataset={dataset_id}'
            )

    def add_monitoring_config(
        self,
        config_info: dict,
    ):
        """Adds a config for either an entire org, or project or a model.
        Here's a sample config:
        {
            'min_bin_value': 3600, # possible values 300, 3600, 7200, 43200, 86400, 604800 secs
            'time_ranges': ['Day', 'Week', 'Month', 'Quarter', 'Year'],
            'default_time_range': 7200,
            'tag': 'anything you want',
            ‘aggregation_config’: {
               ‘baseline’: {
                  ‘type’: ‘dataset’,
                  ‘dataset_name’: yyy
               }
            }
        }
        """
        # Type enforcement
        project_id = (
            type_enforce('project_id', self.project_id, str)
            if self.project_id
            else self.project_id
        )
        model_id = (
            type_enforce('model_id', self.model_id, str)
            if self.model_id
            else self.model_id
        )

        path = ['monitoring_setup', self.connection.org_id]
        if project_id:
            path.append(project_id)
        if model_id:
            if not project_id:
                raise ValueError(
                    'We need to have a `project_id` when a model is specified'
                )
            path.append(model_id)

        result = self.connection.call(path, config_info)
        self._dataset_baseline_display_message(result)
        return result

    def _dataset_baseline_display_message(self, config):
        try:
            aggregation_config_baseline = config['aggregation_config']['baseline']
            aggregation_config_baseline_type = aggregation_config_baseline['type']
            if aggregation_config_baseline_type == 'dataset':
                LOG.info(
                    'Dataset baseline will only be monitoring columns that are both present in the training data '
                    'and the specified dataset used as baseline'
                )
        except KeyError:
            pass
