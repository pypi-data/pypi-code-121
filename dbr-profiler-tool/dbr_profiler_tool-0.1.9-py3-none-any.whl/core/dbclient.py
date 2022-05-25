from distutils.log import INFO
import json
from logging import exception
import os
import requests
import re
import time

from core import logging_utils
#import requests.packages.urllib3

global pprint_j
loggr=None

if loggr == None:
    loggr = logging_utils.get_logger(__name__)

requests.packages.urllib3.disable_warnings()

# Helper to pretty print json
def pprint_j(i):
    return(json.dumps(i, indent=4, sort_keys=True))



class dbclient:
    """
    Rest API Wrapper for Databricks APIs
    """
    # set of http error codes to throw an exception if hit. Handles client and auth errors
    http_error_codes = [401]

    def __init__(self, configs):
        self._profile = configs['profile']
        self._raw_url = configs['url']
        self._url=self._raw_url
        self._export_db = configs['export_db']
        self._is_azure = configs['is_azure']
        self._verify_ssl = configs['verify_ssl']
        self._verbosity = configs['verbosity']
        self._cluster_id=configs['clusterid']
        self._token = ''
        self._raw_token = configs['token']
        self._master_name_scope=configs['master_name_scope']
        self._master_name_key=configs['master_name_key']
        self._master_password_scope=configs['master_pwd_scope']
        self._master_password_key=configs['master_pwd_key']
        self._master_name=''
        self._master_password=''

        if self._verify_ssl == True:
            pass
            # set these env variables if skip SSL verification is enabled
            #os.environ['REQUESTS_CA_BUNDLE'] = ""
            #os.environ['CURL_CA_BUNDLE'] = ""


    def _update_token_master(self):
        import base64
        def get_secret_value(scope_name, secret_key, cid):
            ec_id = self.get_execution_context(cid)
            cmd_set_value = f"value = dbutils.secrets.get(scope = '{scope_name}', key = '{secret_key}')"
            cmd_convert_b64 = "import base64; b64_value = base64.b64encode(value.encode('ascii'))"
            cmd_get_b64 = "print(str(b64_value.decode('ascii')))"   # b64_value.decode('ascii')
            results_set = self.submit_command(cid, ec_id, cmd_set_value)
            results_convert = self.submit_command(cid, ec_id, cmd_convert_b64)
            results_get = self.submit_command(cid, ec_id, cmd_get_b64)
            val = results_get.get('data')
            b64_value_decode = base64.b64decode(val).decode('ascii')
            return b64_value_decode

        if(self._master_name==''): #do it first time
            #secretsClient=SecretsClient(self)
            self._master_name = get_secret_value(self._master_name_scope, self._master_name_key, self._cluster_id )
            self._master_password = get_secret_value(self._master_password_scope, self._master_password_key, self._cluster_id)    
        userAndPass = base64.b64encode(f"{self._master_name}:{self._master_password}".encode("ascii")).decode("ascii")
        self._url = "https://accounts.cloud.databricks.com" #url for accounts api
        self._token = {
            'Authorization' : 'Basic {0}'.format(userAndPass),
            'User-Agent': 'databricks-profiler/0.1.0'
        }

    def _update_token(self):
        self._url=self._raw_url #accounts api uses a different url
        self._token = {
            'Authorization': 'Bearer {0}'.format(self._raw_token),
            'User-Agent': 'databricks-profiler/0.1.0'
        }


    def test_connection(self, master_acct=False):
            if master_acct: #master acct may use a different credential
                self._update_token_master()
            else:
                self._update_token()

            results = requests.get(self._url + '/api/2.0/clusters/spark-versions', headers=self._token,
                                verify=self._verify_ssl)
            http_status_code = results.status_code
            if http_status_code != 200:
                loggr.info("Error. Either the credentials have expired or the credentials don't have proper permissions.")
                loggr.info("If you have a ~/.netrc file, check those credentials. Those take precedence over passed input.")
                loggr.info(results.reason)
                loggr.info(results.text)
                raise Exception('Test connection failed ' + results.reason)
            return True

    default_ignore_error_list=[
        'RESOURCE_ALREADY_EXISTS'
    ]

    def check_error(response, ignore_error_list=default_ignore_error_list):
        return ('error_code' in response and response['error_code'] not in ignore_error_list) \
                or ('error' in response and response['error'] not in ignore_error_list) \
                or (type(response)==dict and response.get('resultType', None) == 'error' and 'already exists' not in response.get('summary', None))


    def get(self, endpoint, json_params=None, version='2.0', master_acct=False):
        if master_acct:
            self._update_token_master()
        else:
            self._update_token()

        while True:
            full_endpoint = self._url + '/api/{0}'.format(version) + endpoint
            
            loggr.debug("Get: {0}".format(full_endpoint))

            if json_params:
                raw_results = requests.get(full_endpoint, headers=self._token, params=json_params, verify=self._verify_ssl)
            else:
                raw_results = requests.get(full_endpoint, headers=self._token, verify=self._verify_ssl)


            http_status_code = raw_results.status_code
            if http_status_code in dbclient.http_error_codes:
                raise Exception("Error: GET request failed with code {}\n{}".format(http_status_code, raw_results.text))
            results = raw_results.json()
            if logging_utils.check_error(results):
                loggr.warn(json.dumps(results) + '\n')
            loggr.debug(json.dumps(results, indent=4, sort_keys=True))
            if type(results) == list:
                results = {'elements': results}
            results['http_status_code'] = http_status_code
            return results

    def http_req(self, http_type, endpoint, json_params, version='2.0', files_json=None, master_acct=False):
        if master_acct:
            self._update_token_master()
            self._url = "https://accounts.cloud.databricks.com"
        else:
            self._update_token()
            self._url=self._raw_url
        if version:
            ver = version
        while True:
            full_endpoint = self._url + '/api/{0}'.format(ver) + endpoint
            loggr.debug("{0}: {1}".format(http_type, full_endpoint))
            if json_params:
                if http_type == 'post':
                    if files_json:
                        raw_results = requests.post(full_endpoint, headers=self._token,
                                                    data=json_params, files=files_json, verify=self._verify_ssl)
                    else:
                        raw_results = requests.post(full_endpoint, headers=self._token,
                                                    json=json_params, verify=self._verify_ssl)
                if http_type == 'put':
                    raw_results = requests.put(full_endpoint, headers=self._token,
                                               json=json_params, verify=self._verify_ssl)
                if http_type == 'patch':
                    raw_results = requests.patch(full_endpoint, headers=self._token,
                                                 json=json_params, verify=self._verify_ssl)
            else:
                loggr.info("Must have a payload in json_args param.")
                return {}


            http_status_code = raw_results.status_code
            if http_status_code in dbclient.http_error_codes:
                raise Exception("Error: {0} request failed with code {1}\n{2}".format(http_type,
                                                                                      http_status_code,
                                                                                      raw_results.text))
            results = raw_results.json()
            if logging_utils.check_error(results):
                loggr.warn(json.dumps(results) + '\n')

            loggr.debug(json.dumps(results, indent=4, sort_keys=True))
            # if results are empty, let's return the return status
            if results:
                results['http_status_code'] = raw_results.status_code
                return results
            else:
                return {'http_status_code': raw_results.status_code}

    def post(self, endpoint, json_params, version='2.0', files_json=None, master_acct=False):
        if master_acct:
            self._update_token_master()
            self._url = "https://accounts.cloud.databricks.com"
        else:
            self._update_token()
            self._url=self._raw_url    
        return self.http_req('post', endpoint, json_params, version, files_json)

    def put(self, endpoint, json_params, version='2.0', master_acct=False):
        if master_acct:
            self._update_token_master()
            self._url = "https://accounts.cloud.databricks.com"
        else:
            self._update_token()
            self._url=self._raw_url           
        return self.http_req('put', endpoint, json_params, version)

    def patch(self, endpoint, json_params, version='2.0', master_acct=False):
        if master_acct:
            self._update_token_master()
            self._url = "https://accounts.cloud.databricks.com"
        else:
            self._update_token()
            self._url=self._raw_url                   
        return self.http_req('patch', endpoint, json_params, version)

    def get_execution_context(self, cid):
        self._update_token()
        loggr.debug("Creating remote Spark Session")
        #time.sleep(5)
        ec_payload = {"language": "python",
                    "clusterId": cid}
        ec = self.post('/contexts/create', json_params=ec_payload, version="1.2")
        # Grab the execution context ID
        ec_id = ec.get('id', None)
        if ec_id is None:
            loggr.info('Remote session error. Cluster may not be started')
            loggr.info(ec)
            raise Exception("Remote session error. Cluster may not be started.")
        return ec_id


    def submit_command(self, cid, ec_id, cmd):
        self._update_token()
        # This launches spark commands and print the results. We can pull out the text results from the API
        command_payload = {'language': 'python',
                        'contextId': ec_id,
                        'clusterId': cid,
                        'command': cmd}
        command = self.post('/commands/execute',
                            json_params=command_payload,
                            version="1.2")

        com_id = command.get('id', None)
        if com_id is None:
            loggr.error(command)
        # print('command_id : ' + com_id)
        result_payload = {'clusterId': cid, 'contextId': ec_id, 'commandId': com_id}

        resp = self.get('/commands/status', json_params=result_payload, version="1.2")
        is_running = self.get_key(resp, 'status')

        # loop through the status api to check for the 'running' state call and sleep 1 second
        while (is_running == "Running") or (is_running == 'Queued'):
            resp = self.get('/commands/status', json_params=result_payload, version="1.2")
            is_running = self.get_key(resp, 'status')
            time.sleep(1)
        end_result_status = self.get_key(resp, 'status')
        end_results = self.get_key(resp, 'results')
        if end_results.get('resultType', None) == 'error':
            loggr.error(end_results.get('summary', None))
        return end_results


    @staticmethod
    def get_key(http_resp, key_name):
        value = http_resp.get(key_name, None)
        if value is None:
            raise ValueError('Unable to find key ' + key_name)
        return value



    def start_cluster_by_name(self, cluster_name):
        cid = self.get_cluster_id_by_name(cluster_name)
        if cid is None:
            raise Exception('Error: Cluster name does not exist')
        loggr.info("Starting {0} with id {1}".format(cluster_name, cid))
        resp = self.post('/clusters/start', {'cluster_id': cid})
        if 'error_code' in resp:
            if resp.get('error_code', None) == 'INVALID_STATE':
                loggr.error(resp.get('message', None))
            else:
                raise Exception('Error: cluster does not exist, or is in a state that is unexpected. '
                                'Cluster should either be terminated state, or already running.')
        self.wait_for_cluster(cid)
        return cid
        
    def wait_for_cluster(self, cid):
        c_state = self.get('/clusters/get', {'cluster_id': cid})
        while c_state['state'] != 'RUNNING' and c_state['state'] != 'TERMINATED':
            c_state = self.get('/clusters/get', {'cluster_id': cid})
            loggr.info('Cluster state: {0}'.format(c_state['state']))
            time.sleep(2)
        if c_state['state'] == 'TERMINATED':
            raise RuntimeError("Cluster is terminated. Please check EVENT history for details")
        return cid



    def whoami(self):
        """
        get current user userName from SCIM API
        :return: username string
        """
        user_name = self.get('/preview/scim/v2/Me').get('userName')
        return user_name



    def set_export_dir(self, dir_location):
        self._export_dir = dir_location

    def get_export_dir(self):
        return self._export_dir

    def get_url(self):
        return self._url

    def get_latest_spark_version(self):
        versions = self.get('/clusters/spark-versions')['versions']
        v_sorted = sorted(versions, key=lambda i: i['key'], reverse=True)
        for x in v_sorted:
            img_type = x['key'].split('-')[1][0:5]
            if img_type == 'scala':
                return x


    @staticmethod
    def listdir(f_path):
        ls = os.listdir(f_path)
        for x in ls:
            # remove hidden directories / files from function
            if x.startswith('.'):
                continue
            yield x

    @staticmethod
    def walk(f_path):
        for my_root, my_subdir, my_files in os.walk(f_path):
            # filter out files starting with a '.'
            filtered_files = list(filter(lambda x: not x.startswith('.'), my_files))
            yield my_root, my_subdir, filtered_files

    @staticmethod
    def delete_dir_if_empty(local_dir):
        if len(os.listdir(local_dir)) == 0:
            os.rmdir(local_dir)       



    @staticmethod
    def my_map(F, items):
        to_return = []
        for elem in items:
            to_return.append(F(elem))
        return to_return            

 