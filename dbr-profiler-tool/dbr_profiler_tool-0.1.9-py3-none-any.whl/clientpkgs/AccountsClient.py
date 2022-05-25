import logging
import os
import re
import time
from core import logging_utils
from core import wmconstants
from core.dbclient import dbclient


class AccountsClient(dbclient):


    def get_workspace_list(self, accountid):
        """
        Returns an array of json objects for workspace
        """
        workspaces_list = self.get(f"/accounts/{accountid}/workspaces", master_acct=True).get('elements',[])
        return workspaces_list
        
    def get_credentials_list(self, accountid):
        """
        Returns an array of json objects for credentials
        """
        credentials_list = self.get(f"/accounts/{accountid}/credentials", master_acct=True).get('elements',[])
        return credentials_list

    def get_storage_list(self, accountid):
        """
        Returns an array of json objects for storage
        """
        storage_list = self.get(f"/accounts/{accountid}/storage-configurations", master_acct=True).get('elements',[])
        return storage_list

    def get_network_list(self, accountid):
        """
        Returns an array of json objects for networks
        """
        network_list = self.get(f"/accounts/{accountid}/networks", master_acct=True).get('elements',[])
        return network_list

    def get_cmk_list(self, accountid):
        """
        Returns an array of json objects for networks
        """
        cmk_list = self.get(f"/accounts/{accountid}/customer-managed-keys", master_acct=True).get('elements',[])
        return cmk_list

    def get_logdelivery_list(self, accountid):
        """
        Returns an array of json objects for log delivery
        """
        logdeliveryinfo = self.get(f"/accounts/{accountid}/log-delivery", master_acct=True).get('elements',[])
        return logdeliveryinfo



