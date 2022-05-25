#!/usr/bin/env python3

################################################
#
#   Object to update
#       MetaWorkflowRun[json]
#        and WorkflowRun[json]
#
#   Michele Berselli
#   berselli.michele@gmail.com
#
################################################

################################################
#   Libraries
################################################
import sys, os

################################################
#   RunUpdate
################################################
class RunUpdate(object):
    """Class to handle MetaWorkflowRun[obj] and WorkflowRun[obj] updates.
    """

    def __init__(self, wflrun_obj):
        """Constructor method.
        Initialize object and attributes.

        :param wflrun_obj: MetaWorkflowRun[obj] representing a MetaWorkflowRun[json]
        :type wflrun_obj: object
        """
        # Basic attributes
        self.wflrun_obj = wflrun_obj
    #end def

    def reset_steps(self, steps_name):
        """Reset WorkflowRun[obj] corresponding to step in steps_name.

        :param steps_name: List of names for steps that need to be reset
        :type steps_name: list(str)
        :return: Updated workflow_runs and final_status information
        :rtype: dict
        """
        for name in steps_name:
            self.wflrun_obj.reset_step(name)
        #end for
        return {'final_status':  self.wflrun_obj.update_status(),
                'workflow_runs': self.wflrun_obj.runs_to_json()}
    #end def

    def reset_shards(self, shards_name):
        """Reset WorkflowRun[obj] with shard_name in shards_name.

        :param shards_name: List of shard_names for WorkflowRun[obj] that need to be reset
        :type shards_name: list(str)
        :return: Updated workflow_runs and final_status information
        :rtype: dict
        """
        for name in shards_name:
            self.wflrun_obj.reset_shard(name)
        #end for
        return {'final_status':  self.wflrun_obj.update_status(),
                'workflow_runs': self.wflrun_obj.runs_to_json()}
    #end def

    def import_steps(self, wflrun_obj, steps_name, import_input=True):
        """Update current MetaWorkflowRun[obj] information.
        Import and use information from specified wflrun_obj.
        Update WorkflowRun[obj] up to steps specified by steps_name

        :param wflrun_obj: MetaWorkflowRun[obj] to import information from
        :type wflrun_obj: object
        :param steps_name: List of names for steps to import
        :type steps_name: list(str)
        :return: MetaWorkflowRun[json]
        :rtype: dict
        """
        ## Import input
        if import_input:
            self.wflrun_obj.input = wflrun_obj.input
        #end if
        ## Import WorkflowRun objects
        for name in steps_name:
            queue = [] # queue of steps to import
                       #    name step and its dependencies
            # Get workflow-runs corresponding to name step
            for shard_name, run_obj in self.wflrun_obj.runs.items():
                if name == shard_name.split(':')[0]:
                    queue.append(run_obj)
                #end if
            #end for
            # Iterate queue, get dependencies and import workflow-runs
            while queue:
                run_obj = queue.pop(0)
                shard_name = run_obj.shard_name
                dependencies = run_obj.dependencies
                try:
                    self.wflrun_obj.runs[shard_name] = wflrun_obj.runs[shard_name]
                except KeyError as e:
                    # raise ValueError('JSON content error, missing information for workflow-run "{0}"\n'
                    #                     .format(e.args[0]))
                    continue
                #end try
                for dependency in dependencies:
                    queue.append(self.wflrun_obj.runs[dependency])
                #end for
            #end while
        #end for
        # Update final_status
        self.wflrun_obj.update_status()

        return self.wflrun_obj.to_json()
    #end def

#end class
