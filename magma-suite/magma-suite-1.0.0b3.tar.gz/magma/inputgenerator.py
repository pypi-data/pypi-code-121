#!/usr/bin/env python3

################################################
#
#   Object to combine and integrate
#       MetaWorkflow[obj] and MetaWorkflowRun[obj]
#       to generate input for WorfklowRun[obj]
#
#   Michele Berselli
#   berselli.michele@gmail.com
#
################################################

################################################
#   Libraries
################################################
import sys, os
import re

# tibanna
from tibanna.utils import create_jobid

################################################
#   Argument
################################################
class Argument(object):
    """Class to model an argument.
    """

    def __init__(self, input_json):
        """Constructor method.
        Initialize object and attributes.

        :param input_json: Argument in json format
            (e.g. from StepWorkflow[json])
        :type input_json: dict
        """
        # Basic attributes
        for key in input_json:
            setattr(self, key, input_json[key])
        #end for
        # Validate
        self._validate()
        # Calculated attributes
        if not getattr(self, 'source_argument_name', None):
            self.source_argument_name = self.argument_name
        #end if
    #end def

    def _validate(self):
        """
        """
        try:
            getattr(self, 'argument_name')
            getattr(self, 'argument_type')
        except AttributeError as e:
            raise ValueError('JSON validation error, {0}\n'
                                .format(e.args[0]))
        #end try
    #end def

#end class

################################################
#   InputGenerator
################################################
class InputGenerator(object):
    """Class to combine MetaWorkflow[obj] and MetaWorkflowRun[obj].
    Has methods to generate specific input for WorkflowRun[obj] and
    information for patching MetaWorkflowRun[obj].
    """

    def __init__(self, wfl_obj, wflrun_obj):
        """Constructor method.
        Initialize object and attributes.

        :parm wfl_obj: MetaWorkflow[obj] representing a MetaWorkflow[json]
        :type wfl_obj: object
        :parm wflrun_obj: MetaWorkflowRun[obj] representing a MetaWorkflowRun[json]
        :type wflrun_obj: object
        """
        # Basic attributes
        self.wfl_obj = wfl_obj
        self.wflrun_obj = wflrun_obj
        # Key to use to access file value information
        #   in workflow-runs output
        self.file_key = 'files'
    #end def

    def input_generator(self):
        """Template function, can be customized to any specific format.

        For each WorkflowRun[obj] ready to run in MetaWorkflowRun[obj]:
            - Update status to 'running'
            - Add a jobid
            - Create specific input as dict
            - Create updated workflow_runs and final_status properties
            - Yield input, {workflow_runs, final_status}

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
                'name': run_obj.name,
                'workflow': step_obj.workflow,
                'config': self._eval_formula(step_obj.config),
                'parameters': {},
                'input_files': [],
                'jobid': jobid
            }

            for arg_obj in run_args:
                if arg_obj.argument_type == 'parameter':
                    input_json['parameters'].setdefault(arg_obj.argument_name, arg_obj.value)
                else:
                    # Basic argument information
                    arg_ = {
                        'workflow_argument_name': arg_obj.argument_name,
                        'files': arg_obj.files
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

    def _eval_formula(self, dit):
        """Replace formulas in dit with corresponding calculated values.
        Detect formula as "formula:<formula>".

        :param dit: Dictionary to evaluate for formulas
        :type dit: dict
        """
        d_ = {}
        for k, v in dit.items():
            if isinstance(v, str) and v.startswith('formula:'):
                frmla = v.split('formula:')[-1]
                # match parameters
                re_match = re.findall('([a-zA-Z_]+)', frmla)
                # replace parameters
                for s in re_match:
                    try:
                        val = self._value_parameter(s, self.wflrun_obj.input)
                        frmla = frmla.replace(s, str(val))
                    except Exception:
                        pass
                    #end try
                #end for
                v = eval(frmla)
            #end if
            d_.setdefault(k, v)
        #end for
        return d_
    #end def

    def _input(self):
        """
        """
        out_ = []
        # Get workflow-runs that need to be run
        for run_obj in self.wflrun_obj.to_run():
            # Get workflow-run arguments
            run_args = self._run_arguments(run_obj)
            # Match and update workflow-run arguments
            #   file arguments -> files
            #   parameter arguments -> value
            self._match_arguments(run_args, run_obj)
            out_.append((run_obj, run_args))
        #end for
        return out_
    #end def

    def _run_arguments(self, run_obj):
        """
        :param run_obj: WorkflowRun[obj] representing a WorkflowRun[json]
        :type run_obj: object
        """
        run_args = []
        for arg in self.wfl_obj.steps[run_obj.name].input:
            arg_obj = Argument(arg)
            run_args.append(arg_obj)
        #end for
        return run_args
    #end def

    def _match_arguments(self, run_args, run_obj):
        """
        :param run_args: List of Argument objects
        :type run_args: list(object)
        :param run_obj: WorkflowRun[obj] representing a WorkflowRun[json]
        :type run_obj: object
        """
        for arg_obj in run_args:
            is_file = False
            # Check argument type
            if arg_obj.argument_type == 'file':
                is_file = True
                is_match = self._match_argument_file(arg_obj, run_obj)
            else: # is parameter
                is_match = self._match_argument_parameter(arg_obj)
            #end if
            if not is_match:
                raise ValueError('Value error, cannot find a match for argument "{0}"\n'
                                    .format(arg_obj.argument_name))
            #end if
            # Check scatter and input_dimension
            dimension_ = getattr(arg_obj, 'scatter', 0)
            dimension_ += getattr(arg_obj, 'input_dimension', 0)
            # input_dimension is additional dimension used to subset the input argument
            #   when creating the step specific input
            if dimension_:
                shard = map(int, run_obj.shard.split(':'))
                if is_file: in_ = arg_obj.files
                else: in_ = arg_obj.value
                #end if
                for idx in list(shard)[:dimension_]:
                    # [:dimension_] handle multiple scatter in same shard,
                    #   use scatter dimension to subset shard index list
                    in_ = in_[idx]
                #end for
                if is_file: arg_obj.files = in_
                else: arg_obj.value = in_
                #end if
            #end if
        #end for
    #end def

    def _match_argument_file(self, arg_obj, run_obj):
        """
        :param arg_obj: Argument object
        :type arg_obj: object
        :param run_obj: WorkflowRun[obj] representing a WorkflowRun[json]
        :type run_obj: object
        """
        if getattr(arg_obj, 'source', None):
        # Is workflow-run dependency, match to workflow-run output
            file_ = []
            for dependency in run_obj.dependencies:
                if arg_obj.source == dependency.split(':')[0]:
                    for arg in self.wflrun_obj.runs[dependency].output:
                        if arg_obj.source_argument_name == arg['argument_name']:
                            file_.append(arg[self.file_key])
                            break
                        #end if
                    #end for
                #end if
            #end for
            gather = getattr(arg_obj, 'gather', 0)
            gather += getattr(arg_obj, 'extra_dimension', 0)
            # extra_dimension is additional increment to dimension used
            #   when creating the step specific input
            if gather == 1:  # gather 1 dimension
                arg_obj.files = file_
            elif gather > 1:  # gather 2+ dimensions
                arg_obj.files = file_
                for i in range(1, gather):
                    arg_obj.files = [arg_obj.files]
            else:  # no gather
                arg_obj.files = file_[0]
            #end if
            return True
        else:
        # No dependency, match to general argument
            return self._match_general_argument(arg_obj)
        #end if
    #end def

    def _match_argument_parameter(self, arg_obj):
        """
        :param arg_obj: Argument object
        :type arg_obj: object
        """
        if getattr(arg_obj, 'value', None) != None:
            # Is value
            return True
        else:
        # No value, match to general argument
            return self._match_general_argument(arg_obj)
        #end if
    #end def

    def _match_general_argument(self, arg_obj):
        """
        :param arg_obj: Argument object
        :type arg_obj: object
        """
        # Try and match with meta-worfklow-run input
        if self._value(arg_obj, self.wflrun_obj.input):
            return True
        #end if
        # No match, try match to default argument in meta-worfklow
        if self._value(arg_obj, self.wfl_obj.input):
            return True
        #end if
        return False
    #end def

    def _value(self, arg_obj, arg_list):
        """
        :param arg_obj: Argument object
        :type arg_obj: object
        :param arg_list: List of arguments as dictionaries
        :type arg_list: list(dict)
        """
        for arg in arg_list:
            if arg_obj.source_argument_name == arg['argument_name'] and \
               arg_obj.argument_type == arg['argument_type']:
                if arg_obj.argument_type == 'file':
                    arg_obj.files = arg['files']
                else:
                    arg_obj.value = arg['value']
                #end if
                return True
            #end if
        #end for
        return False
    #end def

    def _value_parameter(self, arg_name, arg_list):
        """
        :param arg_name: Name of the argument
        :type arg_name: str
        :param arg_list: List of arguments as dictionaries to match
        :type arg_list: list(dict)
        """
        for arg in arg_list:
            if arg_name == arg['argument_name'] and \
               arg['argument_type'] == 'parameter':
                return arg['value']
            #end if
        #end for
        raise ValueError('Value error, cannot find a match for parameter "{0}"\n'
                            .format(arg_name))
    #end def

#end class
