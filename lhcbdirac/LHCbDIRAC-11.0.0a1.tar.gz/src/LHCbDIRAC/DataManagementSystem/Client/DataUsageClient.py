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
:mod: DataUsageClient

.. module: DataUsageClient

:synopsis: Class that contains client access to the StorageUsageDB handler.
"""
import six

# # imports
from DIRAC import S_ERROR
from DIRAC.Core.Base.Client import Client, createClient


@createClient("DataManagement/DataUsage")
class DataUsageClient(Client):
    """
    .. class:: DataUsageClient
    """

    def __init__(self, url=None, **kwargs):
        """c'tor."""
        super(DataUsageClient, self).__init__(**kwargs)
        self.setServer("DataManagement/DataUsage")
        if url:
            self.setServer(url)

    def sendDataUsageReport(self, site, directoryDict, status="New", rpc=None, url="", timeout=120):
        """send data usage report."""
        if not isinstance(directoryDict, dict):
            return S_ERROR("Supplied dictionary is not in correct format!")
        rpcClient = self._getRPC(rpc=rpc, url=url, timeout=timeout)
        return rpcClient.sendDataUsageReport(site, directoryDict, status)

    def getDataUsageSummary(self, startTime, endTime, status, rpc=None, url="", timeout=120):
        """get usage summary."""
        if not (
            isinstance(startTime, six.string_types)
            and isinstance(endTime, six.string_types)
            and isinstance(status, six.string_types)
        ):
            return S_ERROR("Supplied arguments not in correct format!")
        rpcClient = self._getRPC(rpc=rpc, url=url, timeout=timeout)
        return rpcClient.getDataUsageSummary(startTime, endTime, status)

    def insertToDirMetadata(self, directoryDict, url="", timeout=120):
        """insert metadata to dir or maybe other way around."""
        if not isinstance(directoryDict, dict):
            return S_ERROR("Supplied dictionary is not in correct format!")
        rpcClient = self._getRPC(rpc=None, url=url, timeout=timeout)
        return rpcClient.insertToDirMetadata(directoryDict)

    def getDirMetadata(self, directoryList, url="", timeout=120):
        """get directory metadata."""
        if isinstance(directoryList, six.string_types):
            directoryList = [directoryList]
        elif isinstance(directoryList, (set, tuple, dict)):
            directoryList = list(directoryList)
        elif not isinstance(directoryList, list):
            return S_ERROR("Supplied argument is not in correct format!")
        rpcClient = self._getRPC(rpc=None, url=url, timeout=timeout)
        return rpcClient.getDirMetadata(directoryList)

    def updatePopEntryStatus(self, idList, newStatus, url="", timeout=120):
        """whatever, pop new status."""
        if not isinstance(idList, list) or not isinstance(newStatus, six.string_types):
            return S_ERROR("Supplied arguments are not in correct format!")
        rpcClient = self._getRPC(rpc=None, url=url, timeout=timeout)
        return rpcClient.updatePopEntryStatus(idList, newStatus)
