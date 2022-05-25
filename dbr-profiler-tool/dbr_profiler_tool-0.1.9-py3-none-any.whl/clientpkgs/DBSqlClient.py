import os
import logging
from core import logging_utils
from core import wmconstants
from core.dbclient import dbclient

class DBSqlClient(dbclient):
    def get_sqlendpoint_list(self):
        """ 
        Returns an array of json objects for jobruns. 
        """
        # fetch all jobsruns
        endpointsList = self.get("/sql/endpoints", version='2.0').get('endpoints', [])
        return endpointsList


