"""
 This file is part of Pypers.

 Pypers is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 Pypers is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with Pypers.  If not, see <http://www.gnu.org/licenses/>.
 """

import json
import re
import os
import sys
import copy
import glob
import time
from datetime import datetime
from collections import OrderedDict, defaultdict
from pypers.utils import utils as ut
from pypers.utils.utils import import_class
from pypers.core.logger import Logger
from pypers.core.constants import *
from pypers.core.interfaces import db, msgbus


ITERABLE_TYPE = 'input_key_iterable'

STARTUP_CYCLE = 50


class Step(object):
    """
    Base class for any step

    Members:
    - status: current status of the step
    - parameters: dictionary containing the definition of the parameters
                  N.B. The actual values are stored as members
    - meta: dictionary containing the metadata information
    - reqs: job submission requirements
    - cmd_count: counter for distributed step
    """

    # flag to enable local step execution
    spec = {
        "version": None,
        "args": {
            "inputs": [{}],
            "outputs": [{}],
            "params": [{}]
        },
        "requirements": {
        }
    }

    req_spec = {
    }

    base_spec = {}

    tpl_reg = re.compile('{{\s*([^\s\}]+)\s*}}')

    def __init__(self, run_id, collection, step_name, sub_step=None):
        self.bootstrap = STARTUP_CYCLE
        self.status = JOB_STATUS.QUEUED
        self.meta = {
            'pipeline': db.get_db().get_pipeline_config(run_id, collection),
            'step': {},
            'job': {}}
        self.requirements = {}
        self.output_dir = '.'
        self.jobs = OrderedDict()
        self.cmd_count = 0

        self.run_id = run_id
        self.collection = collection
        self.pipeline_type = self.meta['pipeline'].get('type')
        self.is_operation = bool(self.meta['pipeline'].get('is_operation', 'False'))
        self.release = int(self.meta['pipeline'].get('release', '1'))

        if collection and not self.pipeline_type:
            self.pipeline_type = 'brands' if self.collection.endswith('tm') else 'designs'

        self.step_name = step_name
        self.sub_step = sub_step

        self.log = Logger(self.run_id, self.collection, self.step_name,
                          self.sub_step)
        # parse specs and create keys
        self.spec["name"] = self.__module__.replace(
            'pypers.steps.', '').split('.')[-1]
        self.name = self.spec["name"]
        self.__version__ = self.spec['version']
        for k, v in self.spec["args"].items():
            for param in v:
                if param.get('name', None):
                    setattr(self, param['name'], param.get('value', []))

        ut.dict_update(self.requirements,
                       self.spec.get('requirements', {}))
        for k, v in self.requirements.items():
            setattr(self, k, int(v))

    def get_reqs(self, no_default=True):
        """
        Return a dictionary with the list of requirements
        If nodefault is set to True, keys setted to the default value '1'
        are not returned
        """
        reqs = []
        for key in self.req_spec:
            val = getattr(self, key)
            req = copy.deepcopy(self.req_spec[key])
            req['value'] = val
            if (val == 1 and not no_default) or val != 1:
                reqs.append(req)
        return reqs

    def __validate_key_groups(self, key_groups):
        """
        Check if the key_groups are valid
        key_groups mut be in [inputs, outputs, params, requirements]
        """
        spec_groups = {'inputs', 'outputs', 'params', 'requirements'}
        if isinstance(key_groups, str):
            if key_groups not in spec_groups:
                raise Exception("Invalid key_groups %s" % key_groups)
            else:
                return {key_groups}
        elif type(key_groups) in [list, set]:
            key_groups = set(key_groups)
            if not key_groups.issubset(spec_groups):
                raise Exception("%s: Invalid key_groups %s" % (
                    self.name, key_groups))
            else:
                return key_groups
        else:
            raise Exception("Invalid key_groups type %s" % type(key_groups))

    def keys_values(self, key_groups=None, key_filter=None, req_only=False):
        """
        Return dictionary of parameter definitions

        """
        if not key_groups:
            key_groups = {'inputs', 'outputs', 'params', 'requirements'}
        else:
            key_groups = self.__validate_key_groups(key_groups)

        key_vals = {}
        if 'requirements' in key_groups:
            key_groups.remove('requirements')
            key_vals = getattr(self, 'requirements')

        for key_group in key_groups:
            for key_spec in self.keys_specs(key_group):
                if (req_only and 'value' not in key_spec) or (not req_only):
                    if key_filter:
                        for k, v in key_filter.items():
                            if key_spec.get(k, []) == v:
                                key_vals[key_spec["name"]] = getattr(
                                    self, key_spec["name"])
                    else:
                        key_vals[key_spec["name"]] = getattr(
                            self, key_spec["name"])
        return key_vals

    def keys(self, key_groups=None, key_filter=None, req_only=False):
        """
        Return a list of keys defined in the spec
        If req_only is True, then default values are not returned
        """
        if not key_groups:
            key_groups = {'inputs', 'outputs', 'params', 'requirements'}
        else:
            key_groups = self.__validate_key_groups(key_groups)
        keys = []
        for key_group in key_groups:
            for key_spec in self.keys_specs(key_group):
                if (req_only and 'value' not in key_spec) or (not req_only):
                    if key_filter:
                        for k, v in key_filter.items():
                            if key_spec.get(k, []) == v:
                                keys.append(key_spec['name'])
                    else:
                        keys.append(key_spec['name'])
        return keys

    def keys_specs(self, key_groups):
        """
        Returna list with the specification of the keys
        """
        key_groups = self.__validate_key_groups(key_groups)
        keys_specs = []
        if 'requirements' in key_groups:
            key_groups.remove('requirements')
            keys_specs.extend(self.get_reqs())
        for key_group in key_groups:
            keys_specs.extend(self.spec["args"].get(key_group, []))
        return keys_specs

    def key_spec(self, name):
        """
        Return specification of param, input, or output with given name
        """
        ret_val = {}
        for category in ["inputs", "outputs", "params"]:
            for entry in self.spec["args"].get(category, []):
                if entry["name"] == name:
                    ret_val = entry
                    break
        return ret_val

    def validate_config(self, cfg):
        """
        validate a config file
        """
        errors = {}
        required_key = self.keys(['inputs', 'params'], req_only=True)
        for key in required_key:
            if key in cfg:
                key_spec = self.key_spec(key)
                error_msg = Step.validate_value(
                    cfg[key],
                    key_spec.get('type', ''),
                    key_spec.get('name', '')
                )
                if error_msg:
                    errors[key] = error_msg
            else:
                errors[key] = 'missing value'
        return errors

    @classmethod
    def validate_value(cls, pvalue, ptype, pname):
        """
        Check if the value has the right type
        """
        ret_val = ''
        if pvalue == '' and ptype != 'str':
            ret_val = 'missing value'
        elif ptype == 'file':
            if isinstance(pvalue, (list, tuple)):
                for filename in pvalue:
                    if not os.path.exists(filename):
                        ret_val += '%s : no such file\n' % filename
            elif isinstance(pvalue, str):
                if not os.path.exists(pvalue):
                    ret_val = '%s : no such file' % pvalue
            else:
                ret_val = '%s : invalid type, found %s, expected %s' % (
                    pvalue, type(pvalue), 'str or list')
        elif ptype == 'dir' and pname != 'output_dir':
            if isinstance(pvalue, (list, tuple)):
                for dirname in pvalue:
                    if not isinstance(dirname, str):
                        ret_val = '%s : invalid type, found %s, expected %s' % (
                            dirname, type(dirname), 'str')
                    elif not os.path.isdir(dirname):
                        ret_val += '%s : no such directory' % dirname
            elif isinstance(pvalue, str):
                if os.path.isfile(pvalue):
                    with open(pvalue) as fh:
                        for dirname in fh.read().splitlines():
                            if not os.path.isdir(dirname) and dirname:
                                ret_val += '%s : no such directory' % dirname
                elif not os.path.isdir(pvalue):
                    ret_val = '%s : no such directory' % pvalue
            else:
                ret_val = '%s : invalid type, found %s, expected %s' % (
                    pvalue, type(pvalue), 'str or list')
        elif ptype == 'int':
            if not isinstance(pvalue, int):
                ret_val = '%s : invalid type, found %s, expected %s' % (
                    pvalue, type(pvalue), 'int')
        elif ptype == 'float':
            if not isinstance(pvalue, float):
                ret_val = '%s : invalid type, found %s, expected %s' % (
                    pvalue, type(pvalue), 'float')
        return ret_val

    def store_outputs(self):
        """
        Stores the outputs in json format
        # for debug store also the output keys in a output file
        """
        logdata = {'outputs': {}, 'meta': self.meta}
        for key in self.keys('outputs'):
            logdata['outputs'][key] = getattr(self, key)
        output = {
            'status': self.status,
            'results': logdata
        }

        db.get_db().set_step_output(
            self.run_id, self.collection,
            self.step_name, output, sub_step=self.sub_step)
        if self.is_operation and self.status == JOB_STATUS.FAILED:
            collection = self.collection
            if '_' in collection:
                collection = collection.split('_')[-1]
            db.get_operation_db().completed(self.run_id, collection, success=False)

    def distribute(self):
        """
        Submit the step to the scheduler parallelizing the iterable inputs
        """

        self.status = JOB_STATUS.QUEUED
        # initialize the scheduler
        if db.get_db().has_step_config_changed(
                self.run_id, self.collection, self.step_name):
            db.get_db().reset_step_output(
                self.run_id, self.collection, self.step_name)
        elif db.get_db().has_step_run(
                self.run_id, self.collection, self.step_name):
            step_db = db.get_db().get_run_id_config(
                self.run_id, self.collection)['steps_config'][self.step_name]
            if step_db.get(
                    'output', {}).get('status', None) == JOB_STATUS.SUCCEEDED:
                self.log.info(
                    'Skipping step %s: configuration has not been changed' %
                    self.name)
                return len(self.jobs)
        iterables = self.get_iterables()
        if iterables:
            # Step needs to be distributed
            for iterable in iterables:
                # If this is a file, convert it to list from file contents
                iterable_input = self.cfg.get(iterable, [])
                if not isinstance(iterable_input, list) \
                   and os.path.exists(iterable_input):
                    with open(iterable_input) as f:
                        self.cfg[iterable] = f.read().splitlines()
            # copy the config file
            tmpl_cfg = copy.deepcopy(self.cfg)
            for iterable in iterables:
                tmpl_cfg.pop(iterable)
            tmpl_cfg['meta']['pipeline'] = self.cfg['meta']['pipeline']
            tmpl_cfg['meta']['step'] = self.cfg['meta']['step']
            if len(self.cfg[iterables[0]]) == 0:
                self.submit_job(tmpl_cfg)
            for index in range(0, len(self.cfg[iterables[0]])):
                job_cfg = copy.deepcopy(tmpl_cfg)
                # copy the iterable specific to the job
                for iterable in iterables:
                    # permit a null file
                    if iterable in self.cfg and self.cfg[iterable]:
                        job_cfg[iterable] = self.cfg[iterable][index]
                for key, value in self.cfg['meta']['job'].items():
                    job_cfg['meta']['job'][key] = value[index]
                self.submit_job(job_cfg)
        else:
            job_cfg = copy.deepcopy(self.cfg)
            self.submit_job(job_cfg)
        return len(self.jobs)

    def submit_job(self, cfg):
        """
        Submit a job step
        """
        job_cnt = str(len(self.jobs))
        self.log.debug('Configuring step %s %s' % (cfg['name'], job_cnt))
        cfg['output_dir'] = os.path.join(cfg["output_dir"], job_cnt)
        keys_to_save_on_disk = cfg.get('values_on_disk', [])
        db.get_db().create_step_config(
            self.run_id, self.collection, self.step_name, cfg, keys_to_save_on_disk, sub_step=job_cnt)
        job = Step.load_step(self.run_id, self.collection, self.step_name,
                             sub_step=job_cnt)
        job.status = JOB_STATUS.QUEUED

        if db.get_db().has_step_config_changed(
                self.run_id, self.collection, self.step_name, sub_step=job_cnt):
            db.get_db().reset_step_output(
                self.run_id, self.collection, self.step_name, sub_step=job_cnt)
        elif db.get_db().has_step_run(
                self.run_id, self.collection, self.step_name, sub_step=job_cnt):
            step_db = db.get_db().get_run_id_config(self.run_id, self.collection)
            step_db = step_db['steps_config'][self.step_name]['sub_steps'][job_cnt]
            job.status = step_db.get('output', {}).get('status', None)
        if job.status == JOB_STATUS.SUCCEEDED:
            self.log.info('Job %s in %s already completed: skipping' % (
                cfg['name'], cfg['output_dir']))
            job_id = job_cnt
        else:
            msgbus.get_msg_bus().send_message(self.run_id, self.collection,
                                              self.step_name, job_cnt)
            job_id = job_cnt
        job.job_id = job_id
        self.jobs[job_id] = job

    def get_status(self):
        """
        Return step and jobs status
        """
        running = False
        failed = False
        interrupted = False
        succeeded = True

        if self.bootstrap:
            self.bootstrap -= 1

        if not self.bootstrap:
            if self.status != JOB_STATUS.SUCCEEDED:
                time.sleep(2)
        step_db = db.get_db().get_run_id_config(self.run_id, self.collection)
        jobs_db_state = step_db.get(
            'steps_config', {}).get(self.step_name, {}).get('sub_steps', {})
        incomplete_jobs = [key for key in jobs_db_state.keys()
                           if jobs_db_state[key].get('status', None) != JOB_STATUS.SUCCEEDED]
        if incomplete_jobs:
            for job_id in incomplete_jobs:
                job_done = db.get_db().has_step_run(
                    self.run_id,
                    self.collection,
                    self.step_name,
                    sub_step=job_id)
                if not job_done:
                    job_status = JOB_STATUS.RUNNING
                else:
                    tmp = step_db[
                        'steps_config'][self.step_name]['sub_steps'][job_id]
                    job_status = tmp.get('output', {}).get('status', None)
                running |= (job_status == JOB_STATUS.RUNNING)
                failed |= (job_status == JOB_STATUS.FAILED)
                interrupted |= (job_status == JOB_STATUS.INTERRUPTED)
                succeeded &= (job_status == JOB_STATUS.SUCCEEDED)

                if job_status != JOB_STATUS.RUNNING:
                    running |= not job_done
        if failed:
            self.status = JOB_STATUS.FAILED
        elif interrupted:
            self.status = JOB_STATUS.INTERRUPTED
        elif running:
            self.status = JOB_STATUS.RUNNING
        elif succeeded:
            self.status = JOB_STATUS.SUCCEEDED
        if self.status == JOB_STATUS.SUCCEEDED:
            res = self.fetch_results()
            while not res:
                time.sleep(0.1)
                res = self.fetch_results()
            self.store_outputs()
        return self.status, [self.jobs[idx].__dict__.copy()
                             for idx in self.jobs]

    def fetch_results(self):
        """
        Load the output of each job and merge them
        """

        # check if stepobj has been already loaded
        outputs_val = defaultdict(list)
        outputs_meta = {'pipeline': {}, 'step': {}, 'job': {}}
        # self.log.debug('Loading jobs outputs for step %s...' % self.name)
        db_state = db.get_db().get_run_id_config(self.run_id, self.collection)
        jobs_db_state = db_state.get(
            'steps_config', {}).get(self.step_name, {}).get('sub_steps', {})
        sorted_jobs_id = []
        for job_id in jobs_db_state.keys():
            # Wait until all the jobs finish
            job = jobs_db_state[job_id]
            sorted_jobs_id.append(int(job_id))
            job_output = job['output'].get('results', None)
            if job_output is None:
                return False
        for job_id in sorted(sorted_jobs_id):
            job = jobs_db_state[str(job_id)]
            job_output = job['output'].get('results', None)
            outputs_meta['pipeline'] = job_output['meta']['pipeline']
            outputs_meta['step'] = job_output['meta']['step']
            for param in self.keys('outputs'):
                outputs_val[param].extend(
                    job_output['outputs'].get(param, []))
            for key, value in job_output['meta']['job'].items():
                if key in outputs_meta['job']:
                    if not isinstance(outputs_meta['job'][key], list):
                        outputs_meta['job'][key] = [outputs_meta['job'][key]]
                    outputs_meta['job'][key].append(value)
                else:
                    if self.get_iterables():
                        outputs_meta['job'][key] = [value]
                    else:
                        outputs_meta['job'][key] = value

        for key in self.keys('outputs'):
            setattr(self, key, outputs_val[key])
        self.meta = outputs_meta
        return True

    def get_url(self):
        """
        Return the spec url
        """
        url = self.spec.get('url')
        if url and not url.startswith('http'):
            url = 'http://'+url
        return url

    def get_iterables(self):
        """
        Return the names of the iterable inputs, if any, or an empty list.
        """
        iterables = []
        base_specs_inputs = self.base_spec.get('args', {}).get('inputs', {})
        base_input = [b['name'] for b in base_specs_inputs]
        for input in self.spec["args"]["inputs"]:
            if input['name'] in base_input:
                if self.cfg and not self.cfg.get(input['name']):
                    continue
            if input.get('iterable', False):
                iterables.append(input["name"])
        return iterables

    def print_params(self):
        """
        Pretty-print all parameters
        """
        self.log.info(json.dumps(self.spec, sort_keys=True, indent=4))

    def set_status(self, status):
        """
        Update the status and time data
        """
        if self.status != status:
            if status == JOB_STATUS.RUNNING:
                self.running_at = datetime.utcnow()
            elif status == JOB_STATUS.SUCCEEDED or status == JOB_STATUS.FAILED:
                self.completed_at = datetime.utcnow()
            self.status = status

    def run(self):
        """
        Pre-process, process and post-process.
        This is the routine called to actually run any step.
        """
        raise NotImplementedError()

    def set_outputs(self):
        """
        Set the output to a absolute paths and also check if they exists
        """

        # Outputs: convert relative to absolute paths and make sure it's a list
        for key in self.keys('outputs'):
            value = getattr(self, key)
            # convert all the outputs to list objects
            is_file_type = self.key_spec(key).get("type") == 'file'
            if type(value) != list:
                if "*" in value and isinstance(
                        value, str) and is_file_type:
                    val = [os.path.join(self.output_dir, f)
                           for f in glob.glob(value)]
                    if not val:
                        raise Exception(
                            '%s error: reg ex %s does not match any file in '
                            'the output directory' % (key, value))
                    else:
                        setattr(self, key, val)
                else:
                    setattr(self, key, [value])

            abs_outputs = []
            if is_file_type:
                value = getattr(self, key)
                if isinstance(value, str):
                    value = [value]
                if isinstance(value, (list, tuple)):
                    for filename in value:
                        # chech the value exists
                        if self.key_spec(key).get("required", True):
                            if not os.path.exists(filename):
                                raise Exception('File not found: %s' % filename)

                        # convert relative path to absolute path
                        if not os.path.isabs(filename):
                            abs_outputs.append(os.path.normpath(
                                os.path.join(self.output_dir, filename)))
                        else:
                            abs_outputs.append(filename)

                setattr(self, key, abs_outputs)

    def prestart(self):
        """
        Run before the job manager starts splitting into distributed steps.
        """
        pass

    def preprocess(self):
        """
        Pre-process hook: to be run just before process
        """
        pass

    def postprocess(self):
        """
        Post-process hook: to be run just after process
        """
        pass

    @staticmethod
    def import_class(step_name):
        """
        Import and return the step class
        """

        class_name = ''
        try:
            # try to load the step from local
            class_name = import_class(step_name)
        except Exception:
            # try to load the step from step library
            if not step_name.startswith('pypers.steps.'):
                step_name = 'pypers.steps.' + step_name
            class_name = import_class(step_name)
        return class_name

    @classmethod
    def create(cls, step_name, run_id=None, collection=None, name=None,
               sub_step=None):
        """
        Create a step object from the step name
        """
        if type(step_name) == type:
            class_name = step_name
        else:
            class_name = cls.import_class(step_name)
        return class_name(run_id, collection, name, sub_step=sub_step)

    @classmethod
    def load_cfg(cls, cfg):
        """
        Load and return the step configuration
        """
        try:
            if type(cfg) == dict:
                cfg_data = copy.deepcopy(cfg)
            else:
                if os.path.exists(cfg):
                    with open(cfg) as fh:
                        cfg_data = json.load(fh)
                else:
                    cfg_data = json.load(cfg)
        except Exception as error:
            raise Exception("Unable to load step cfg %s: %s" % (cfg, error))
        else:
            return cfg_data

    @classmethod
    def load_step(cls, run_id, collection, step_name, sub_step=None):
        """
        Load a the step configuration and instanciate a step
        """
        cfg = db.get_db().get_step_config(
            run_id, collection, step_name, sub_step=sub_step)
        cfg_data = cls.load_cfg(cfg)
        if 'sys_path' in cfg_data:
            sys.path.insert(0, cfg_data['sys_path'])
        else:
            sys.path.insert(0, os.getcwd())
        try:
            step = cls.create(cfg_data.get('step_class', ''),
                              run_id, collection, step_name, sub_step=sub_step)
            for key in cfg_data:
                if key in step.requirements:
                    # cast memory and cpus to int since they are not validated
                    setattr(step, key, int(cfg_data[key]))
                    step.requirements[key] = int(cfg_data[key])
                else:
                    setattr(step, key, cfg_data[key])
            if 'name' not in cfg_data:
                step.name = cfg_data.get('step_class', '').rsplit(".", 1)[1]
        except Exception:
            raise Exception("Unable to load step class %s " % (
                cfg_data.get('step_class', '')))
        else:
            del sys.path[0]
            step.cfg = cfg_data
            return step

    def configure_params(self):
        """
        Configure the templated parameters, if any

        Note that it treats replacement by a file parameter in a special way.
        E.g., if input_file is defined as '/foo/bla.txt', {{input_file}} will
        be replace by the raw basename, without extension, of input_file:
        {{input_file}} => 'bla'
        """
        for category in ["inputs", "outputs", "params"]:
            for entry in self.spec["args"].get(category, []):
                # Loop over all entries of all categories of parameters
                name = entry["name"]
                value = getattr(self, name)
                if value and isinstance(value, str):
                    matches = self.tpl_reg.findall(value)
                    for match in matches:  # value is templated
                        subst_val = getattr(self, match)
                        # If this is a list, take the first element
                        if type(subst_val) is list:
                            subst_val = str(subst_val[0])
                        else:
                            subst_val = str(subst_val)
                        # If this is a file, take the bare file name
                        if self.key_spec(match).get("type") in ['file']:
                            subst_val = os.path.basename(
                                subst_val).split('.')[0]
                        if subst_val:
                            newval = re.sub('{{\s*' + match + '\s*}}',
                                            subst_val,
                                            value)
                            setattr(self, name, newval)
                            value = newval
                        else:
                            raise Exception(
                                "Couldn't replace parameter %s: "
                                "%s not found" % (entry, match))


class FunctionStep(Step):

    def __init__(self, *args, **kwargs):
        # Call the base class' initialization
        super(FunctionStep, self).__init__(*args, **kwargs)

    def run(self):
        try:
            self.status = JOB_STATUS.RUNNING
            self.store_outputs()
            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir, 0o775)
            self.configure_params()
            self.preprocess()
            self.process()
            self.postprocess()
            self.status = JOB_STATUS.SUCCEEDED
            self.store_outputs()
            self.log.info("Step %s - %s run completed" % (self.step_name, self.sub_step))

        except Exception as e:
            self.status = JOB_STATUS.FAILED
            self.store_outputs()
            raise e


base_classes = [Step, FunctionStep]
