#!/usr/bin/env python3

################################################
#
#   Library to work with MetaWorkflowRun[obj]
#
#   Implement the template for a generic object
#       and generic methods for status checking
#
################################################

################################################
#   Libraries
################################################
import sys, os

################################################
#   AbstractCheckStatus
################################################
class AbstractCheckStatus(object):
    """Template for CheckStatus class.
    """

    def __init__(self, wflrun_obj):
        """Constructor method.
        Initialize object and attributes.

        :param wflrun_obj: MetaWorkflowRun[obj] representing a MetaWorkflowRun[json]
        :type wflrun_obj: object
        """
        # Basic attributes
        self.wflrun_obj = wflrun_obj

    @property
    def status_map(self):
        """Mapping from get_status output to magma status.
        Set to property so that inherited classes can overwrite it.
        """
        return {
            'pending': 'pending',
            'running': 'running',
            'completed': 'completed',
            'failed' : 'failed'
        }

    def check_running(self): # We can maybe have a flag that switch between tibanna or dcic utils functions
        """
        """
        for run_obj in self.wflrun_obj.running():

            # Check current status from jobid
            status_ = self.get_status(run_obj.jobid)
            status = self.status_map[status_]

            # Update run status no matter what
            self.wflrun_obj.update_attribute(run_obj.shard_name, 'status', status)

            # Get run uuid
            run_uuid = self.get_uuid(run_obj.jobid)

            # Update run uuid regardless of the status
            if run_uuid:  # some failed runs don't have run uuid
                self.wflrun_obj.update_attribute(run_obj.shard_name, 'workflow_run', run_uuid)

            if status == 'completed':

                # Get formatted output
                output = self.get_output(run_obj.jobid)

                # Update output
                if output:
                    self.wflrun_obj.update_attribute(run_obj.shard_name, 'output', output)

            elif status == 'running':
                yield None  # yield None so that it doesn't terminate iteration
                continue
            else:  # failed
                # handle error status - anything to do before yielding the updated json
                self.handle_error(run_obj)
            #end if

            # Return the json to patch workflow_runs for both completed and failed
            #   and keep going so that it can continue updating status for other runs
            yield {'final_status':  self.wflrun_obj.update_status(),
                   'workflow_runs': self.wflrun_obj.runs_to_json()}
        #end for
    #end def

    # Inherited classes could define stuff to do with an error case
    def handle_error(self, run_obj):
        pass

    # Replace them with real functions for getting status or (formatted) output
    def get_status(self, jobid):
        """
        """
        return 'running'

    def get_output(self, jobid):
        """
        """
        return [{'argument_name': 'arg', 'files': 'uuid'}]

    def get_uuid(self, jobid):
        """
        """
        return 'uuid'

#end class
