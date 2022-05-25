# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains functionality for deploying models to AzureML through MLFlow."""

import json
import logging
import tempfile
from azureml.core import Webservice, Model as AzureModel
from azureml.core.webservice import AciWebservice
from azureml.exceptions import WebserviceException
from azureml.mlflow._internal.utils import load_azure_workspace
from azureml._model_management._util import deploy_config_dict_to_obj, get_requests_session
from azureml._restclient.clientbase import ClientBase
from mlflow.deployments import BaseDeploymentClient
from mlflow.exceptions import MlflowException
from mlflow.utils.annotations import experimental
from mlflow.utils.file_utils import TempDir
from ._util import (file_stream_to_object, handle_model_uri, load_model_environent, create_inference_config,
                    submit_update_call, get_deployments_import_error, submit_rest_request,
                    get_and_poll_on_async_op, convert_v2_deploy_config_to_rest_config, get_base_arm_request_route)
from azureml.mlflow._internal.constants import NUMPY_SWAGGER_FORMAT


_logger = logging.getLogger(__name__)


class AzureMLDeploymentClient(BaseDeploymentClient):
    """Client object used to deploy MLFlow models to AzureML."""

    def __init__(self, target_uri):
        """
        Initialize the deployment client with the MLFlow target uri.

        :param target_uri: AzureML workspace specific target uri.
        :type target_uri: str
        """
        super(AzureMLDeploymentClient, self).__init__(target_uri)
        try:
            self.workspace = load_azure_workspace()
        except Exception as e:
            raise MlflowException("Failed to retrieve AzureML Workspace") from e

        self.v2_api_version = '2021-10-01'

    @experimental
    def create_deployment(self, name, model_uri, flavor=None, config=None, endpoint=None):
        """
        Deploy a model to the specified target.

        Deploy a model to the specified target. By default, this method should block until
        deployment completes (i.e. until it's possible to perform inference with the deployment).
        In the case of conflicts (e.g. if it's not possible to create the specified deployment
        without due to conflict with an existing deployment), raises a
        :py:class:`mlflow.exceptions.MlflowException`. See target-specific plugin documentation
        for additional detail on support for asynchronous deployment and other configuration.

        :param name: Unique name to use for deployment. If another deployment exists with the same
                     name, raises a :py:class:`mlflow.exceptions.MlflowException`
        :param model_uri: URI of model to deploy. AzureML supports deployments of 'models', 'runs', and 'file' uris.
        :param flavor: (optional) Model flavor to deploy. If unspecified, a default flavor
                       will be chosen.
        :param config: (optional) Dict containing updated target-specific configuration for the
                       deployment
        :param endpoint: (optional) Endpoint to create the deployment under
        :return: Dict corresponding to created deployment, which must contain the 'name' key.
        """
        if flavor and flavor != 'python_function':
            raise MlflowException('Unable to use {} model flavor, '
                                  'AML currently only supports python_function.'.format(flavor))

        model_name, model_version = handle_model_uri(model_uri, name)

        try:
            aml_model = AzureModel(self.workspace, id='{}:{}'.format(model_name, model_version))
        except Exception as e:
            raise MlflowException('Failed to retrieve model to deploy') from e

        v1_deploy_config = None
        v2_deploy_config = None

        # Convert passed in file to deployment config
        if config and 'deploy-config-file' in config:
            with open(config['deploy-config-file'], 'r') as deploy_file_stream:
                deploy_config_obj = file_stream_to_object(deploy_file_stream)
                try:
                    if 'computeType' in deploy_config_obj:
                        v1_deploy_config = deploy_config_dict_to_obj(deploy_config_obj, deploy_config_obj.get('tags'),
                                                                     deploy_config_obj.get('properties'),
                                                                     deploy_config_obj.get('description'))
                    else:
                        if 'type' in deploy_config_obj and deploy_config_obj['type'].lower() != 'managed':
                            raise MlflowException('Unable to deploy MLFlow model to {} compute, currently only '
                                                  'supports Managed '
                                                  'compute.'.format(deploy_config_obj['endpointComputeType']))
                        if 'model' in deploy_config_obj:
                            raise MlflowException('Unable to provide model information in the deployment config file '
                                                  'when deploying through MLFlow. Please use the `model_uri` '
                                                  'parameter.')
                        else:
                            deploy_config_obj['model'] = \
                                '/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/' \
                                'Microsoft.MachineLearningServices/workspaces/{workspace_name}/models/{model_name}/' \
                                'versions/{model_version}'.format(subscription_id=self.workspace.subscription_id,
                                                                  resource_group=self.workspace.resource_group,
                                                                  workspace_name=self.workspace.name,
                                                                  model_name=model_name, model_version=model_version)
                        if 'code_configuration' in deploy_config_obj or 'environment' in deploy_config_obj or \
                                'endpoint_name' in deploy_config_obj:
                            raise MlflowException(
                                'code_configuration, environment, and endpoint_name are not used with '
                                'MLFlow deployments. Please remove from the deployment config and '
                                'try again.')
                        v2_deploy_config = deploy_config_obj
                except Exception as e:
                    raise MlflowException('Failed to parse provided configuration file') from e
        else:
            if not endpoint:
                v1_deploy_config = AciWebservice.deploy_configuration()

        if v1_deploy_config:
            deployment = self._v1_create_deployment(name, model_name, model_version, aml_model, config,
                                                    v1_deploy_config)
        else:
            deployment = self._v2_create_deployment(name, model_name, model_version, v2_deploy_config, endpoint)

        if 'flavor' not in deployment:
            deployment['flavor'] = flavor if flavor else 'python_function'
        return deployment

    def _v1_create_deployment(self, name, model_name, model_version, aml_model, create_deployment_config,
                              v1_deploy_config):
        with TempDir(chdr=True) as tmp_dir:
            model_conf = load_model_environent(tmp_dir, model_name, model_version, name)
            inference_config = create_inference_config(tmp_dir, **model_conf)
            try:
                _logger.info("Creating an AzureML deployment with name: `%s`", name)

                # Deploy
                webservice = AzureModel.deploy(
                    workspace=self.workspace,
                    name=name,
                    models=[aml_model],
                    inference_config=inference_config,
                    deployment_config=v1_deploy_config,
                )

                if create_deployment_config and 'async' in create_deployment_config and \
                        create_deployment_config['async']:
                    _logger.info('AzureML deployment in progress, you can use get_deployment to check on the '
                                 'current deployment status.')
                else:
                    webservice.wait_for_deployment(show_output=True)
            except Exception as e:
                raise MlflowException('Error while creating deployment') from e

            return webservice.serialize()

    def _v2_create_deployment(self, name, model_name, model_version, v2_deploy_config=None, endpoint=None):
        # Create Endpoint if necessary
        if not endpoint:
            _logger.info('Creating endpoint with name {} to create deployment under')
            self.create_endpoint(name, None)

        # Create Deployment using v2_deploy_config
        endpoint_name = endpoint if endpoint else name
        base_uri = '{arm_base}/subscriptions/{subscription_id}/resourceGroups/' \
                   '{resource_group}/providers/Microsoft.MachineLearningServices/workspaces/' \
                   '{workspace_name}'.format(arm_base=get_base_arm_request_route(self.workspace),
                                             subscription_id=self.workspace.subscription_id,
                                             resource_group=self.workspace.resource_group,
                                             workspace_name=self.workspace.name)
        endpoint_request_uri = base_uri + '/onlineEndpoints/{endpoint_name}'.format(endpoint_name=endpoint_name)
        deployment_request_uri = endpoint_request_uri + '/deployments/{deployment_name}'.format(deployment_name=name)
        deployment_request_headers = {'Content-Type': 'application/json'}
        deployment_request_headers.update(self.workspace._auth_object.get_authentication_header())
        deployment_request_params = {'api-version': self.v2_api_version}

        deployment_request_body = {
            "location": self.workspace.location,
            "properties": convert_v2_deploy_config_to_rest_config(self.workspace, model_name, model_version,
                                                                  v2_deploy_config),
            "sku": {
                "name": "default",
                "capacity": 1
            }
        }

        _logger.info('Starting deployment request')
        resp = submit_rest_request(get_requests_session().put, deployment_request_uri, deployment_request_body,
                                   deployment_request_params, deployment_request_headers)
        get_and_poll_on_async_op(resp, self.workspace, 'Deployment Create')

        # Update Endpoint traffic, only if we are implicitly creating the endpoint for the user
        if not endpoint:
            _logger.info('Updating endpoint to serve 100 percent traffic to deployment {}'.format(name))
            update_config = {"traffic": {name: 100}}
            self._update_endpoint(endpoint_name, update_config)
        else:
            _logger.info('Deployment created. Be sure to update your endpoint with desired traffic settings.')

        return self.get_deployment(name, endpoint)

    @experimental
    def update_deployment(self, name, model_uri=None, flavor=None, config=None, endpoint=None):
        """
        Update the deployment specified by name.

        Update the deployment with the specified name. You can update the URI of the model, the
        flavor of the deployed model (in which case the model URI must also be specified), and/or
        any target-specific attributes of the deployment (via `config`). By default, this method
        should block until deployment completes (i.e. until it's possible to perform inference
        with the updated deployment). See target-specific plugin documentation for additional
        detail on support for asynchronous deployment and other configuration.

        :param name: Unique name of deployment to update
        :param model_uri: URI of a new model to deploy.
        :param flavor: (optional) new model flavor to use for deployment. If provided,
                       ``model_uri`` must also be specified. If ``flavor`` is unspecified but
                       ``model_uri`` is specified, a default flavor will be chosen and the
                       deployment will be updated using that flavor.
        :param config: (optional) dict containing updated target-specific configuration for the
                       deployment
        :param endpoint: (optional) Endpoint containing the deployment to update.
        :return: None
        """
        if endpoint:
            endpoint_name = endpoint
        else:
            endpoint = self.get_endpoint(name)
            endpoint_name = name

        if endpoint:
            deployment = self.get_deployment(name, endpoint_name)
            if deployment:
                self._v2_deployment_update(name, endpoint_name, model_uri, flavor, config)
            else:
                raise MlflowException('No deployment with name {} found to update'.format(name))
        else:
            service = self._get_v1_service(name)
            if service:
                self._v1_deployment_update(service, name, model_uri, flavor, config)
            else:
                raise MlflowException('No deployment with name {} found to update'.format(name))

    def _v1_deployment_update(self, service, name, model_uri=None, flavor=None, config=None):
        models = None
        inference_config = None

        deploy_config = None
        if config and 'deploy-config-file' in config:
            try:
                with open(config['deploy-config-file'], 'r') as deploy_file_stream:
                    deploy_config_obj = file_stream_to_object(deploy_file_stream)
                    deploy_config = deploy_config_dict_to_obj(
                        deploy_config_obj, deploy_config_obj.get('tags'),
                        deploy_config_obj.get('properties'), deploy_config_obj.get('description')
                    )
            except Exception as e:
                raise MlflowException('Failed to parse provided deployment config file') from e

        aks_endpoint_version_config = None
        if config and 'aks-endpoint-deployment-config' in config:
            aks_endpoint_version_config = config['aks-endpoint-deployment-config']

        with TempDir(chdr=True) as tmp_dir:
            if model_uri:
                model_name, model_version = handle_model_uri(model_uri, name)
                try:
                    aml_model = AzureModel(self.workspace, id='{}:{}'.format(model_name, model_version))
                except Exception as e:
                    raise MlflowException('Failed to retrieve model to deploy') from e
                models = [aml_model]

                model_conf = load_model_environent(tmp_dir, model_name, model_version, name)
                inference_config = create_inference_config(tmp_dir, **model_conf)

            try:
                submit_update_call(service, models, inference_config, deploy_config, aks_endpoint_version_config)

                if config and config.get('async'):
                    _logger.info('AzureML deployment in progress, you can use get_deployment to check on the current '
                                 'deployment status.')
                else:
                    service.wait_for_deployment(show_output=True)
            except Exception as e:
                raise MlflowException('Error submitting deployment update') from e

    def _v2_deployment_update(self, name, endpoint_name, model_uri=None, flavor=None, config=None):
        base_uri = '{arm_base}/subscriptions/{subscription_id}/resourceGroups/{resource_group}/' \
                   'providers/Microsoft.MachineLearningServices/workspaces/' \
                   '{workspace_name}'.format(arm_base=get_base_arm_request_route(self.workspace),
                                             subscription_id=self.workspace.subscription_id,
                                             resource_group=self.workspace.resource_group,
                                             workspace_name=self.workspace.name)
        endpoint_request_uri = base_uri + '/onlineEndpoints/{endpoint_name}'.format(endpoint_name=endpoint_name)
        deployment_request_uri = endpoint_request_uri + '/deployments/{deployment_name}'.format(deployment_name=name)
        deployment_request_headers = {'Content-Type': 'application/json'}
        deployment_request_headers.update(self.workspace._auth_object.get_authentication_header())
        deployment_request_params = {'api-version': self.v2_api_version}

        try:
            resp = submit_rest_request(get_requests_session().get, deployment_request_uri, None,
                                       deployment_request_params, deployment_request_headers)
        except MlflowException as e:
            raise MlflowException('Failure retrieving the deployment to update') from e

        existing_deployment = resp.json()

        v2_deploy_config = {}
        if model_uri:
            model_name, model_version = handle_model_uri(model_uri, name)
        else:
            model_parts_list = existing_deployment['properties']['model'].split('/')
            model_name = model_parts_list[-3]
            model_version = model_parts_list[-1]

        if config and 'deploy-config-file' in config:
            with open(config['deploy-config-file'], 'r') as deploy_file_stream:
                deploy_config_obj = file_stream_to_object(deploy_file_stream)
                if 'code_configuration' in deploy_config_obj or 'environment' in deploy_config_obj or \
                        'endpoint_name' in deploy_config_obj:
                    raise MlflowException('code_configuration, environment, and endpoint_name are not used with '
                                          'MLFlow deployments. Please remove from the deployment config and '
                                          'try again.')
                v2_deploy_config = deploy_config_obj

        deployment_request_body = {
            "location": self.workspace.location,
            "properties": convert_v2_deploy_config_to_rest_config(self.workspace, model_name, model_version,
                                                                  v2_deploy_config, existing_deployment),
            "sku": {
                "name": "default",
                "capacity": 1
            }
        }

        _logger.info('Starting update request')
        resp = submit_rest_request(get_requests_session().put, deployment_request_uri, deployment_request_body,
                                   deployment_request_params, deployment_request_headers)
        get_and_poll_on_async_op(resp, self.workspace, 'Deployment Update')

    @experimental
    def delete_deployment(self, name, endpoint=None, **kwargs):
        """
        Delete the deployment with name ``name``.

        :param name: Name of deployment to delete
        :param endpoint: (optional) Endpoint containing the deployment to delete.
        :return: None
        """
        if endpoint:
            endpoint_obj = self.get_endpoint(endpoint)
            endpoint_name = endpoint
        else:
            endpoint_obj = self.get_endpoint(name)
            endpoint_name = name

        if endpoint_obj:
            # Need to remove any traffic for deployment to be deleted, in the implicit case
            if not endpoint:
                traffic = endpoint_obj['properties']['traffic']
                if name in traffic:
                    del(traffic[name])

                traffic_update_config_file_path = tempfile.mkstemp(suffix='.json')[1]
                traffic_update_config = {
                    "traffic": traffic
                }
                with open(traffic_update_config_file_path, 'w') as traffic_update_config_file:
                    json.dump(traffic_update_config, traffic_update_config_file)
                test_config = {'endpoint-config-file': traffic_update_config_file_path}
                self.update_endpoint(endpoint_name, test_config)

            base_uri = '{arm_base}/subscriptions/{subscription_id}/resourceGroups/' \
                       '{resource_group}/providers/Microsoft.MachineLearningServices/workspaces/' \
                       '{workspace_name}'.format(arm_base=get_base_arm_request_route(self.workspace),
                                                 subscription_id=self.workspace.subscription_id,
                                                 resource_group=self.workspace.resource_group,
                                                 workspace_name=self.workspace.name)
            endpoint_uri = base_uri + '/onlineEndpoints/{endpoint_name}'.format(endpoint_name=endpoint_name)
            deployment_request_uri = endpoint_uri + '/deployments/{deployment_name}'.format(deployment_name=name)
            endpoint_request_headers = {'Content-Type': 'application/json'}
            endpoint_request_headers.update(self.workspace._auth_object.get_authentication_header())
            endpoint_request_params = {'api-version': self.v2_api_version}

            resp = submit_rest_request(get_requests_session().delete, deployment_request_uri, None,
                                       endpoint_request_params, endpoint_request_headers)
            get_and_poll_on_async_op(resp, self.workspace, 'Deployment Delete')

            if 'delete_empty_endpoint' in kwargs and kwargs['delete_empty_endpoint'] is True:
                self.delete_endpoint(endpoint_name)
        else:
            service = self._get_v1_service(name)
            if service:
                try:
                    service.delete()
                except WebserviceException as e:
                    raise MlflowException('There was an error deleting the deployment: \n{}'.format(e.message)) from e
            else:
                _logger.warning('No deployment with name {} found to delete'.format(name))

    @experimental
    def list_deployments(self, endpoint=None):
        """
        List deployments.

        If no endpoint is provided, will list all deployments. If an endpoint is provided,
        will list all deployments under that endpoint.

        :param endpoint: (optional) List deployments in the specified endpoint.
        :return: A list of dicts corresponding to deployments.
        """
        try:
            if endpoint:
                _logger.info('Retrieving all deployments under endpoint {}'.format(endpoint))
                base_uri = '{arm_base}/subscriptions/{subscription_id}/resourceGroups/' \
                           '{resource_group}/providers/Microsoft.MachineLearningServices/workspaces/' \
                           '{workspace_name}'.format(arm_base=get_base_arm_request_route(self.workspace),
                                                     subscription_id=self.workspace.subscription_id,
                                                     resource_group=self.workspace.resource_group,
                                                     workspace_name=self.workspace.name)
                endpoint_uri = base_uri + '/onlineEndpoints/{endpoint_name}'.format(endpoint_name=endpoint)
                deployment_list_uri = endpoint_uri + '/deployments'
                endpoint_request_headers = {'Content-Type': 'application/json'}
                endpoint_request_headers.update(self.workspace._auth_object.get_authentication_header())
                endpoint_request_params = {'api-version': self.v2_api_version}

                resp = submit_rest_request(get_requests_session().get, deployment_list_uri, None,
                                           endpoint_request_params, endpoint_request_headers)
                v2_list_response = resp.json()
                if 'value' in v2_list_response:
                    endpoint_list = v2_list_response['value']
                else:
                    endpoint_list = v2_list_response

                return endpoint_list
            else:
                _logger.info('Retrieving all ACI/AKS deployments')
                service_list = []
                services = Webservice.list(self.workspace, compute_type='ACI')
                services += Webservice.list(self.workspace, compute_type='AKS')
                for service in services:
                    service_list.append(service.serialize())

                endpoints = self.list_endpoints()
                for endpoint in endpoints:
                    deployments = self.list_deployments(endpoint['name'])
                    for deployment in deployments:
                        deployment['endpointName'] = endpoint['name']
                        deployment['scoringUri'] = endpoint['properties']['scoringUri']
                        deployment['swaggerUri'] = endpoint['properties']['swaggerUri']
                    service_list += deployments

                return service_list
        except WebserviceException as e:
            raise MlflowException('There was an error listing deployments: \n{}'.format(e.message)) from e

    @experimental
    def get_deployment(self, name, endpoint=None):
        """
        Retrieve details for the specified deployment.

        Returns a dictionary describing the specified deployment. The dict is guaranteed to contain an 'name' key
        containing the deployment name.

        :param name: Name of deployment to retrieve
        :param endpoint: (optional) Endpoint containing the deployment to get
        """
        endpoint_name = name
        if endpoint:
            endpoint_name = endpoint

        deployment = self._get_v2_deployment(name, endpoint_name)

        if not deployment:
            service = self._get_v1_service(name)
            if service:
                deployment = service.serialize()

        if not deployment:
            raise MlflowException('No deployment with name {} found'.format(name))

        if 'flavor' not in deployment:
            deployment['flavor'] = 'python_function'

        return deployment

    def _get_v1_service(self, name):
        try:
            service = Webservice(self.workspace, name)
            return service
        except WebserviceException as e:
            if 'WebserviceNotFound' in e.message:
                return None
            raise MlflowException('There was an error retrieving the deployment: \n{}'.format(e.message)) from e

    def _get_v2_deployment(self, name, endpoint_name):
        base_uri = '{arm_base}/subscriptions/{subscription_id}/resourceGroups/{resource_group}/' \
                   'providers/Microsoft.MachineLearningServices/workspaces/' \
                   '{workspace_name}'.format(arm_base=get_base_arm_request_route(self.workspace),
                                             subscription_id=self.workspace.subscription_id,
                                             resource_group=self.workspace.resource_group,
                                             workspace_name=self.workspace.name)
        deployment_request_uri = base_uri + '/onlineEndpoints/{endpoint_name}' \
                                            '/deployments/{deployment_name}'.format(endpoint_name=endpoint_name,
                                                                                    deployment_name=name)
        deployment_request_headers = {'Content-Type': 'application/json'}
        deployment_request_headers.update(self.workspace._auth_object.get_authentication_header())
        deployment_request_params = {'api-version': self.v2_api_version}

        try:
            resp = submit_rest_request(get_requests_session().get, deployment_request_uri, None,
                                       deployment_request_params, deployment_request_headers)
        except MlflowException as e:
            if 'Response Code: 404' in e.message:
                return None
            else:
                raise e

        return resp.json()

    @experimental
    def predict(self, deployment_name=None, df=None, endpoint=None):
        """
        Predict on the specified deployment using the provided dataframe.

        Compute predictions on the ``df`` using the specified deployment.
        Note that the input/output types of this method matches that of `mlflow pyfunc predict`
        (we accept a pandas.DataFrame, numpy.ndarray, or Dict[str, numpy.ndarray] as input and return
        either a pandas.DataFrame, pandas.Series, or numpy.ndarray as output).

        :param deployment_name: Name of deployment to predict against
        :param df: pandas.DataFrame, numpy.ndarray, or Dict[str, numpy.ndarray] to use for inference
        :param endpoint: Endpoint to predict against
        :return: A pandas.DataFrame, pandas.Series, or numpy.ndarray
        """
        try:
            from mlflow.pyfunc.scoring_server import parse_json_input, _get_jsonable_obj
            import numpy as np
        except ImportError as exception:
            raise get_deployments_import_error(exception)

        if not deployment_name and not endpoint:
            raise MlflowException('Error, must provide one of deployment_name or endpoint')

        # Take in DF, parse to json using split orient
        if isinstance(df, dict):
            input_data = {key: _get_jsonable_obj(value, pandas_orient='split') for key, value in df.items()}
        else:
            input_data = _get_jsonable_obj(df, pandas_orient='split')

        if endpoint:
            endpoint_obj = self.get_endpoint(endpoint)
            if deployment_name:
                # Predict against a specific deployment in an endpoint
                _logger.info('Issuing prediction against deployment {} in endpoint '
                             '{}'.format(deployment_name, endpoint))
                scoring_resp, output_format = self._v2_predict(endpoint_obj, input_data, deployment_name)
            else:
                # Predict against endpoint and rely on traffic management
                _logger.info('Issuing prediction against endpoint {}'.format(endpoint))
                scoring_resp, output_format = self._v2_predict(endpoint_obj, input_data)
        else:
            # Try to get implicitly created endpoint
            endpoint_obj = self.get_endpoint(deployment_name)
            if endpoint_obj:
                # Predict against implicitly created endpoint and rely on traffic management
                _logger.info('Issuing prediction against endpoint {}'.format(deployment_name))
                scoring_resp, output_format = self._v2_predict(endpoint_obj, input_data)
            else:
                service = self._get_v1_service(deployment_name)
                if service:
                    # Predict against v1 webservice
                    _logger.info('Issuing prediction against deployment {}'.format(service.name))
                    scoring_resp, output_format = self._v1_predict(service, input_data)
                else:
                    raise MlflowException('No deployment with name {} '
                                          'found to predict against'.format(deployment_name))

        if scoring_resp.status_code == 200:
            if output_format == NUMPY_SWAGGER_FORMAT:
                return np.array(scoring_resp.json())
            return parse_json_input(json.dumps(scoring_resp.json()), orient='records')
        else:
            raise MlflowException('Failure during prediction:\n'
                                  'Response Code: {}\n'
                                  'Headers: {}\n'
                                  'Content: {}'.format(scoring_resp.status_code, scoring_resp.headers,
                                                       scoring_resp.content))

    def _v1_predict(self, service, input_data):
        if not service.scoring_uri:
            raise MlflowException('Error attempting to call deployment, scoring_uri unavailable. '
                                  'This could be due to a failed deployment, or the service is not ready yet.\n'
                                  'Current State: {}\n'
                                  'Errors: {}'.format(service.state, service.error))

        # Pass split orient json to webservice
        # Take records orient json from webservice
        resp = ClientBase._execute_func(service._webservice_session.post, service.scoring_uri,
                                        data=json.dumps({'input_data': input_data}))
        swagger_params = {"version": 3}
        swagger_resp = ClientBase._execute_func(service._webservice_session.get, service.swagger_uri,
                                                params=swagger_params)
        output_format = None
        if swagger_resp.status_code != 200:
            _logger.warning(
                f'Unable to fetch swagger for deployment {service.name}. Proceeding with default output handling.'
            )
        else:
            swagger = swagger_resp.json()
            output_format = swagger.get("components", {}) \
                                   .get("schemas", {}) \
                                   .get("ServiceOutput", {}) \
                                   .get("format", None)

        if resp.status_code == 401:
            if service.auth_enabled:
                service_keys = service.get_keys()
                service._session.headers.update({'Authorization': 'Bearer ' + service_keys[0]})
            elif service.token_auth_enabled:
                service_token, refresh_token_time = service.get_access_token()
                service._refresh_token_time = refresh_token_time
                service._session.headers.update({'Authorization': 'Bearer ' + service_token})
            resp = ClientBase._execute_func(service._webservice_session.post, service.scoring_uri, data=input_data)

        return resp, output_format

    def _v2_predict(self, endpoint_obj, input_data, deployment_name=None):
        base_uri = '{arm_base}/subscriptions/{subscription_id}/resourceGroups/{resource_group}/' \
                   'providers/Microsoft.MachineLearningServices/workspaces/' \
                   '{workspace_name}'.format(arm_base=get_base_arm_request_route(self.workspace),
                                             subscription_id=self.workspace.subscription_id,
                                             resource_group=self.workspace.resource_group,
                                             workspace_name=self.workspace.name)
        if endpoint_obj['properties']['authMode'] == 'Key':
            endpoint_auth_request_uri = base_uri + '/onlineEndpoints/{endpoint_name}/listKeys'.format(
                endpoint_name=endpoint_obj['name'])
        else:
            endpoint_auth_request_uri = base_uri + '/onlineEndpoints/{endpoint_name}/token'.format(
                endpoint_name=endpoint_obj['name'])
        endpoint_request_headers = {'Content-Type': 'application/json'}
        endpoint_request_headers.update(self.workspace._auth_object.get_authentication_header())
        endpoint_request_params = {'api-version': self.v2_api_version}

        if deployment_name:
            endpoint_request_headers.update({'azureml-model-deployment': deployment_name})

        try:
            endpoint_auth_response = submit_rest_request(get_requests_session().post, endpoint_auth_request_uri, None,
                                                         endpoint_request_params, endpoint_request_headers)
        except MlflowException as e:
            raise MlflowException('Received bad response attempting to retrieve auth token') from e

        scoring_uri = endpoint_obj['properties']['scoringUri']
        if endpoint_obj['properties']['authMode'] == 'Key':
            scoring_request_headers = {'Content-Type': 'application/json',
                                       'Authorization': 'Bearer {}'.format(
                                           endpoint_auth_response.json()['primaryKey'])}
        else:
            scoring_request_headers = {'Content-Type': 'application/json',
                                       'Authorization': 'Bearer {}'.format(
                                           endpoint_auth_response.json()['accessToken'])}
        scoring_resp = submit_rest_request(get_requests_session().post, scoring_uri,
                                           {'input_data': input_data}, None, scoring_request_headers)

        output_format = None
        try:
            swagger_params = {"version": 3}
            swagger_resp = ClientBase._execute_func(get_requests_session().get,
                                                    endpoint_obj["properties"]["swaggerUri"],
                                                    params=swagger_params, headers=scoring_request_headers)
            if swagger_resp.status_code != 200:
                _logger.warning(
                    f'Unable to fetch swagger for deployment {endpoint_obj["name"]}. '
                    f'Proceeding with default output handling.'
                )
            else:
                swagger = swagger_resp.json()
                output_format = swagger.get("components", {}) \
                                       .get("schemas", {}) \
                                       .get("ServiceOutput", {}) \
                                       .get("format", None)
        except Exception as e:
            _logger.warning(
                f'Exception received while attempting to fetch swagger for deployment {endpoint_obj["name"]}. '
                f'Proceeding with prediction request, but this may result in a failure to parse the received output.\n'
                f'Exception was {e}'
            )

        return scoring_resp, output_format

    def _get_logs(self, deployment_name=None, endpoint=None, get_init_container_logs=False):
        if not deployment_name and not endpoint:
            raise MlflowException('Error, must provide one of deployment_name or endpoint')

        if endpoint:
            endpoint_name = endpoint
        else:
            endpoint = self.get_endpoint(deployment_name)
            endpoint_name = deployment_name

        if endpoint:
            base_uri = '{arm_base}/subscriptions/{subscription_id}/resourceGroups/' \
                       '{resource_group}/providers/Microsoft.MachineLearningServices/workspaces/' \
                       '{workspace_name}'.format(arm_base=get_base_arm_request_route(self.workspace),
                                                 subscription_id=self.workspace.subscription_id,
                                                 resource_group=self.workspace.resource_group,
                                                 workspace_name=self.workspace.name)
            deployment_request_uri = base_uri + '/onlineEndpoints/{endpoint_name}'.format(endpoint_name=endpoint_name)
            if deployment_name:
                deployment_request_uri = \
                    deployment_request_uri + '/deployments/{deployment_name}'.format(deployment_name=deployment_name)
            deployment_request_uri = deployment_request_uri + '/getLogs'

            deployment_request_headers = {'Content-Type': 'application/json'}
            deployment_request_headers.update(self.workspace._auth_object.get_authentication_header())
            deployment_request_params = {'api-version': self.v2_api_version}

            logs_body = {}
            if get_init_container_logs:
                logs_body = {"containerType": "storageInitializer"}

            resp = submit_rest_request(get_requests_session().post, deployment_request_uri, logs_body,
                                       deployment_request_params, deployment_request_headers)
            content = json.loads(resp.content)
            return content
        else:
            service = self._get_v1_service(deployment_name)
            if service:
                return service.get_logs(init=get_init_container_logs)
            else:
                raise MlflowException('No deployment with name {} found to get logs for'.format(deployment_name))

    @experimental
    def create_endpoint(self, name, config=None):
        """
        Create an endpoint with the specified target.

        By default, this method should block until creation completes (i.e. until it's possible
        to create a deployment within the endpoint). In the case of conflicts (e.g. if it's not
        possible to create the specified endpoint due to conflict with an existing endpoint),
        raises a :py:class:`mlflow.exceptions.MlflowException`. See target-specific plugin
        documentation for additional detail on support for asynchronous creation and other
        configuration.

        :param name: Unique name to use for endpoint. If another endpoint exists with the same
                     name, raises a :py:class:`mlflow.exceptions.MlflowException`.
        :param config: (optional) Dict containing target-specific configuration for the
                       endpoint.
        :return: Dict corresponding to created endpoint, which must contain the 'name' key.
        """
        endpoint_config_obj = {}
        run_async = False
        if config:
            if 'endpoint-config-file' in config:
                with open(config['endpoint-config-file'], 'r') as deploy_file_stream:
                    endpoint_config_obj = file_stream_to_object(deploy_file_stream)
            if 'async' in config:
                run_async = config['async']

        self._create_endpoint(name, endpoint_config_obj, run_async)

        return self.get_endpoint(name)

    def _create_endpoint(self, name, config, run_async=False):
        base_uri = '{arm_base}/subscriptions/{subscription_id}/resourceGroups/' \
                   '{resource_group}/providers/Microsoft.MachineLearningServices/workspaces/' \
                   '{workspace_name}'.format(arm_base=get_base_arm_request_route(self.workspace),
                                             subscription_id=self.workspace.subscription_id,
                                             resource_group=self.workspace.resource_group,
                                             workspace_name=self.workspace.name)
        endpoint_request_uri = base_uri + '/onlineEndpoints/{endpoint_name}'.format(endpoint_name=name)
        endpoint_request_headers = {'Content-Type': 'application/json'}
        endpoint_request_headers.update(self.workspace._auth_object.get_authentication_header())
        endpoint_request_params = {'api-version': self.v2_api_version}

        endpoint_request_body = self._build_endpoint_request_body(config)

        _logger.info('Starting endpoint create request')
        resp = submit_rest_request(get_requests_session().put, endpoint_request_uri, endpoint_request_body,
                                   endpoint_request_params, endpoint_request_headers)

        if not run_async:
            get_and_poll_on_async_op(resp, self.workspace, 'Endpoint Create')

    @experimental
    def update_endpoint(self, endpoint, config=None):
        """
        Update the endpoint with the specified name.

        You can update any target-specific attributes of the endpoint (via `config`). By default,
        this method should block until the update completes (i.e. until it's possible to create a
        deployment within the endpoint). See target-specific plugin documentation for additional
        detail on support for asynchronous update and other configuration.

        :param endpoint: Unique name of endpoint to update
        :param config: (optional) dict containing target-specific configuration for the
                       endpoint
        :return: None
        """
        endpoint_obj = self.get_endpoint(endpoint)

        if not endpoint_obj:
            raise MlflowException('No endpoint with name {} found to update'.format(endpoint))

        endpoint_config_obj = {}
        run_async = False
        if config:
            if 'endpoint-config-file' in config:
                with open(config['endpoint-config-file'], 'r') as deploy_file_stream:
                    endpoint_config_obj = file_stream_to_object(deploy_file_stream)
            if 'async' in config:
                run_async = config['async']

        self._update_endpoint(endpoint, endpoint_config_obj, run_async)

        return self.get_endpoint(endpoint)

    def _update_endpoint(self, name, config, run_async=False):
        base_uri = '{arm_base}/subscriptions/{subscription_id}/resourceGroups/' \
                   '{resource_group}/providers/Microsoft.MachineLearningServices/workspaces/' \
                   '{workspace_name}'.format(arm_base=get_base_arm_request_route(self.workspace),
                                             subscription_id=self.workspace.subscription_id,
                                             resource_group=self.workspace.resource_group,
                                             workspace_name=self.workspace.name)
        endpoint_request_uri = base_uri + '/onlineEndpoints/{endpoint_name}'.format(endpoint_name=name)
        update_endpoint_request_headers = {'Content-Type': 'application/json'}
        update_endpoint_request_headers.update(self.workspace._auth_object.get_authentication_header())
        update_endpoint_request_params = {'api-version': self.v2_api_version}

        update_endpoint_request_body = self._build_endpoint_request_body(config, update=True)

        _logger.info('Starting endpoint update request')
        resp = submit_rest_request(get_requests_session().patch, endpoint_request_uri,
                                   update_endpoint_request_body, update_endpoint_request_params,
                                   update_endpoint_request_headers)

        if not run_async:
            get_and_poll_on_async_op(resp, self.workspace, 'Endpoint Update')

    def _build_endpoint_request_body(self, config, update=False):
        endpoint_request_body = {"properties": {}}

        if 'identity' in config:
            endpoint_request_body['identity'] = config['identity']
        elif not update:
            endpoint_request_body['identity'] = {"type": "systemAssigned"}

        if 'location' in config:
            endpoint_request_body['location'] = config['location']
        elif not update:
            endpoint_request_body['location'] = self.workspace.location

        if 'tags' in config:
            endpoint_request_body['tags'] = config['tags']

        auth_mode_switch = {
            'aml_token': "AMLToken",
            'aad_token': "AADToken",
            'key': 'Key'
        }

        if 'auth_mode' in config:
            endpoint_request_body['properties']['authMode'] = \
                auth_mode_switch.get(config['auth_mode'], config['auth_mode'])
        elif not update:
            endpoint_request_body['properties']['authMode'] = 'Key'

        if 'description' in config:
            endpoint_request_body['properties']['description'] = config['description']
        if 'traffic' in config:
            endpoint_request_body['properties']['traffic'] = config['traffic']
        if 'mirror_traffic' in config:
            endpoint_request_body['properties']['mirrorTraffic'] = config['mirror_traffic']
        if 'properties' in config:
            endpoint_request_body['properties']['properties'] = config['properties']
        elif not update:
            endpoint_request_body['properties']['properties'] = {}

        if not update:
            endpoint_request_body['properties']['properties']['azureml.mlflow_client_endpoint'] = 'True'

        return endpoint_request_body

    @experimental
    def delete_endpoint(self, endpoint):
        """
        Delete the endpoint from the specified target.

        Deletion should be idempotent (i.e. deletion should not fail if retried on a non-existent
        deployment).

        :param endpoint: Name of endpoint to delete
        :return: None
        """
        endpoint_obj = self.get_endpoint(endpoint)

        if endpoint_obj:
            base_uri = '{arm_base}/subscriptions/{subscription_id}/resourceGroups/' \
                       '{resource_group}/providers/Microsoft.MachineLearningServices/workspaces/' \
                       '{workspace_name}'.format(arm_base=get_base_arm_request_route(self.workspace),
                                                 subscription_id=self.workspace.subscription_id,
                                                 resource_group=self.workspace.resource_group,
                                                 workspace_name=self.workspace.name)
            endpoint_request_uri = base_uri + '/onlineEndpoints/{endpoint_name}'.format(endpoint_name=endpoint)
            endpoint_request_headers = {'Content-Type': 'application/json'}
            endpoint_request_headers.update(self.workspace._auth_object.get_authentication_header())
            endpoint_request_params = {'api-version': self.v2_api_version}

            _logger.info('Starting endpoint delete request')
            resp = submit_rest_request(get_requests_session().delete, endpoint_request_uri, None,
                                       endpoint_request_params, endpoint_request_headers)
            get_and_poll_on_async_op(resp, self.workspace, 'Endpoint Delete')
        else:
            _logger.info('No endpoint with name {} found to delete'.format(endpoint))

    @experimental
    def list_endpoints(self):
        """
        List endpoints in the specified target.

        This method is expected to return an unpaginated list of all endpoints (an alternative
        would be to return a dict with an 'endpoints' field containing the actual endpoints,
        with plugins able to specify other fields, e.g. a next_page_token field, in the
        returned dictionary for pagination, and to accept a `pagination_args` argument to this
        method for passing pagination-related args).

        :return: A list of dicts corresponding to endpoints. Each dict is guaranteed to
                 contain a 'name' key containing the endpoint name. The other fields of
                 the returned dictionary and their types may vary across targets.
        """
        base_uri = '{arm_base}/subscriptions/{subscription_id}/resourceGroups/' \
                   '{resource_group}/providers/Microsoft.MachineLearningServices/workspaces/' \
                   '{workspace_name}'.format(arm_base=get_base_arm_request_route(self.workspace),
                                             subscription_id=self.workspace.subscription_id,
                                             resource_group=self.workspace.resource_group,
                                             workspace_name=self.workspace.name)
        endpoint_list_request_uri = base_uri + '/onlineEndpoints'
        endpoint_request_headers = {'Content-Type': 'application/json'}
        endpoint_request_headers.update(self.workspace._auth_object.get_authentication_header())
        endpoint_request_params = {'api-version': self.v2_api_version}

        _logger.info('Starting endpoint list request')
        resp = submit_rest_request(get_requests_session().get, endpoint_list_request_uri, None,
                                   endpoint_request_params, endpoint_request_headers)
        v2_list_response = resp.json()

        if 'value' in v2_list_response:
            endpoint_list = v2_list_response['value']
        else:
            endpoint_list = v2_list_response

        return endpoint_list

    @experimental
    def get_endpoint(self, endpoint):
        """
        Retrieve the details of the specified endpoint.

        Returns a dictionary describing the specified endpoint, throwing a
        py:class:`mlflow.exception.MlflowException` if no endpoint exists with the provided
        name.
        The dict is guaranteed to contain an 'name' key containing the endpoint name.
        The other fields of the returned dictionary and their types may vary across targets.

        :param endpoint: Name of endpoint to fetch
        :return: A dict corresponding to the retrieved endpoint. The dict is guaranteed to
                 contain a 'name' key corresponding to the endpoint name. The other fields of
                 the returned dictionary and their types may vary across targets.
        """
        base_uri = '{arm_base}/subscriptions/{subscription_id}/resourceGroups/{resource_group}/' \
                   'providers/Microsoft.MachineLearningServices/workspaces/' \
                   '{workspace_name}'.format(arm_base=get_base_arm_request_route(self.workspace),
                                             subscription_id=self.workspace.subscription_id,
                                             resource_group=self.workspace.resource_group,
                                             workspace_name=self.workspace.name)
        endpoint_request_uri = base_uri + '/onlineEndpoints/{endpoint_name}'.format(endpoint_name=endpoint)
        endpoint_request_headers = {'Content-Type': 'application/json'}
        endpoint_request_headers.update(self.workspace._auth_object.get_authentication_header())
        endpoint_request_params = {'api-version': self.v2_api_version}

        try:
            _logger.info('Starting endpoint get request')
            resp = submit_rest_request(get_requests_session().get, endpoint_request_uri, None, endpoint_request_params,
                                       endpoint_request_headers)
        except MlflowException as e:
            if 'Response Code: 404' in e.message:
                return None
            else:
                raise e

        endpoint_json = resp.json()

        return endpoint_json
