#!/usr/bin/env python3

#  (C) Copyright IBM Corp. 2021.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import os
import sys
import importlib.util
from pathlib import Path
import platform
import ibm_watson_machine_learning._wrappers.requests as requests
import json
import logging
from ibm_watson_machine_learning.wml_resource import WMLResource
from ibm_watson_machine_learning.wml_client_error import WMLClientError

logger = logging.getLogger(__name__)

def process_heartbeat(client, **kwargs):
    try:
        config_dict = kwargs.get('config_dict')
        agg_info = config_dict.get('aggregator')
        wml_services_url = agg_info['ip'].split('/')[0]

        hearbeat_resp = requests.get("https://" + wml_services_url + "/wml_services/training/heartbeat")
        hearbeat_resp_json = json.loads(hearbeat_resp.content.decode("utf-8"))
        service_version = hearbeat_resp_json.get("service_implementation")

        if service_version.startswith("4.0"):
            version_details = service_version.split('-')
            if version_details[1] >= "202203":
                return "cpd408"
            if version_details[1] >= "202202":
                return "cpd407"
            if version_details[1] >= "202112":
                return "cpd406"
            elif version_details[1] >= "202110":
                return "cpd403"
            elif version_details[1] >= "202108":
                return "cpd402"
            else:
                return "cpd401"
        if service_version.startswith("35"):
            return "cpd35"

        return "cloud"

    except Exception as ex:
        logger.info("unable to process heartbeat")
        logger.exception(ex)
        return "cloud"


def import_diff(module_file_path):

    if "py38-tf24-pt17-sk23" in module_file_path:
        return
    pathlist = Path(module_file_path).rglob('*.py')
    for path in pathlist:
        # because path is object not string
        path_in_str = str(path)
        if not path_in_str.endswith("__init__.py"):
            module_name = ("ibmfl" + path_in_str.split("ibmfl")[2].replace("/", "."))[:-3]
            module_spec = importlib.util.spec_from_file_location(
                module_name, path_in_str)
            loader = importlib.util.LazyLoader(module_spec.loader)
            module_spec.loader = loader
            module = importlib.util.module_from_spec(module_spec)
            sys.modules[module_name] = module
            module_spec.loader.exec_module(module)


def choose_software_version(software_spec):
    if software_spec == "runtime-22.1-py3.9" or software_spec == "12b83a17-24d8-5082-900f-0ab31fbfd3cb":
        return "py39-tf27-pt110-sk10"
    else:
        return "py38-tf24-pt17-sk23"


def check_python_version(platform_env):
    py_version = platform.python_version()
    if platform_env != "cloud" and platform_env != "cpd407" and platform_env != "cpd408":
        if not py_version.startswith("3.7.") and not py_version.startswith("3.8."):
            raise Exception("Python version {} is not supported for Federated Learning. "
                            "Parties must use a supported Python version to train the model. "
                            "For details, please refer to the documentation".format(py_version))
    else:
        if not py_version.startswith("3.7.") and not py_version.startswith("3.8.") and not py_version.startswith("3.9"):
            raise Exception("Python version {} is not supported for Federated Learning. "
                            "Parties must use a supported Python version to train the model. "
                            "For details, please refer to the documentation".format(py_version))


fl_path = os.path.abspath('.')
if fl_path not in sys.path:
    sys.path.append(fl_path)


class Party(WMLResource):
    """
    Party Wrapper for determining required version of FL Party to invoke.
    """

    SUPPORTED_PLATFORMS_MAP = {
        'cloud': "/cloud/ibmfl",
        'cpd35': "1.0.181",
        'cpd401': "1.0.122",
        'cpd402': "1.0.165",
        'cpd403': "/cpd403/ibmfl",
        'cpd406': "/cpd406/ibmfl",
        'cpd407': "/cpd406/ibmfl",
        'cpd408': "/cpd406/ibmfl",
        'py38-tf24-pt17-sk23': "/py38-tf24-pt17-sk23/ibmfl", #default
        'py39-tf27-pt110-sk10': "/py39-tf27-pt110-sk10/ibmfl"
    }

    def __init__(self, client=None, **kwargs):

        libs_module = sys.modules['ibm_watson_machine_learning.libs']
        libs_location_list = libs_module.__path__

        # base location string, default to cloud location
        ibmfl_base_module_location = libs_location_list[0] + '/ibmfl'

        # get arg for platform
        calculated_platform_env = process_heartbeat(client=client, **kwargs)
        platform_env = kwargs.get('env', calculated_platform_env)

        #check python version
        check_python_version(platform_env)

        # process location
        ibmfl_module_location = ibmfl_base_module_location + self.SUPPORTED_PLATFORMS_MAP.get(platform_env)
        if not ibmfl_module_location.endswith("ibmfl"):
            raise Exception("Please use ibm-watson-machine-learning " + self.SUPPORTED_PLATFORMS_MAP.get(platform_env) )

        #check if using old connector script which is removed
        if not client:
            raise Exception("This version of the party connector script is outdated. "
                            "Please download the party connector script from your current Federated Learning experiment. "
                            "For more details, please refer to the documentation.")

        self.module_location = ibmfl_module_location
        self.args = kwargs
        self.Party = None
        self.connection = None
        self.log_level = None
        self.metrics_output = None

        if 'ibmfl' in sys.modules:
            del sys.modules['ibmfl']
        if 'ibmfl.party' in sys.modules:
            del sys.modules['ibmfl.party']
        if 'ibmfl.party.party' in sys.modules:
            del sys.modules['ibmfl.party.party']

        #install the general lib (which is the cloud version)
        module_name = 'ibmfl'
        module_spec = importlib.util.spec_from_file_location(
            module_name, ibmfl_base_module_location + '/py38-tf24-pt17-sk23/ibmfl/__init__.py')
        module = importlib.util.module_from_spec(module_spec)
        sys.modules[module_name] = module
        module_spec.loader.exec_module(module)

        WMLResource.__init__(self, __name__, client)
        self._client = client
        self.auth_token = "Bearer " + self._client.wml_token
        self.project_id = self._client.project_id
        self.log_level = kwargs.get("log_level", "ERROR")

    def start(self):
        self.Party.start()

    def run(self, aggregator_id=None, experiment_id=None, asynchronous=True, verify=True, timeout: int = 60 * 10):
        """
        Connect to a Federated Learning aggregator and run local training.
        Exactly one of aggregator_id and experiment_id must be supplied.  

        **Parameters**

        .. important::
           #. **aggregator_id**:  aggregator identifier\n
              * If aggregator_id is supplied, the party will connect to the given aggregator.\n
              **type**: str\n
           #. **experiment_id**:  experiment identifier\n
              * If experiment_id is supplied, the party will connect to the most recently created aggregator for the experiment.\n
              **type**: str\n
           #. **asynchronous**:\n
              * True  - party starts to run the job in the background and progress can be checked later.\n
              * False - method will wait until training is complete and then print the job status.\n
              **type**: bool\n
           #. **verify**:  verify certificate\n
              **type**: bool\n
           #. **timeout**:  timeout in seconds.\n
              * If the aggregator is not ready within timeout seconds, exit.\n
              **type**: int, or None for no timeout\n


        **Examples**
         >>> party.run( aggregator_id = "69500105-9fd2-4326-ad27-7231aeb37ac8", asynchronous = True, verify = True )
         >>> party.run( experiment_id = "2466fa06-1110-4169-a166-01959adec995", asynchronous = False )

        """
        from ibmfl.exceptions import FLException
        from datetime import datetime
        import time

        timeout_time = None if timeout is None else timeout + time.time()
        if ( experiment_id is None and aggregator_id is None ) or ( experiment_id is not None and aggregator_id is not None ) :
            raise FLException("Exactly one of aggregator_id and experiment_id must be supplied")

        if ( experiment_id is not None ):
            while True: 
                try:
                    details = self._client.training.get_details(get_all=True,training_definition_id=experiment_id)['resources']
                    details = [ d for d in details if d['entity']['status']['state'] in ['accepting_parties','pending','running'] ]
                    if not details :
                        if timeout_time and timeout_time < time.time() :
                            raise FLException("Cannot find an aggregator for experiment %s" % experiment_id)
                        else :
                            logger.info("Cannot find an aggregator for experiment %s . Retrying." % experiment_id)
                            time.sleep(30)
                            continue
                    else :
                        aggregator_id = max( [(t['metadata']['id'],datetime.strptime(t['metadata']['created_at'],'%Y-%m-%dT%H:%M:%S.%fZ'))
                                          for t in details],key=lambda d:d[1])[0]
                        logger.info("Using aggregator id %s" % aggregator_id) 
                        break
                except Exception as ex:
                    logger.exception(ex)
                    raise FLException(str(ex))


        #import the changed files in the desired lib version

        config_dict = self.args.get('config_dict')
        metrics_config = {
            "name": "WMLMetricsRecorder",
            "path": "ibmfl.party.metrics.metrics_recorder",
            "output_file": self.metrics_output,
            "output_type": "json",
            'compute_pre_train_eval': False,
            'compute_post_train_eval': False
        }
        if 'metrics_recorder' not in config_dict:
            config_dict["metrics_recorder"] = metrics_config
        agg_info = config_dict.get('aggregator').get('ip').split('/')[0] + "/ml/v4/trainings/" + aggregator_id
        config_dict['aggregator']['ip'] = agg_info
        self.args['config_dict'] = config_dict

        #check for aggregator state and start job
        try:
            training_status = self._client.training.get_status(aggregator_id)
            state = training_status['state']
            ready = False
            if state == "pending":
                while state == "pending" and ( not timeout_time or timeout_time > time.time() ) :
                    logger.info("Waiting for aggregator accepting parties state..")
                    time.sleep(10)
                    training_status = self._client.training.get_status(aggregator_id)
                    state = training_status['state']
                if state != "accepting_parties":
                    raise FLException("The current state of training %s is %s, so the party is not able to start a job." % (aggregator_id,state))
                ready = True
            elif state == "running" or state == "accepting_parties":
                ready = True
            else:
                raise FLException("The current state of training %s is %s, so the party is not able to start a job." % (aggregator_id,state))

            if ready:
                if "cpd406" in self.module_location or "cloud" in self.module_location:
                    details = self._client.training.get_details(aggregator_id)
                    fl_entity = details["entity"]["federated_learning"]
                    if "software_spec" in fl_entity:
                        software_spec = fl_entity["software_spec"]["name"] if "name" in fl_entity["software_spec"] else fl_entity["software_spec"]["id"]
                    else:
                        software_spec = "default_py3.8"
                    platform_env = choose_software_version(software_spec)
                    print("Loading {} environment..".format(platform_env))
                    self.module_location = '/'.join(self.module_location.split('/')[0:-2]) + self.SUPPORTED_PLATFORMS_MAP.get(platform_env)
                import_diff(self.module_location)
                from ibmfl.party.party import Party
                self.Party = Party(**self.args, token=self.auth_token, self_signed_cert=not verify, log_level=self.log_level)
                self.connection = self.Party.connection
                self.start()
            else:
                raise FLException("The current state of training %s is %s, so the party is not able to start a job." % (aggregator_id,state))
            #wait for the job to finish if synchrounous
            if not asynchronous:
                while "completed" != state and "failed" != state and "canceled" != state and self.is_running():
                    training_status = self._client.training.get_status(aggregator_id)
                    state = training_status['state']
                    time.sleep(10)
                logger.info("The training finishes with %s status" % state)
        except FLException as ex:
            raise FLException(str(ex))
        except Exception as ex:
            logger.info("The party failed to start training")
            logger.exception(ex)

    def monitor_logs(self, log_level="INFO"):
        """
        This method should be called prior to the run() method to
        enable the logs of the training job in the standard output

        **Parameters**

        .. important::
           #. **log_level**:  log level specified by user\n
              **type**: str\n

        **Output**

        .. important::
            **returns**: This method only outputs the logs to stdout\n
            **return type**: None\n

        **Example**
         >>> party.monitor_logs()

        """
        self.log_level = log_level

    def monitor_metrics(self, metrics_file="-"):
        """
        Enable the metrics of the training job in the standard output

        **Parameters**

        .. important::
           #. **metrics_file**:  a filename specified by user for metrics output\n
              **type**: str\n

        **Output**

        .. important::
            **returns**: This method outputs the metrics to stdout if a filename is not specified\n
            **return type**: None\n

        **Example**
         >>> party.monitor_metrics()

        """
        self.metrics_output = metrics_file

    def is_running(self):
        """
        Check if the training job is running

        **Output**

        .. important::
             **returns**: If the job is running\n
             **return type**: bool\n

        **Example**
         >>> party.is_running()

        """
        return not self.connection.stopped

    def get_round(self):  

        """
        Get the current round number

        **Output**

        .. important::
             **returns**: The current round number\n
             **return type**: int\n

        **Example**
         >>> party.get_round()

        """
        return self.Party.proto_handler.metrics_recorder.get_round_no()

    def cancel(self):
        """
        Stop the local connection to the training on the party side

        **Example**
         >>> party.cancel()

        """
        self.Party.stop_connection()
