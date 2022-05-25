import os
import logging
from core import logging_utils
from core import wmconstants
from core.dbclient import dbclient

class ReposClient(dbclient):
    def get_repos_list(self):
        """ 
        Returns an array of json objects for repos
        """
        # fetch all repos list
        reposList = self.get("/repos", version='2.0').get('repos', [])
        return reposList


