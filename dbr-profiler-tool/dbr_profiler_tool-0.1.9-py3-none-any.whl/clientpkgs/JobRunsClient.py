import os
import logging
from core import logging_utils
from core import wmconstants
from core.dbclient import dbclient

class JobRunsClient(dbclient):
    def get_jobruns_list(self):
        """ 
        Returns an array of json objects for jobruns. 
        """
        # fetch all jobsruns
        runsList = self.get("/jobs/runs/list", version='2.0').get('runs', [])
        return runsList


