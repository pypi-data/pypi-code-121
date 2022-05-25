import os
import logging
from core import logging_utils
from core import wmconstants
from core.dbclient import dbclient

class IPAccessClient(dbclient):
    def get_ipaccess_list(self):
        """ 
        Returns an array of json objects for jobruns. 
        """
        # fetch all jobsruns
        endpointsList = self.get("/ip-access-lists", version='2.0').get('ip_access_lists', [])
        return endpointsList


