from infinstor_mlflow_plugin.tokenfile import get_token, get_id_token
from infinstor_mlflow_plugin import set_builtins_with_serverside_config
from infinstor_mlflow_plugin import login
from mlflow.store.artifact.s3_artifact_repo import S3ArtifactRepository
import os
from os.path import sep, expanduser
import builtins
from urllib.parse import quote
from urllib.request import unquote, urlretrieve
from requests.exceptions import HTTPError
import requests
import mlflow
from mlflow.utils.file_utils import relative_path_to_artifact_path
from mlflow.entities import FileInfo
import xml.etree.ElementTree as ET
from mlflow import data
from mlflow.exceptions import MlflowException
from . import tokenfile

class InfinStorArtifactRepository(S3ArtifactRepository):
    """LocalArtifactRepository provided through plugin system"""
    is_plugin = True

    def __init__(self, artifact_uri):
        self.srvc = login.bootstrap_from_mlflow_rest() 
        set_builtins_with_serverside_config(self.srvc)
        id_token, service = get_id_token(self.srvc['region'])
        rj = login.get_customer_info_rest(id_token)
        if 'usePresignedUrlForMLflow' in rj and rj['usePresignedUrlForMLflow'] == 'true':
            print('InfinStorArtifactRepository: usePresignedUrlForMLflow='
                    + str(rj['usePresignedUrlForMLflow']), flush=True)
            self.use_presigned_url_for_mlflow = True
        else:
            self.use_presigned_url_for_mlflow = False
        # Ugly, but we need to determine the run_id from the artifact URI.
        # artifact URI is either the artifact URI for the run, which will always end with the run_id
        # or the model URI, which will always end with run_id/<>
        last_slash = artifact_uri.rfind('/')
        if last_slash == -1:
            raise ValueError('artifact_uri ' + str(artifact_uri) + ' does not include run_id')
        self.this_run_id = artifact_uri[last_slash+1:]
        if self.is_run_id_valid(self.this_run_id):
            self.is_models_uri = False
            self.model_subpath = None
        else:
            success, run_id, subpath = self.parse_run_id_from_uri(artifact_uri)
            if success:
                self.is_models_uri = True
                self.this_run_id = run_id
                self.model_subpath = subpath
            else:
                raise ValueError('Unable to extract run_id from artifact_uri ' + str(artifact_uri))
        if self.use_presigned_url_for_mlflow:
            print('InfinStorArtifactRepository.initialized. artifact_uri=' + artifact_uri\
                +', is_models_uri=' + str(self.is_models_uri)\
                + ', run_id=' + self.this_run_id\
                + ', model_subpath=' + str(self.model_subpath))
        super().__init__(artifact_uri)

    def is_run_id_valid(self, run_id):
        ind = run_id.find('-')
        if ind == -1:
            return False
        try:
            exp_id = int(run_id[:ind])
            run_id_portion = int(run_id[ind+1:])
            return True
        except ValueError as verr:
            return False

    def parse_run_id_from_uri(self, artifact_uri):
        au_parts = artifact_uri.lstrip('/').rstrip('/').split('/')
        for ind in range(len(au_parts), 0, -1):
            run_id = au_parts[ind-1]
            if self.is_run_id_valid(run_id):
                subpath = ''
                for ind1 in range(ind, len(au_parts), 1):
                    subpath = subpath + '/' + au_parts[ind1]
                subpath = subpath.lstrip('/').rstrip('/')
                return True, run_id, subpath
        return False, '', ''

    def _get_s3_client(self):
        if not self.use_presigned_url_for_mlflow:
            return super()._get_s3_client()
        return None

    def _upload_file(self, s3_client, local_file, bucket, key):
        if not self.use_presigned_url_for_mlflow:
            return super()._upload_file(s3_client, local_file, bucket, key)
        print('InfinStorArtifactRepository._upload_file: local_file=' + local_file\
                + ', bucket=' + str(bucket) + ', key=' + key)
        (apbucket, artifact_path) = data.parse_s3_uri(self.artifact_uri)
        self._verify_listed_object_contains_artifact_path_prefix(
            listed_object_path=key, artifact_path=artifact_path
        )
        if apbucket != bucket:
            raise MlflowException(
                "InfinStorArtifactRepository:_upload_file bucket mismatch. artifact_bucket="\
                        + apbucket + ", bucket in=" + bucket)
        new_key = key[len(artifact_path):].lstrip('/')
        ps_url = self.get_presigned_url(new_key, 'put_object')
        with open(local_file, 'rb') as fp:
            file_data = fp.read()
            hr = requests.put(ps_url, data=file_data)
            if (hr.status_code != 200):
                print('InfinStorArtifactRepository._upload_file: WARNING. upload resp != 200. is '\
                        + str(hr.status_code))

    def _download_file(self, remote_file_path, local_path):
        if not self.use_presigned_url_for_mlflow:
            return super()._download_file(remote_file_path, local_path)
        if self.is_models_uri:
            remote_file_path = self.model_subpath + '/' + remote_file_path
        print('InfinStorArtifactRepository._download_file: remote_file_path='\
                + str(remote_file_path) + ', local_path=' + str(local_path))
        ps_url = self.get_presigned_url(remote_file_path, 'get_object')
        urlretrieve(ps_url, local_path)

    def _is_directory(self, artifact_path):
        if not self.use_presigned_url_for_mlflow:
            return super()._is_directory(artifact_path)
        if not artifact_path:
            #print('InfinStorArtifactRepository._is_directory: True since no artifact_path')
            return True
        if artifact_path[-1] == '/':
            #print('InfinStorArtifactRepository._is_directory: True since artifact_path ends in /')
            return True
        ps_url = self.get_presigned_url(artifact_path, 'list_objects_v2')
        try:
            response = requests.get(ps_url)
            response.raise_for_status()
        except HTTPError as http_err:
            print('InfinStorArtifactRepository._is_directory: HTTP error occurred: '\
                    + str(http_err))
            raise
        except Exception as err:
            print('InfinStorArtifactRepository._is_directory: Other error occurred: ' + str(err))
            raise
        root = ET.fromstring(response.content)
        for child in root:
            if (child.tag.endswith('CommonPrefixes')):
                #print('InfinStorArtifactRepository._is_directory: True since at least 1 common prefix is present')
                return True
        #print('InfinStorArtifactRepository._is_directory: False since at no common prefix is present')
        return False

    def list_artifacts(self, path):
        if not self.use_presigned_url_for_mlflow:
            return super().list_artifacts(path=path)
        if not path:
            path = ''
        elif path[len(path) - 1] != '/':
            path = path + '/'
        # path is guaranteed to be a directory
        print('InfinStorArtifactRepository.list_artifacts: path=' + path\
                + ', artifact_uri=' + str(self.artifact_uri))
        (bucket, artifact_path) = data.parse_s3_uri(self.artifact_uri)
        if self.is_models_uri:
            path = self.model_subpath + '/' + path
        ps_url = self.get_presigned_url(path, 'list_objects_v2')
        try:
            response = requests.get(ps_url)
            response.raise_for_status()
        except HTTPError as http_err:
            print('list_artifacts: HTTP error occurred: ' + str(http_err))
            raise
        except Exception as err:
            print('list_artifacts: Other error occurred: ' + str(err))
            raise
        #print('InfinStorArtifactRepository.list_artifacts: resp=' + str(response.content))
        root = ET.fromstring(response.content)
        infos=[]
        for child in root:
            if (child.tag.endswith('CommonPrefixes')):
                for child1 in child:
                    fp = unquote(str(child1.text))
                    self._verify_listed_object_contains_artifact_path_prefix(
                        listed_object_path=fp, artifact_path=artifact_path
                    )
                    fp1 = fp[len(artifact_path)+1:]
                    fp2 = fp1.rstrip('/')
                    infos.append(FileInfo(fp2, True, None))
            elif (child.tag.endswith('Contents')):
                filesize = 0
                filename = None
                for child1 in child:
                    if child1.tag.endswith('Key'):
                        filename = child1.text
                    elif child1.tag.endswith('Size'):
                        filesize = int(child1.text)
                if filename:
                    fp = unquote(str(filename))
                    self._verify_listed_object_contains_artifact_path_prefix(
                        listed_object_path=fp, artifact_path=artifact_path
                    )
                    fp1 = fp[len(artifact_path)+1:]
                    fp2 = fp1.rstrip('/')
                    fp3 = fp2.lstrip('/')
                    infos.append(FileInfo(fp3, False, filesize))
        return infos

    def get_presigned_url(self, prefix, method):
        tokfile = tokenfile.get_token_file_name()
        attempt = 0
        while attempt < 2:
            if attempt == 0:
                force = False
            else:
                print('get_presigned_url: retrying')
                force = True
            attempt = attempt + 1
            token, service = get_token(builtins.region,
                tokfile, force)
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Authorization': token
                }
            url = 'https://' + builtins.mlflowserver\
                    + '/Prod/2.0/mlflow/artifacts/getpresignedurl'\
                    + '?run_id=' + self.this_run_id\
                    + '&path=' + quote(prefix)\
                    + '&method=' + method
            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
            except HTTPError as http_err:
                print('HTTP error occurred: ' + str(http_err))
                raise
            except Exception as err:
                print('Other error occurred: ' + str(err))
                raise
            if 'Login expired. Please login again' in response.text:
                continue
            js = response.json()
            return js['presigned_url']
        print('get_presigned_url: Tried twice. Giving up')
        return None

