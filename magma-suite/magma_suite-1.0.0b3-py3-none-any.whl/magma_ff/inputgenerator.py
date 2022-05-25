#!/usr/bin/env python3

################################################
#
#   InputGenerator ff
#
################################################

################################################
#   Libraries
################################################
import sys, os

# tibanna
from tibanna.utils import create_jobid

# magma
from magma.inputgenerator import InputGenerator as InputGeneratorFromMagma
from magma.inputgenerator import Argument

################################################
#   InputGenerator
################################################
class InputGenerator(InputGeneratorFromMagma):

    def __init__(self, wfl_obj, wflrun_obj):
        super().__init__(wfl_obj, wflrun_obj)

        # Output from ff use file as key
        #      instead of files for file argument value
        self.file_key = 'file'
    #end def

    def input_generator(self, env='env'):
        """Function customized for tibanna and portal interaction.
        Require env as an additional input.

        For each WorkflowRun[obj] ready to run:
            - Update status to 'running'
            - Add a jobid
            - Create specific input as dict
            - Create updated workflow_runs and final_status properties
            - Yield input, {workflow_runs, final_status}

        :param env: Environment to pass to tibanna (e.g. fourfront-cgap)
        :type env: str
        :return: Generator to input for WorkflowRun[obj] and updated
            workflow_runs and final_status information for patching
        :rtype: generator(dict, dict)
        """
        for run_obj, run_args in self._input():
            jobid = create_jobid()
            # Update run status and jobid
            self.wflrun_obj.update_attribute(run_obj.shard_name, 'status', 'running')
            self.wflrun_obj.update_attribute(run_obj.shard_name, 'jobid', jobid)
            ### This is where formatting happens,
            #       to change formatting just change this part
            step_obj = self.wfl_obj.steps[run_obj.name]
            input_json = {
                'app_name': run_obj.name,
                'workflow_uuid': step_obj.workflow,
                'config': self._eval_formula(step_obj.config),
                'parameters': {},
                'input_files': [],
                'jobid': jobid,
                "_tibanna": {
                  "run_type": run_obj.name,
                  "env": env
                }
            }

            ####################################################################
            # This should either come from run_obj or step_obj
            #     at some point add that option and possibly merge the two
            if getattr(step_obj, 'custom_pf_fields', None):
                input_json.setdefault('custom_pf_fields', step_obj.custom_pf_fields)
            #end if
            if getattr(step_obj, 'custom_qc_fields', None):
                input_json.setdefault('custom_qc_fields', step_obj.custom_qc_fields)
            #end if
            ####################################################################

            ####################################################################
            # This should either come from wflrun_obj or wfl_obj
            #     at some point add that option and possibly merge the two
            if getattr(self.wflrun_obj, 'common_fields', None):
                input_json.setdefault('common_fields', self.wflrun_obj.common_fields)
            #end if
            ####################################################################

            for arg_obj in run_args:
                if arg_obj.argument_type == 'parameter':
                    input_json['parameters'].setdefault(arg_obj.argument_name, arg_obj.value)
                else:
                    # Basic argument information
                    arg_ = {
                        'workflow_argument_name': arg_obj.argument_name,
                        'uuid': arg_obj.files
                    }
                    # Additional information
                    if getattr(arg_obj, 'mount', None):
                        arg_.setdefault('mount', arg_obj.mount)
                    #end if
                    if getattr(arg_obj, 'rename', None):
                        rname = arg_obj.rename
                        if isinstance(rname, str) and rname.startswith('formula:'):
                            frmla = rname.split('formula:')[-1]
                            rname = self._value_parameter(frmla, self.wflrun_obj.input)
                        #end if
                        arg_.setdefault('rename', rname)
                    #end if
                    if getattr(arg_obj, 'unzip', None):
                        arg_.setdefault('unzip', arg_obj.unzip)
                    #end if
                    input_json['input_files'].append(arg_)
                #end if
            #end for
            yield input_json, {'final_status':  self.wflrun_obj.update_status(),
                               'workflow_runs': self.wflrun_obj.runs_to_json()}
        #end for
    #end def

#end class
