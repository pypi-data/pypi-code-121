import logging
import os
import json
from core import logging_utils
from core import wmconstants
from core.dbclient import dbclient

class ScimClient(dbclient):

    def get_users(self):
        user_list = self.get('/preview/scim/v2/Users').get('Resources', None)
        return user_list if user_list else None
    
    def get_groups(self):
        group_list = self.get("/preview/scim/v2/Groups").get('Resources', [])
        return group_list if group_list else None
