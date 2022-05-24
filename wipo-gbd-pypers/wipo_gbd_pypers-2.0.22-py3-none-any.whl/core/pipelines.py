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
import os
import sys
import networkx as nx
import datetime
import copy
from pypers.core.interfaces import db, msgbus
from collections import defaultdict

from pypers.core.logger import Logger
from pypers.core.step import Step
from pypers.core.constants import *
from pypers.utils import utils as ut
from pypers.pipelines import pipeline_names


class Pipeline(Step):
    """
    Pipeline object: takes care of the execution of a whole pipeline
    """

    __version__ = "$Format:%H$"

    params = [
        {
            "type": "str",
            "name": "project_name",
            "descr": "the project name (will be displayed in the run list)"
        },
        {
            "type": "str",
            "name": "description",
            "descr": "description of the pipeline "
                     "(will be displayed in the run list)"
        },
        {
            "type": "dir",
            "name": "output_dir",
            "descr": "output directory"
        }
    ]

    def _get_value_or_empty(self, cfg, key, default=''):
        res = cfg.get(key, default)
        if res is None:
            res = default
        return res

    def __init__(self, cfg, user='Unknown', reset_logs=False):
        """
        Read in the pipeline graph and load the configuration.
        """
        self.all_ok = True
        self.user = user
        self.status = JOB_STATUS.QUEUED

        self.completed = []
        self.running = {}
        self.outputs = {}

        try:
            self.cfg = Pipeline.load_cfg(cfg)
        except Exception as e1:
            raise Exception('Failed to load config (error=%s). ' % e1)

        self.name = self.cfg['name']
        self.label = self.cfg['label']

        self.output_dir = self._get_value_or_empty(
            self.cfg['config']['pipeline'], 'output_dir', '')

        self.collection = self.cfg['config']['pipeline']['collection']
        self.pipeline_type = self.cfg['config']['pipeline'].get('type')
        if not self.pipeline_type:
            self.pipeline_type = 'brands' if self.collection.endswith('tm') else 'designs'
        self.is_operation = self.cfg['config']['pipeline'].get('is_operation', 'False') == 'True'
        self.notify = self.cfg['config']['pipeline'].get('notify', None)

        self.ordered = Pipeline.ordered_steps(self.cfg)

        self.run_id = (self.cfg.get('run_id') or
                       self.cfg['config']['pipeline'].get('run_id') or
                       datetime.datetime.today().strftime('%Y%m%d.%H%M'))
        self.cfg['run_id'] = self.run_id

        self.sys_path = self.cfg.get('sys_path')
        if self.sys_path:
            sys.path.insert(0, self.sys_path)

        self.dag = self.create_dag(self.cfg)

        # setting output_dir
        self.output_dir = os.path.join(self.output_dir,
                                       self.name)
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        self.meta = {
            'pipeline': {
                'input': {}
            },
            'steps': {},
            'job': {}
        }
        self.meta['pipeline']['run_id'] = self.run_id
        self.meta['pipeline']['output_dir'] = self.output_dir
        self.meta['pipeline']['collection'] = self.collection
        self.meta['pipeline']['dag_name'] = self.name
        self.meta['pipeline']['pipeline_type'] = self.pipeline_type
        self.meta['pipeline']['is_operation'] = self.is_operation


        pipeline_input = self.cfg['config'].get('pipeline', {}).get('input')
        if pipeline_input:
            self.meta['pipeline']['input'] = pipeline_input

        # Use default output dir under /scratch/cgi/nespipe
        # (linked to user-defined dir.)
        # if: a) this run is using the db (so we have a run ID);
        #     b) it is not a demux. run;
        # and c) the user-defined directory is not already under /scratch
        self.work_dir = self.output_dir

        # Setup the logger

        self.log = Logger(self.run_id, self.collection, None, None)
        self.log.debug('Output directories: output_dir=%s, work_dir=%s' % (
            self.output_dir, self.work_dir), reset=reset_logs)

        # Get running steps form db
        for step_name in db.get_db().get_running_steps(self.run_id, self.collection):
            # If substep
            if '_' in step_name:
                continue
            self.running[step_name] = Step.load_step(
                self.run_id, self.collection, step_name)

    @staticmethod
    def create_dag(cfg):
        """
        Create and return a dag object
        """
        dag = nx.DiGraph()
        if cfg.get('inputs', ''):
            dag.add_node('inputs', class_name="")
        for step in cfg['dag']['nodes']:
            dag.add_node(step, class_name=cfg['dag']['nodes'][step])
        for edge in cfg['dag']['edges']:
            dag.add_edge(edge['from'], edge['to'], **edge)
        return dag

    @classmethod
    def validate_config(cls, cfg, user):
        """
        Check if all the config params are ok
        """

        retval = defaultdict(dict)
        s_errors = defaultdict(dict)

        cfg = cls.load_cfg(cfg)
        params = cls.get_params(cfg)
        unb_inputs = cls.get_unbound_inputs(cfg)

        # validate step section
        for stepname in params['steps']:
            if stepname is not 'inputs':
                classname = cfg['dag']['nodes'][stepname]
                stepobj = Step.create(classname)
                if stepname in cfg['config']['steps']:
                    required_keys = []
                    required_keys.extend(unb_inputs.get(stepname, []))
                    required_keys.extend(stepobj.keys(['params'],
                                                      req_only=True))
                    stepcfg = cfg['config']['steps'][stepname]
                    for key in required_keys:
                        if key in stepcfg:
                            param_spec = stepobj.key_spec(key)
                            error_msg = stepobj.validate_value(
                                stepcfg[key], param_spec['type'],
                                param_spec['name'])
                            if error_msg:
                                s_errors[stepname][key] = error_msg
                        else:
                            s_errors[stepname][key] = 'missing value'
                else:
                    for key in stepobj.keys(['params'], req_only=True):
                        s_errors[stepname][key] = 'missing value'
                    if stepname in unb_inputs:
                        for key in unb_inputs[stepname]:
                            s_errors[stepname][key] = 'missing value'

        # validate pipeline section
        p_errors = {}
        if not cfg['config']['pipeline']['project_name']:
            p_errors['project_name'] = 'missing value'

        if not cfg['config']['pipeline']['description']:
            p_errors['description'] = 'missing value'

        if not cfg['config']['pipeline']['output_dir']:
            p_errors['output_dir'] = 'missing value'
        else:
            output_dir = cfg['config']['pipeline']['output_dir']
            if not isinstance(output_dir, str):
                p_errors['output_dir'] = '%s : invalid type, found %s, ' \
                                         'expected %s' % (output_dir,
                                                          type(output_dir),
                                                          'str')
            elif not output_dir.startswith('/'):
                p_errors['output_dir'] = '%s : not an absolute path' % \
                                         output_dir

        if s_errors:
            retval['steps'] = s_errors

        if p_errors:
            retval['pipeline'] = p_errors

        return retval

    @classmethod
    def get_unbound_inputs(cls, cfg):
        """
        Get the unbound inputs
        """

        cfg = cls.load_cfg(cfg)
        dag = cls.create_dag(cfg)

        # Step parameters
        uinputs = defaultdict(dict)
        for stepname, classname in cfg['dag']['nodes'].items():
            step = Step.create(classname)
            input_keys = step.keys('inputs', req_only=True)
            if input_keys:
                for pred in dag.predecessors(stepname):
                    # Remove any key that is already bound
                    for binding in dag[pred][stepname].get('bindings', []):
                        key = binding.split('.')[1]
                        # maybe it has been already removed
                        if key in input_keys:
                            input_keys.remove(key)
                if input_keys:
                    uinputs[stepname] = input_keys
        return uinputs

    @staticmethod
    def create_steps(cfg):
        stepobjs = {}
        if 'sys_path' in cfg:
            sys.path.insert(0, cfg['sys_path'])
        for stepname, classname in cfg['dag']['nodes'].items():
            stepobjs[stepname] = Step.create(classname)
        if 'sys_path' in cfg:
            del sys.path[0]
        return stepobjs

    @classmethod
    def get_params(cls, cfg):
        """
        Return the list of required parameters for all the configurable
        steps in the pipeline.
        Parses the config file to look for all step parameters as well as
        unconnected input keys.
        """
        cfg = cls.load_cfg(cfg)
        # Step parameters
        params = defaultdict(dict)
        params['steps'] = defaultdict(dict)
        params['pipeline'] = defaultdict(dict)
        params['steps_order'] = list(nx.topological_sort(cls.create_dag(cfg)))

        # create all the steps objects
        stepobjs = Pipeline.create_steps(cfg)

        # get the configuration of the steps
        steps_config = {}

        if cfg.get('config', {}).get('steps', {}):
            steps_config = copy.deepcopy(cfg['config']['steps'])

        # add the parameters and unbound inputs
        for stepname in stepobjs:
            params['steps'][stepname]['descr'] = stepobjs[stepname].spec.get(
                'descr')
            params['steps'][stepname]['url'] = stepobjs[stepname].get_url()
            step_params = stepobjs[stepname].keys_specs(['params',
                                                         'requirements'])
            if step_params:
                params['steps'][stepname]["params"] = copy.deepcopy(step_params)
                if stepname in steps_config:
                    for key in steps_config[stepname]:
                        for i, param in enumerate(
                                params['steps'][stepname]["params"]):
                            if param['name'] == key:
                                params['steps'][stepname][
                                    "params"][i]['value'] = copy.deepcopy(
                                    steps_config[stepname][key])
        if cfg.get('inputs', ''):
            params['steps']['inputs'] = {}
            params['steps']['inputs']['descr'] = [
                "Dispatch inputs to subsequent steps"]
            params['steps']['inputs']['inputs'] = cfg.get('inputs', '')

        # get unbound inputs
        steps_inputs = cls.get_unbound_inputs(cfg)

        for stepname in steps_inputs:
            params['steps'][stepname]['inputs'] = []
            for input_key in steps_inputs[stepname]:
                inputspec = copy.deepcopy(stepobjs[stepname].key_spec(
                    input_key))
                # overwrite the value with the value set in the config section
                cfg_value = steps_config.get(stepname, {}).get(input_key, {})
                if cfg_value:
                    inputspec['value'] = cfg_value
                params['steps'][stepname]['inputs'].append(inputspec)

        # Mandatory pipeline parameters
        params['pipeline']['params'] = cls.params

        return dict(params)

    @classmethod
    def ordered_steps(cls, cfg):
        """
        Return ordered steps from config
        """
        return list(nx.topological_sort(cls.create_dag(cfg)))

    @classmethod
    def load_cfg_from_db(cls, pipeline_name):
        db_connector = db.get_db_config()
        config_db = db_connector.get_configuration(pipeline_name)
        config_db['config']['pipeline']['collection'] = pipeline_name
        return Pipeline.load_cfg(config_db)

    @classmethod
    def load_cfg(cls, cfg):
        """
        Return the json cfg
        Is expecting as input one between a file, a json text or a dictionary
        """
        cfg_load = None
        try:
            if type(cfg) == dict:
                cfg_load = copy.deepcopy(cfg)
            elif isinstance(cfg, str):
                if os.path.exists(cfg):
                    with open(cfg) as fh:
                        cfg_load = json.load(fh)
                        if 'sys_path' not in cfg_load:
                            cfg_load['sys_path'] = os.path.dirname(
                                os.path.realpath(cfg))
                else:
                    cfg_load = json.load(cfg)
        except Exception as e:
            raise Exception("Unable to load config file %s: %s" % (cfg, e))
        else:
            # load the spec_type or spec_file into the json_spec
            # if they exists
            cfg_data = {
                'config': {
                    'steps': {},
                    'pipeline': {
                        'project_name': '',
                        'description': '',
                        'output_dir': ''
                    }
                }
            }
            ut.dict_update(cfg_data, cfg_load)

            if 'sys_path' in cfg_data:
                sys.path.insert(0, cfg_data['sys_path'])

            pipeline_to_load = cfg_data['dag'].pop(
                "load") if "load" in cfg_data['dag'] else None
            if pipeline_to_load:
                try:
                    if os.path.exists(pipeline_to_load):
                        spec_file = pipeline_to_load
                    else:
                        if pipeline_to_load in pipeline_names:
                            spec_file = pipeline_names[pipeline_to_load]
                        else:
                            raise Exception("Pipeline %s not found in list of "
                                            "pipelines: [%s]" %
                                            (pipeline_to_load,
                                             ','.join(pipeline_names)))
                    with open(spec_file) as fh:
                        spec = json.load(fh)
                        stepobjs = Pipeline.create_steps(spec)
                        steps_defaults = {}
                        for step in stepobjs:
                            step_default = stepobjs[step].keys_values(
                                ['params', 'requirements'])
                            if step_default:
                                steps_defaults[step] = step_default

                        spec.setdefault('config', {})
                        spec['config'].setdefault('pipeline', {})
                        spec['config'].setdefault('steps', {})
                        ut.dict_update(spec['config']['steps'],
                                       steps_defaults, replace=False)
                        ut.dict_update(spec['config'],
                                       cfg_data.get('config', ''))
                        cfg_data = spec
                except Exception as e:
                    raise e
            if 'sys_path' in cfg_data:
                del sys.path[0]
            return cfg_data

    def get_next_steps(self):
        """
        Get the list of steps that are ready to run
        """
        next_steps = set()
        for node in self.ordered:
            if node not in self.completed and node not in self.running:
                ready = True
                for parent in self.dag.predecessors(node):
                    if parent not in self.completed or parent in self.running:
                        ready = False
                if ready:
                    next_steps.add(node)

        if len(next_steps) > 0:
            self.log.debug('Next steps to run: [%s]' % ','.join(next_steps))
        return next_steps

    def run_step(self, step_name):
        """
        Configure and run a job for the given step
        """
        # skip the input step
        if step_name == 'inputs':
            self.completed.append(step_name)
            self.outputs[step_name] = self.cfg['config']['steps'].get(
                step_name, {})
            self.outputs[step_name]['output_dir'] = ''
        else:
            step_config = {
                'meta': {
                    'pipeline': {},
                    'step': {},
                    'job': {}
                }}
            ut.dict_update(step_config['meta']['pipeline'],
                           self.meta['pipeline'])
            step_class = self.dag.nodes[step_name]['class_name']
            step_config['name'] = step_name
            step_config['sys_path'] = self.sys_path
            step_config['step_class'] = step_class
            step_config['output_dir'] = os.path.join(self.work_dir,
                                                     step_name)
            step_config['pipeline_type'] = self.pipeline_type
            keys_to_save_on_disk = set()
            # 1. Form input keys
            # Remember: edges are labelled by 'from' keys
            for pred in self.dag.predecessors(step_name):
                edge = self.dag[pred][step_name]
                # Not an actual loop: just get key/value
                for bind_to, bind_from in edge.get('bindings',
                                                   {}).items():
                    to_key = bind_to.split('.')[1]
                    keys_to_save_on_disk.add(to_key)
                    if isinstance(bind_from, list):
                        for from_key in bind_from:
                            key = from_key.split('.')[1]
                            out = self.outputs[pred][key]
                            if to_key in step_config:
                                if isinstance(step_config[to_key],
                                              str):
                                    step_config[to_key] = [
                                        step_config[to_key]]
                                step_config[to_key].extend(out)
                            else:
                                step_config[to_key] = out
                    else:
                        from_key = bind_from.split('.')[1]
                        out = self.outputs[pred][from_key]
                        if to_key in step_config:
                            if isinstance(step_config[to_key], str):
                                step_config[to_key] = [step_config[to_key]]
                            step_config[to_key].extend(out)
                        else:
                            step_config[to_key] = out

                # Transfer metadata of previous step to next step
                for key in self.meta['steps'].get(pred, {}):
                    step_config['meta'][key] = self.meta['steps'][pred][key]
            # 2. Form step config.
            ut.dict_update(step_config,
                           self.cfg['config']['steps'].get(step_name, {}),
                           replace=False)
            self.update_metadata(step_name, step_config[KEY_META])
            db.get_db().create_step_config(
                self.run_id, self.collection, step_name, step_config,
                list(keys_to_save_on_disk))
            # 3. Submit step
            self.log.info('Executing step %s' % str(step_name))
            self.running[step_name] = Step.load_step(
                self.run_id, self.collection, step_name)
            self.running[step_name].distribute()

    def update_metadata(self, step_name, step_meta):
        """
        Store step metadata (if any) and pull out global metadata from it
        """
        self.meta['steps'][step_name] = step_meta
        if 'pipeline' in step_meta:
            ut.dict_update(self.meta['pipeline'], step_meta['pipeline'])

    def update_status(self):
        """
        Update list of completed jobs
        """
        for step_name in copy.copy(self.running):
            step_status, jobs_status = self.running[step_name].get_status()
            if self.status == JOB_STATUS.QUEUED and \
                    step_status == JOB_STATUS.RUNNING:
                self.status = JOB_STATUS.RUNNING
            if step_status == JOB_STATUS.SUCCEEDED:
                if step_name not in self.completed:
                    self.completed.append(step_name)
                self.log.info("Step %s completed" % step_name)
                self.outputs[step_name] = self.running[step_name].keys_values(
                    'outputs')
                self.outputs[step_name]['output_dir'] = self.running[
                    step_name].output_dir
                self.update_metadata(step_name, self.running[step_name].meta)
                self.running.pop(step_name)
                self.log.debug('Completed jobs: (%s)' % ','.join(self.completed))
            elif step_status == JOB_STATUS.FAILED:
                self.log.error('Step %s failed' % step_name)
                self.log.error('+++ Stopping pipeline %s +++' % self.name)
                self.status = JOB_STATUS.FAILED
                self.all_ok = False
            elif step_status == JOB_STATUS.INTERRUPTED:
                self.log.error('Step %s interrupted' % step_name)
                self.log.error('+++ Stopping pipeline %s +++' % self.name)
                self.status = JOB_STATUS.INTERRUPTED
                self.all_ok = False


    def load_completed(self, restart=False):
        cfg = db.get_db().get_run_id_config(self.run_id, self.collection)
        if not cfg or restart:
            self.log.debug('Saving configuration to db')
            db.get_db().create_new_run_for_pipeline(
                self.run_id, self.collection, self.cfg)
            cfg = db.get_db().get_run_id_config(self.run_id, self.collection)
        for step_name, step in cfg.get('steps_config', {}).items():
            if step.get('output', {}).get('status', None) == 'SUCCEEDED':
                if step_name not in self.completed:
                    self.completed.append(step_name)
                self.outputs[step_name] = step.get(
                    'output', {}).get(
                    'results', {}).get('outputs', {})
                self.outputs[step_name]['output_dir'] = step.get(
                    'output', {}).get(
                    'results', {}).get(
                    'meta', {}).get(
                    'pipeline', {}).get(
                    'output_dir', '')
                self.update_metadata(step_name, step.get(
                    'output', {}).get(
                    'results', {}).get('meta', {}))
        self.update_status()

    def _has_payload(self, root):
        to_return = False
        if isinstance(root, dict):
            for key in root.keys():
                to_return = to_return or self._has_payload(root[key])
        elif isinstance(root, list):
            for key in root:
                to_return = to_return or self._has_payload(key)
        elif root:
            to_return = True
        return to_return

    def parse_next(self, restart_step=False):
        if self.all_ok:  # because update_status takes time...
            if (len(self.dag.nodes()) - len(self.completed)) > 0:
                should_stop = len(self.completed) > 0
                for step_name in self.completed:
                    has_payload = False
                    for key in self.outputs[step_name].keys():
                        if key not in ['output_dir']:
                            has_payload = has_payload or self._has_payload(self.outputs[step_name][key])
                    if step_name in self.running:
                        has_payload = True
                    should_stop = should_stop and not(has_payload)
                if should_stop:
                    self.log.info('+++ Pipeline %s completed +++' % self.name)
                    self.status = JOB_STATUS.SUCCEEDED
                    return
                for step_name in self.get_next_steps():
                    msgbus.get_msg_bus().send_message(self.run_id,
                                                      self.collection,
                                                      step_name,
                                                      restart_step=restart_step)
            else:
                self.log.info('+++ Pipeline %s completed +++' % self.name)
                self.status = JOB_STATUS.SUCCEEDED
        else:
            self.log.error('+++ Pipeline %s Error +++' % self.name)
            sys.exit(1)

    def run(self, verbose=False, restart=False):
        """
        Run a node of the pipeline
        If the pipeline is completed return False otherwise True
        """
        # Store config file and log some information
        self.load_completed(restart=restart)
        self.parse_next(restart_step=True)

