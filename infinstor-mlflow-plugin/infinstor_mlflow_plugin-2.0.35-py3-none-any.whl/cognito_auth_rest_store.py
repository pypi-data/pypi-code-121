import builtins
import os
from typing import Any, Dict, List
import mlflow.store.tracking.rest_store
from mlflow.utils.rest_utils import MlflowHostCreds
from .tokenfile import get_token
from . import tokenfile, set_builtins_with_serverside_config
from os.path import expanduser
from os.path import sep as separator
import ast
import logging
import traceback
from mlflow.entities import (
        ViewType
        )
import requests
from requests.exceptions import HTTPError
import json
from mlflow.entities.model_registry.model_version_stages import (
    get_canonical_stage,
    DEFAULT_STAGES_FOR_GET_LATEST_VERSIONS,
    ALL_STAGES,
    STAGE_DELETED_INTERNAL,
    STAGE_ARCHIVED,
)
from mlflow.entities.model_registry.registered_model import ModelVersion, RegisteredModel
from mlflow.store.entities.paged_list import PagedList
from . import login

from mlflow.utils.proto_json_utils import message_to_json
from mlflow.entities import Experiment, ExperimentTag
from mlflow.protos.service_pb2 import (
    CreateExperiment,
    ListExperiments )

from . import get_log_level_from_config_json

logger:logging.Logger = logging.getLogger(__name__)
loglevel_int:int = get_log_level_from_config_json(__name__)
if loglevel_int:
    logger.setLevel(loglevel_int)
class CognitoModelVersion():
    def __init__(self, name, user_id, version, creation_timestamp, last_updated_timestamp,
            current_stage, source, run_id, status):
        self.name = name
        self.user_id = user_id
        self.version = version
        self.creation_timestamp = creation_timestamp
        self.last_updated_timestamp = last_updated_timestamp
        self.current_stage = current_stage
        self.source = source
        self.run_id = status

class TagWithProperties():
    key = None
    value = None
    def __init__(self, k, v):
        self.key = k
        self.value = v

ENABLE_PROJECTS = "ENABLE_PROJECTS"
class CognitoAuthenticatedRestStore(mlflow.store.tracking.rest_store.RestStore):
    """
    instance variables:
    
    'srvc': a dictionary which contains the details of the service.  See login.bootstrap_from_mlflow_rest() or /api/2.0/mlflow/infinstor/get_version() for details

    """
    def cognito_host_creds(self):
        tokfile = tokenfile.get_token_file_name()
        if (self.srvc):
            token, service = get_token(self.srvc['region'], tokfile, False)
            return MlflowHostCreds('https://' + self.srvc['mlflowserver'] + ':443/', token=token)
        else:
            token, service = get_token('us-east-1', tokfile, False)
            return MlflowHostCreds('https://mlflow.' + service + ':443/', token=token)

    def get_service(self):
        if (self.srvc):
            return self.srvc['mlflowserver']
        tokfile = tokenfile.get_token_file_name()
        token, service = get_token(self.srvc['region'], tokfile, False)
        return 'mlflow.' + service

    def get_token_string(self):
        """ get the access token """
        tokfile = tokenfile.get_token_file_name()
        token, service = get_token(self.srvc['region'], tokfile, False)
        return token

    def get_id_token_string(self):
        id_token, service = tokenfile.get_id_token(self.srvc['region'])
        return id_token
        
    def get_headers(self):
        headers = {'Content-Type': 'application/x-amz-json-1.1'}
        if (self.get_token_string().startswith('Custom')):
            headers['Authorization'] = self.get_token_string()
        else:
            headers['Authorization'] = 'Bearer ' + self.get_token_string()
        return headers

    def _hard_delete_run(self, run_id):
        """
        Permanently delete a run (metadata and metrics, tags, parameters).
        This is used by the ``mlflow gc`` command line and is not intended to be used elsewhere.
        """
        print('_hard_delete_run: Entered. run_id=' + str(run_id))
        run = self.get_run(run_id)
        if (not run):
            print('_hard_delete_run: Error. could not find run ' + str(run_id))
            return
        runs = self.search_runs(experiment_ids=[run.info.experiment_id],
                filter_string="tags.mlflow.parentRunId = \""+run_id + "\"",
                run_view_type=ViewType.ALL)
        if (len(runs) > 0):
            print('_hard_delete_run: This run has child runs. Delete child runs first')
            print('_hard_delete_run: Here are the commands to delete the child runs:')
            for chrun in runs:
                print('  mlflow gc --backend-store-uri infinstor:/// --run-ids '
                        + str(chrun.info.run_id))
            return

        headers = self.get_headers()
        url = 'https://' + self.get_service() + '/api/2.0/mlflow/runs/hard-delete'

        body = dict()
        body['run_id'] = run_id

        try:
            response = requests.post(url, data=json.dumps(body), headers=headers)
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            raise
        except Exception as err:
            print(f'Other error occurred: {err}')
            raise
        else:
            return

    def _get_deleted_runs(self):
        print('_get_deleted_runs: Entered')
        experiments = self.list_experiments(view_type=ViewType.ALL)
        experiment_ids = map(lambda x: x.experiment_id, experiments)
        deleted_runs = self.search_runs(
            experiment_ids=experiment_ids, filter_string="", run_view_type=ViewType.DELETED_ONLY
        )
        rv = [deleted_run.info.run_uuid for deleted_run in deleted_runs]
        print('_get_deleted_runs: runs marked as deleted=' + str(rv))
        return rv

    def get_latest_versions(self, name, stages=None):
        """
        Latest version models for each requested stage. If no ``stages`` argument is provided,
        returns the latest version for each stage.

        :param name: Registered model name.
        :param stages: List of desired stages. If input list is None, return latest versions for
                       for 'Staging' and 'Production' stages.
        :return: List of :py:class:`mlflow.entities.model_registry.ModelVersion` objects.
        """
        #print('get_latest_versions: Entered. name=' + str(name) + ', stages=' + str(stages),
        #        flush=True)
        headers = self.get_headers()
        url = 'https://' + self.get_service() + '/api/2.0/mlflow/registered-models/get'

        try:
            response = requests.get(url, params={'name':name}, headers=headers)
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            raise
        except Exception as err:
            print(f'Other error occurred: {err}')
            raise
        respjson = json.loads(response.text)
        model = respjson['registered_model']
        staging = None
        production = None
        archived = None
        none_version = None
        if ('latest_versions' in model):
            for lv in model['latest_versions']:
                if (lv['current_stage'] == 'Staging'):
                    if (not staging):
                        staging = lv
                    elif (int(lv['version']) > int(staging['version'])):
                        staging = lv
                elif (lv['current_stage'] == 'Production'):
                    if (not production):
                        production = lv
                    elif (int(lv['version']) > int(production['version'])):
                        production = lv
                elif (lv['current_stage'] == 'Archived'):
                    if (not archived):
                        archived = lv
                    elif (int(lv['version']) > int(archived['version'])):
                        archived = lv
                elif (lv['current_stage'] == 'None'):
                    if (not none_version):
                        none_version = lv
                    elif (int(lv['version']) > int(none_version['version'])):
                        none_version = lv

        latest_versions = []
        if (staging):
            latest_versions.append(CognitoModelVersion(staging['name'],
                staging['user_id'], staging['version'], staging['creation_timestamp'],
                staging['last_updated_timestamp'], staging['current_stage'],
                staging['source'], staging['run_id'], staging['status']))
        if (production):
            latest_versions.append(CognitoModelVersion(production['name'],
                production['user_id'], production['version'], production['creation_timestamp'],
                production['last_updated_timestamp'], production['current_stage'],
                production['source'], production['run_id'], production['status']))
        if (archived):
            latest_versions.append(CognitoModelVersion(archived['name'],
                archived['user_id'], archived['version'], archived['creation_timestamp'],
                archived['last_updated_timestamp'], archived['current_stage'],
                archived['source'], archived['run_id'], archived['status']))
        if (none_version):
            latest_versions.append(CognitoModelVersion(none_version['name'],
                none_version['user_id'], none_version['version'], none_version['creation_timestamp'],
                none_version['last_updated_timestamp'], none_version['current_stage'],
                none_version['source'], none_version['run_id'], none_version['status']))

        if stages is None or len(stages) == 0 or stages[0] == '':
            expected_stages = set(
                [get_canonical_stage(stage) for stage in ALL_STAGES]
            )
        else:
            expected_stages = set([get_canonical_stage(stage) for stage in stages])
        return [mv for mv in latest_versions if mv.current_stage in expected_stages]

    def get_model_version_download_uri(self, name, version):
        #print('get_model_version_download_uri: Entered. name=' + str(name)
        #        + ', version=' + str(version), flush=True)
        headers = self.get_headers()
        url = 'https://' + self.get_service() + '/api/2.0/mlflow/model-versions/get'

        try:
            response = requests.get(url, params={'name':name, 'version':version}, headers=headers)
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            raise
        except Exception as err:
            print(f'Other error occurred: {err}')
            raise
        respjson = json.loads(response.text)
        model_version = respjson['model_version']
        return model_version['source']

    def _get_dict_for_projectid_tag_in_body_or_api_tags_or_query_param(self, tagIn) :
        """ returns a dict which represents the 'projectid' tag.  Raises an exception if enableProjects is true on the server side and MLFLOW_PROJECT_ID_INFINSTOR is not defined 
        
        Note that calls to mlflow APIs which accept a 'tags' parameter ( like createExperiment() API ) expect 'tags' to be List[ExperimentTag]..  But in the actual REST request, in the http request body, the format for tags is different and is as shown here: [ {'key':'tag1', 'value':'tag1_value'}, ... ]
        
        args: 
        tagIn = 'body' | 'api_tags' | 'query_param'
        Returns:  a dict or an ExperimentTag, which represents the 'tag'..
        """
        retval = { 'key':'projectid', 'value':"projectidnotenabled" } if tagIn == 'body' else ExperimentTag('projectid', 'projectidnotenabled') if tagIn=='api_tags' else {'projectid':'projectidnotenabled'}
        enableProjects:bool = self.srvc.get(ENABLE_PROJECTS, None)
        if enableProjects:
            mlflow_project_id_infinstor = os.environ.get("MLFLOW_PROJECT_ID_INFINSTOR", None)
            # if server side has projects enabled but no environment variable set, raise and exception
            if not mlflow_project_id_infinstor:
                errmsg:str = f"enableProjects={enableProjects} on the server side but MLFLOW_PROJECT_ID_INFINSTOR environment variable not set; set this environment variable and try the operation again"
                logger.error(errmsg)
                raise Exception(errmsg)
            retval = { 'key':'projectid', 'value':mlflow_project_id_infinstor } if tagIn == 'body' else ExperimentTag('projectid',mlflow_project_id_infinstor) if tagIn=='api_tags' else {'projectid':mlflow_project_id_infinstor}
        else:  
            logger.warn(f"attempt to set mandatory tag projectid when enableProjects={enableProjects}.  Fix caller of this code..", traceback.extract_stack())
        
        return retval

    def _add_or_update_api_tags_with_projectid_tag(self, api_tags:List[ExperimentTag]) -> List[ExperimentTag]:
        """ adds the 'projectid' tag to the specified 'api dict'.  Raises an exception if enableProjects is true on the server side and MLFLOW_PROJECT_ID_INFINSTOR is not defined..
        
        Note that calls to mlflow APIs which accept a 'tags' parameter ( like createExperiment() API ) expect 'tags' to be List[ExperimentTag]..  But in the actual REST request, in the body, the format for tags is different: [ {'key':'tag1', 'value':'tag1_value'}, ... ]

        Args:
            api_tags (list): [<ExperimentTag: key='projectid', value='projectdatascientists'>]

        Returns:
            the 'api_tags' that was passed to this method
        """
        enableProjects:bool = self.srvc.get(ENABLE_PROJECTS, None)
        if enableProjects:
            # [<ExperimentTag: key='projectid', value='projectdatascientists'>]
            exptag:ExperimentTag
            for exptag in api_tags:
                # if projectid is already set, don't set it again: user specified overrides environment variable       
                if exptag.key == "projectid": break
            else: 
                # else clause: When the items are exhausted (which is immediately when the sequence is empty or an iterator raises a StopIteration exception), the suite in the else clause, if present, is executed, and the loop terminates.
                # add 'projectid' only if it is not already set..
                api_tags.append(self._get_dict_for_projectid_tag_in_body_or_api_tags_or_query_param(tagIn='api_tags'))
        else:  
            logger.warn(f"attempt to set mandatory tag projectid when enableProjects={enableProjects}.  Fix caller of this code..", traceback.extract_stack())
        
        return api_tags
        
    def _add_or_update_body_dict_with_projectid_tag(self, body:dict) -> dict:
        """ adds the 'projectid' tag to the specified 'body' dict.  Raises an exception if enableProjects is true on the server side and MLFLOW_PROJECT_ID_INFINSTOR is not defined..
        
        Note that calls to mlflow APIs which accept 'tags' ( like createExperiment() API ) expect 'tags' to be a dictionary with the dict 'key' being the name of the tag and 'value' being the value of the tag..  But in the body of the REST request, the format for tags is different: [ {'key':'tag1', 'value':'tag1_value'}, ... ]

        Args:
            body (dict): a dict, that represents the http body, to which the 'tags' key is added

        Returns:
            dict: the 'body' dict that was passed to this method
        """
        enableProjects:bool = self.srvc.get(ENABLE_PROJECTS, None)
        if enableProjects:
            # check if 'tags' key already exists.
            tags_in_body:list = body.get('tags')
            # if 'tags' not found, add 'tags'
            if not tags_in_body:
                tags_in_body = []; body['tags'] = tags_in_body
            
            # check if 'projectid' tag exists already in 'tags'
            tag:dict
            for tag in tags_in_body:
                # { 'key':'projectid', 'value':"projectidnotenabled" }
                if tag.get("key", None) == "projectid": break
            # if projectid tag doesn't exist, then add it from the environment variable
            else: # When the items are exhausted (which is immediately when the sequence is empty or an iterator raises a StopIteration exception), the suite in the else clause, if present, is executed, and the loop terminates.
                tags_in_body.append( self._get_dict_for_projectid_tag_in_body_or_api_tags_or_query_param(tagIn='body') )
        else:  
            logger.warn(f"attempt to set mandatory tag projectid when enableProjects={enableProjects}.  Fix caller of this code..", traceback.extract_stack())
        
        return body
        
    def create_registered_model(self, name, tags=None, description=None):
        """
        Create a new registered model in backend store.

        :param name: Name of the new model. This is expected to be unique in the backend store.
        :param tags: A list of :py:class:`mlflow.entities.model_registry.RegisteredModelTag`
                     instances associated with this registered model.
        :param description: Description of the model.
        :return: A single object of :py:class:`mlflow.entities.model_registry.RegisteredModel`
                 created in the backend.
        """
        headers = self.get_headers()
        url = 'https://' + self.get_service() + '/api/2.0/mlflow/registered-models/create'

        body = dict()
        body['name'] = name
        if (description != None):
            body['description'] = description

        tgs = []
        if (tags != None):
            for tag in tags:
                tgs.append({'key': tag.key, 'value': tag.value})
        body['tags'] = tgs
        # if ENABLE_PROJECTS is enabled on the server side        
        if self.srvc.get(ENABLE_PROJECTS, False): 
            logger.debug(f"create_registered_model(): before update: body={body}")
            # add the 'projectId' tag to the http body 
            self._add_or_update_body_dict_with_projectid_tag(body)
            logger.debug(f"create_registered_model(): after update: body={body}")

        try:
            response = requests.post(url, data=json.dumps(body), headers=headers)
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            raise
        except Exception as err:
            print(f'Other error occurred: {err}')
            raise
        regmod = response.json()['registered_model']
        return self.RegisteredModel_from_dict(regmod)

    def get_registered_model(self, name):
        """
        Get registered model instance by name.

        :param name: Registered model name.
        :return: A single :py:class:`mlflow.entities.model_registry.RegisteredModel` object.
        """
        headers = self.get_headers()
        url = 'https://' + self.get_service() + '/api/2.0/mlflow/registered-models/get'
        try:
            response = requests.get(url, params={'name':name}, headers=headers)
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            raise
        except Exception as err:
            print(f'Other error occurred: {err}')
            raise
        respjson = json.loads(response.text)
        regmod = respjson['registered_model']
        return self.RegisteredModel_from_dict(regmod)

    def rename_registered_model(self, name, new_name):
        """
        Rename the registered model.

        :param name: Registered model name.
        :param new_name: New proposed name.
        :return: A single updated :py:class:`mlflow.entities.model_registry.RegisteredModel` object.
        """
        headers = self.get_headers()
        url = 'https://' + self.get_service() + '/api/2.0/mlflow/registered-models/rename'
        body = {'name': name, 'new_name': new_name}

        try:
            response = requests.post(url, data=json.dumps(body), headers=headers)
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            raise
        except Exception as err:
            print(f'Other error occurred: {err}')
            raise
        regmod = response.json()['registered_model']
        return self.RegisteredModel_from_dict(regmod)

    def delete_registered_model(self, name):
        """
        Delete the registered model.
        Backend raises exception if a registered model with given name does not exist.

        :param name: Registered model name.
        :return: None
        """
        headers = self.get_headers()
        url = 'https://' + self.get_service() + '/api/2.0/mlflow/registered-models/delete'

        body = dict()
        body['name'] = name
        try:
            response = requests.delete(url, data=json.dumps(body), headers=headers)
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            raise
        except Exception as err:
            print(f'Other error occurred: {err}')
            raise

    def update_registered_model(self, name, description):
        """
        Update description of the registered model.

        :param name: Registered model name.
        :param description: New description.
        :return: A single updated :py:class:`mlflow.entities.model_registry.RegisteredModel` object.
        """
        headers = self.get_headers()
        url = 'https://' + self.get_service() + '/api/2.0/mlflow/registered-models/update'

        body = dict()
        body['name'] = name
        if (description):
            body['description'] = description

        try:
            response = requests.patch(url, data=json.dumps(body), headers=headers)
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            raise
        except Exception as err:
            print(f'Other error occurred: {err}')
            raise
        regmod = response.json()['registered_model']
        return self.RegisteredModel_from_dict(regmod)


    def update_model_version(self, name, version, description):
        headers = self.get_headers()
        url = 'https://' + self.get_service() + '/api/2.0/mlflow/model-versions/update'

        body = dict()
        body['name'] = name
        body['version'] = version
        if (description):
            body['description'] = description

        try:
            response = requests.patch(url, data=json.dumps(body), headers=headers)
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            raise
        except Exception as err:
            print(f'Other error occurred: {err}')
            raise
        modvers = response.json()['model_version']
        return self.ModelVersion_from_dict(modvers)


    def list_registered_models(self, max_results, page_token):
        """
        List of all registered models.

        :param max_results: Maximum number of registered models desired.
        :param page_token: Token specifying the next page of results. It should be obtained from
                            a ``list_registered_models`` call.
        :return: A PagedList of :py:class:`mlflow.entities.model_registry.RegisteredModel` objects
                that satisfy the search expressions. The pagination token for the next page can be
                obtained via the ``token`` attribute of the object.
        """
        headers = self.get_headers()
        url = 'https://' + self.get_service() + '/api/2.0/mlflow/registered-models/list'

        try:
            params={'max_results':max_results, 'page_token':page_token}
            if self.srvc.get(ENABLE_PROJECTS): 
                logger.debug(f"list_registered_models(): before update: params={params}")
                # adjust the query parameters to include the 'projectId' tag
                params.update(self._get_dict_for_projectid_tag_in_body_or_api_tags_or_query_param(tagIn='query_param'))
                logger.debug(f"list_registered_models(): after update: params={params}")
            response = requests.get(url,
                    params=params,
                    headers=headers)
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            raise
        except Exception as err:
            print(f'Other error occurred: {err}')
            raise
        respjson = json.loads(response.text)
        registered_models = respjson['registered_models']

        rma = []
        for regmod in registered_models:
            rma.append(self.RegisteredModel_from_dict(regmod))

        next_page_token = None
        if ('next_page_token' in respjson):
            next_page_token = respjson['next_page_token']
        return PagedList(rma, next_page_token)

    def search_registered_models(
        self, filter_string=None, max_results=None, order_by=None, page_token=None
    ):
        """
        Search for registered models in backend that satisfy the filter criteria.

        :param filter_string: Filter query string, defaults to searching all registered models.
        :param max_results: Maximum number of registered models desired.
        :param order_by: List of column names with ASC|DESC annotation, to be used for ordering
                         matching search results.
        :param page_token: Token specifying the next page of results. It should be obtained from
                            a ``search_registered_models`` call.
        :return: A PagedList of :py:class:`mlflow.entities.model_registry.RegisteredModel` objects
                that satisfy the search expressions. The pagination token for the next page can be
                obtained via the ``token`` attribute of the object.
        """
        headers = self.get_headers()
        url = 'https://' + self.get_service() + '/api/2.0/mlflow/registered-models/search'

        params = {}
        if (filter_string != None):
            params['filter'] = filter_string
        if (max_results != None):
            params['max_results'] = max_results
        if (order_by != None):
            params['order_by'] = order_by
        if (page_token != None):
            params['page_token'] = page_token
        try:
            if self.srvc.get(ENABLE_PROJECTS): 
                logger.debug(f"search_registered_models(): before update: params={params}")
                # adjust the query parms to include the 'projectId' tag
                params.update(self._get_dict_for_projectid_tag_in_body_or_api_tags_or_query_param(tagIn='query_param'))
                logger.debug(f"search_registered_models(): before update: params={params}")
            response = requests.get(url, params=params, headers=headers) 
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            raise
        except Exception as err:
            print(f'Other error occurred: {err}')
            raise
        respjson = json.loads(response.text)
        registered_models = respjson['registered_models']

        rma = []
        for regmod in registered_models:
            rma.append(self.RegisteredModel_from_dict(regmod))

        next_page_token = None
        if ('next_page_token' in respjson):
            next_page_token = respjson['next_page_token']
        return PagedList(rma, next_page_token)

    def set_registered_model_tag(self, name, tag):
        """
        Set a tag for the registered model.

        :param name: Registered model name.
        :param tag: :py:class:`mlflow.entities.model_registry.RegisteredModelTag` instance to log.
        :return: None
        """
        headers = self.get_headers()
        url = 'https://' + self.get_service() + '/api/2.0/mlflow/registered-models/set-tag'

        body = dict()
        body['name'] = name
        body['key'] = tag.key
        body['value'] = tag.value

        try:
            response = requests.post(url, data=json.dumps(body), headers=headers)
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            raise
        except Exception as err:
            print(f'Other error occurred: {err}')
            raise

    def delete_registered_model_tag(self, name, key):
        """
        Delete a tag associated with the registered model.

        :param name: Registered model name.
        :param key: Registered model tag key.
        :return: None
        """
        headers = self.get_headers()
        url = 'https://' + self.get_service() +'/api/2.0/mlflow/registered-models/delete-tag'
        body = dict()
        body['name'] = name
        body['key'] = key
        try:
            response = requests.delete(url, data=json.dumps(body), headers=headers)
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            raise
        except Exception as err:
            print(f'Other error occurred: {err}')
            raise

    # Model Versions CRUD
    def create_model_version(
        self, name, source, run_id=None, tags=None, run_link=None, description=None
    ):
        """
        Create a new model version from given source and run ID.

        :param name: Registered model name.
        :param source: Source path where the MLflow model is stored.
        :param run_id: Run ID from MLflow tracking server that generated the model.
        :param tags: A list of :py:class:`mlflow.entities.model_registry.ModelVersionTag`
                     instances associated with this model version.
        :param run_link: Link to the run from an MLflow tracking server that generated this model.
        :param description: Description of the version.
        :return: A single object of :py:class:`mlflow.entities.model_registry.ModelVersion`
                 created in the backend.
        """
        headers = self.get_headers()
        url = 'https://' + self.get_service() + '/api/2.0/mlflow/model-versions/create'

        body = dict()
        body['name'] = name
        body['source'] = source
        if (run_id != None):
            body['run_id'] = run_id
        tgs = []
        if (tags != None):
            for tag in tags:
                tgs.append({'key': tag.key, 'value': tag.value})
        body['tags'] = tgs
        if (description != None):
            body['description'] = description

        try:
            response = requests.post(url, data=json.dumps(body), headers=headers)
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            raise
        except Exception as err:
            print(f'Other error occurred: {err}')
            raise
        modvers = response.json()['model_version']
        return self.ModelVersion_from_dict(modvers)

    def set_model_version_tag(self, name, version, tag):
        """
        Set a tag for the model version.

        :param name: Registered model name.
        :param version: Registered model version.
        :param tag: :py:class:`mlflow.entities.model_registry.ModelVersionTag` instance to log.
        :return: None
        """
        headers = self.get_headers()
        url = 'https://' + self.get_service() + '/api/2.0/mlflow/model-versions/set-tag'

        body = dict()
        body['name'] = name
        body['version'] = version
        body['key'] = tag.key
        body['value'] = tag.value

        try:
            response = requests.post(url, data=json.dumps(body), headers=headers)
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            raise
        except Exception as err:
            print(f'Other error occurred: {err}')
            raise

    def delete_model_version_tag(self, name, version, key):
        """
        Delete a tag associated with the model version.

        :param name: Registered model name.
        :param version: Registered model version.
        :param key: Tag key.
        :return: None
        """
        headers = self.get_headers()
        url = 'https://' + self.get_service() + '/api/2.0/mlflow/model-versions/delete-tag'

        body = dict()
        body['name'] = name
        body['version'] = version
        body['key'] = key

        try:
            response = requests.delete(url, data=json.dumps(body), headers=headers)
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            raise
        except Exception as err:
            print(f'Other error occurred: {err}')
            raise

    def delete_model_version(self, name, version):
        """
        Delete model version in backend.

        :param name: Registered model name.
        :param version: Registered model version.
        :return: None
        """
        headers = self.get_headers()
        url = 'https://' + self.get_service() + '/api/2.0/mlflow/model-versions/delete'

        body = dict()
        body['name'] = name
        body['version'] = version

        try:
            response = requests.delete(url, data=json.dumps(body), headers=headers)
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            raise
        except Exception as err:
            print(f'Other error occurred: {err}')
            raise

    def transition_model_version_stage(self, name, version, stage, archive_existing_versions):
        """
        Update model version stage.

        :param name: Registered model name.
        :param version: Registered model version.
        :param new_stage: New desired stage for this model version.
        :param archive_existing_versions: If this flag is set to ``True``, all existing model
            versions in the stage will be automically moved to the "archived" stage. Only valid
            when ``stage`` is ``"staging"`` or ``"production"`` otherwise an error will be raised.

        :return: A single :py:class:`mlflow.entities.model_registry.ModelVersion` object.
        """
        headers = self.get_headers()
        url = 'https://' + self.get_service() \
                + '/api/2.0/mlflow/model-versions/transition-stage'

        body = dict()
        body['name'] = name
        body['stage'] = stage
        body['version'] = version
        body['archive_existing_versions'] = archive_existing_versions

        try:
            response = requests.post(url, data=json.dumps(body), headers=headers)
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            raise
        except Exception as err:
            print(f'Other error occurred: {err}')
            raise
        modvers = response.json()['model_version']
        return self.ModelVersion_from_dict(modvers)

    def get_model_version(self, name, version):
        """
        Get the model version instance by name and version.

        :param name: Registered model name.
        :param version: Registered model version.
        :return: A single :py:class:`mlflow.entities.model_registry.ModelVersion` object.
        """
        headers = self.get_headers()
        url = 'https://' + self.get_service() + '/api/2.0/mlflow/model-versions/get'

        params = {}
        params['name'] = name
        params['version'] = version
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            raise
        except Exception as err:
            print(f'Other error occurred: {err}')
            raise
        modvers = response.json()['model_version']
        return self.ModelVersion_from_dict(modvers)

    def search_model_versions(self, filter_string):
        """
        Search for model versions in backend that satisfy the filter criteria.

        :param filter_string: A filter string expression. Currently supports a single filter
                              condition either name of model like ``name = 'model_name'`` or
                              ``run_id = '...'``.
        :return: PagedList of :py:class:`mlflow.entities.model_registry.ModelVersion`
                 objects.
        """
        headers = self.get_headers()
        url = 'https://' + self.get_service() + '/api/2.0/mlflow/model-versions/search'

        params = {}
        if (filter_string != None):
            params['filter'] = filter_string
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            raise
        except Exception as err:
            print(f'Other error occurred: {err}')
            raise
        respjson = json.loads(response.text)
        model_versions = respjson['model_versions']

        rma = []
        for modvers in model_versions:
            rma.append(self.ModelVersion_from_dict(modvers))
        return PagedList(rma, 'unused')

    def RegisteredModel_from_dict(self, regmod):
        ct = None
        dscr = None
        lu = None
        tgs = None
        if ('creation_timestamp' in regmod):
            ct = regmod['creation_timestamp']
        if ('description' in regmod):
            dscr = regmod['description']
        if ('last_updated_timestamp' in regmod):
            lu = regmod['last_updated_timestamp']
        if ('tags' in regmod):
            tgs_in = regmod['tags']
            tgs = []
            for one_tg_in in tgs_in:
                tgs.append(TagWithProperties(one_tg_in['key'], one_tg_in['value']))
        return RegisteredModel(regmod['name'], creation_timestamp=ct,
                last_updated_timestamp=lu, description=dscr,
                latest_versions=self.get_latest_versions(regmod['name']),
                tags=tgs)

    def ModelVersion_from_dict(self, modvers):
        if ('description' in modvers):
            description=modvers['description']
        else:
            description=None
        if ('run_id' in modvers):
            run_id=modvers['run_id']
        else:
            run_id=None
        if ('run_link' in modvers):
            run_link=modvers['run_link']
        else:
            run_link=None
        if ('tags' in modvers):
            tgs_in = modvers['tags']
            tgs = []
            for one_tg_in in tgs_in:
                tgs.append(TagWithProperties(one_tg_in['key'], one_tg_in['value']))
        else:
            tgs = None
        return ModelVersion(modvers['name'], modvers['version'],
                modvers['creation_timestamp'],
                last_updated_timestamp=modvers['last_updated_timestamp'],
                description=description, user_id=modvers['user_id'],
                current_stage=modvers['current_stage'], source=modvers['source'],
                run_id=run_id, status=modvers['status'], status_message=None, tags=tgs,
                run_link=run_link)

    def list_experiments(
        self, view_type=ViewType.ACTIVE_ONLY, max_results=None, page_token=None,
    ):
        """
        Modified copy from mlflow/store/tracking/rest_store.py
        
        :param view_type: Qualify requested type of experiments.
        :param max_results: If passed, specifies the maximum number of experiments desired. If not
                            passed, the server will pick a maximum number of results to return.
        :param page_token: Token specifying the next page of results. It should be obtained from
                            a ``list_experiments`` call.
        :return: A :py:class:`PagedList <mlflow.store.entities.PagedList>` of
                 :py:class:`Experiment <mlflow.entities.Experiment>` objects. The pagination token
                 for the next page can be obtained via the ``token`` attribute of the object.
        """
        # req_body_jsonstr={"view_type": "ACTIVE_ONLY", "max_results": "1000" }
        # req_body_jsonstr is a representation of the query param by the marshalling library.. on the wire, this is sent as query param
        req_body_jsonstr:str = message_to_json(
            ListExperiments(view_type=view_type, max_results=max_results, page_token=page_token)
        )
        
        logger.debug(f"list_experiments(): before modify: req_body_jsonstr={req_body_jsonstr}")
        # if ENABLE_PROJECTS is enabled on the server side
        if self.srvc.get(ENABLE_PROJECTS, False):
            # append mandatory tags (projectid mandatory tag) to the body
            req_body:dict = json.loads(req_body_jsonstr)
            # list_experiments() API does not support tags yet.  So API request body will not have 'tags' key.  So blindly add 'tags' key, without checking if it already exists or not
            # add 'projectId' tag to the query parm
            req_body.update(self._get_dict_for_projectid_tag_in_body_or_api_tags_or_query_param(tagIn='query_param'))
            req_body_jsonstr = json.dumps(req_body)
        logger.debug(f"list_experiments(): after modify: req_body_jsonstr={req_body_jsonstr}")
        
        response_proto = self._call_endpoint(ListExperiments, req_body_jsonstr)
        experiments = [Experiment.from_proto(x) for x in response_proto.experiments]
        # If the response doesn't contain `next_page_token`, `response_proto.next_page_token`
        # returns an empty string (default value for a string proto field).
        token = (
            response_proto.next_page_token if response_proto.HasField("next_page_token") else None
        )
        return PagedList(experiments, token)

    def create_experiment(self, name, artifact_location=None, tags:List[ExperimentTag]=None):
        """
        Create a new experiment.
        If an experiment with the given name already exists, throws exception.

        :param name: Desired name for an experiment
        :param tags: [<ExperimentTag: key='projectid', value='projectdatascientists'>]

        :return: experiment_id (string) for the newly created experiment if successful, else None
        """
        # if ENABLE_PROJECTS is enabled on the server side, add the 'projectid' tag to 'tags'
        logger.debug(f"create_experiment(): before modify: tags={tags}")
        if self.srvc.get(ENABLE_PROJECTS, False): 
            # tags = [<ExperimentTag: key='projectid', value='projectdatascientists'>]
            tags = [] if tags == None else tags
            # add 'projectId' tag to 'tags', which is List[ExperimentTag], if needed.
            self._add_or_update_api_tags_with_projectid_tag(tags)
        logger.debug(f"create_experiment(): after modify: tags={tags}")
        
        return super().create_experiment(name, artifact_location, tags)

    def __init__(self, store_uri=None, artifact_uri=None):
        """ 'srvc': a dictionary which contains the details of the service.  See login.bootstrap_from_mlflow_rest() or /api/2.0/mlflow/infinstor/get_version() for details """
        self.srvc:Dict[str, Any] = login.bootstrap_from_mlflow_rest() 
        set_builtins_with_serverside_config(self.srvc)
        
        # use idToken and call /customerinfo REST api, to read enableProjects flag from server side
        customerinfo:dict = login.get_customer_info_rest(self.get_id_token_string())
        # set enableProjects / isProjectEnabled ; /customer_info REST response has 'enableProjects': 'true'
        builtins.enableProjects = True if customerinfo.get('enableProjects', False) == 'true' else False
        self.srvc[ENABLE_PROJECTS] = builtins.enableProjects
        logger.debug(f"mlflow server has ENABLE_PROJECTS={self.srvc[ENABLE_PROJECTS]}")
        
        super().__init__(self.cognito_host_creds)
