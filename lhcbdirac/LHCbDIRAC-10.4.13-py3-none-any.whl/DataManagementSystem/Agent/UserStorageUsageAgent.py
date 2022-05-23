###############################################################################
# (c) Copyright 2019 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "LICENSE".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
"""
:mod: UserStorageUsageAgent

.. module: UserStorageUsageAgent

:synopsis: UserStorageUsageAgent simply inherits the StorageUsage agent
  and loops over the /lhcb/user directory, removing empty ones.
"""
# # imports
from DIRAC import S_OK
from LHCbDIRAC.DataManagementSystem.Agent.StorageUsageAgent import StorageUsageAgent
from DIRAC.Core.Utilities import List


class UserStorageUsageAgent(StorageUsageAgent):
    """
    .. class:: UserStorageUsageAgent

    """

    def removeEmptyDir(self, dirPath):
        """remove empty directories, but skip home.

        :param self: self reference
        :param str dirPath: directory to remove
        """
        # Do not remove user's home dir
        if len(List.fromChar(dirPath, "/")) > 4:
            return StorageUsageAgent.removeEmptyDir(self, dirPath)
        return S_OK()
