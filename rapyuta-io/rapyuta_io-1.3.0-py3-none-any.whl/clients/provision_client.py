# encoding: utf-8
from __future__ import absolute_import
from rapyuta_io.clients.api_client import CatalogConfig
from rapyuta_io.utils import ResourceNotFoundError, ServiceBindingError
from rapyuta_io.utils.rest_client import RestClient, HttpMethod
from rapyuta_io.utils.settings import *
from rapyuta_io.utils.utils import response_validator
from six.moves import map


class ProvisionClient(CatalogConfig):
    def __init__(self, catalog_api_host, auth_token, project):
        CatalogConfig.__init__(self, catalog_api_host, auth_token, project)
        self._api_path = PROVISION_API_PATH

    def _get_api_path(self):
        return self._catalog_api_host + self._api_path

    def _execute_api(self, url, method, payload=None, query_params=None, retry_limit=0):
        response = RestClient(url).method(method).headers(self._headers) \
            .retry(retry_limit).query_param(query_params).execute(payload=payload)
        return response

    @response_validator(True)
    def provision(self, payload, retry_limit):
        url = self._get_api_path() + "/" + payload['instance_id']
        response = self._execute_api(url, HttpMethod.PUT, payload, retry_limit=retry_limit)
        return response

    @response_validator(return_value=True)
    def deprovision(self, deployment_id, plan_id, service_id, retry_limit):
        path = '{}?plan_id={}&service_id={}&accepts_incomplete=false' \
            .format(deployment_id, plan_id, service_id)
        url = self._get_api_path() + "/" + path
        response = self._execute_api(url, HttpMethod.DELETE, retry_limit=retry_limit)
        return response

    @response_validator(True, errors={404: ServiceBindingError})
    def service_binding(self, deployment_id, plan_id, service_id, binding_id, retry_limit):
        payload = dict(service_id=service_id, plan_id=plan_id)
        path = '/{}/service_bindings/{}'.format(deployment_id, binding_id)
        url = self._get_api_path() + path
        return self._execute_api(url, HttpMethod.PUT, payload, retry_limit=retry_limit)

    @response_validator(errors={404: ResourceNotFoundError}, return_value=True)
    def service_unbinding(self, deployment_id, plan_id, service_id, binding_id, retry_limit):
        path = '/{}/service_bindings/{}?service_id={}&plan_id={}'.format(deployment_id, binding_id,
                                                                         service_id, plan_id)
        url = self._get_api_path() + path
        response = self._execute_api(url, HttpMethod.DELETE, retry_limit=retry_limit)
        return response

    @response_validator(True)
    def deployments(self, service_id, phases, retry_limit):
        query_params = {'package_uid': service_id}
        if phases:
            query_params['phase'] = list(map(str, phases))
        path = '/deployment/list'
        url = self._catalog_api_host + path
        return self._execute_api(url, HttpMethod.GET, retry_limit=retry_limit, query_params=query_params)

    @response_validator(True)
    def deployment_status(self, deployment_id, retry_limit):
        path = '/serviceinstance/{}'.format(deployment_id)
        url = self._catalog_api_host + path
        return self._execute_api(url, HttpMethod.GET, retry_limit=retry_limit)

    @response_validator(True)
    def create_disk(self, payload, retry_limit):
        path = '/disk'
        url = self._catalog_api_host + path
        return self._execute_api(url, HttpMethod.POST, payload=payload, retry_limit=retry_limit)

    @response_validator(True)
    def get_disk(self, disk_guid, retry_limit):
        path = '/disk/{}'.format(disk_guid)
        url = self._catalog_api_host + path
        return self._execute_api(url, HttpMethod.GET, retry_limit=retry_limit)

    @response_validator(True)
    def list_disk(self, deploymentGUIDs=None, retry_limit=0):
        path = '/disk'
        query_params = {}
        if deploymentGUIDs:
            query_params['deployment_guid'] = deploymentGUIDs
        url = self._catalog_api_host + path
        return self._execute_api(url, HttpMethod.GET, query_params=query_params, retry_limit=retry_limit)

    @response_validator(True)
    def delete_disk(self, disk_guid, retry_limit):
        path = '/disk/{}'.format(disk_guid)
        url = self._catalog_api_host + path
        return self._execute_api(url, HttpMethod.DELETE, retry_limit=retry_limit)