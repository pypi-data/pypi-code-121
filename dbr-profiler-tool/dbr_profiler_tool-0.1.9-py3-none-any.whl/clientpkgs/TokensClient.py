import os
import logging
from core import logging_utils
from core import wmconstants
from core.dbclient import dbclient

class TokensClient(dbclient):
    def get_tokens_list(self):
        """ 
        Returns an array of json objects for tokens. 
        """
        # fetch all jobsruns
        tokensList = self.get("/token-management/tokens", version='2.0').get('token_infos', [])
        return tokensList


