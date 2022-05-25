import os
import logging
from core import logging_utils
from core import wmconstants
from core.dbclient import dbclient

class PoolsClient(dbclient):
    def get_pools_list(self):
        """ 
        Returns an array of json objects for poolslist
        """
        # fetch all poolslist
        poolsList = self.get("/instance-pools/list", version='2.0').get('instance_pools', [])
        return poolsList


