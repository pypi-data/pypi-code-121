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
"""Client for BookkeepingDB file catalog."""
import six

from DIRAC import gLogger, S_OK, S_ERROR
from DIRAC.Core.Utilities.List import breakListIntoChunks
from DIRAC.Resources.Catalog.FileCatalogClientBase import FileCatalogClientBase
from DIRAC.Resources.Catalog.Utilities import checkCatalogArguments
from LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient import BookkeepingClient


class BookkeepingDBClient(FileCatalogClientBase):
    """File catalog client for bookkeeping DB."""

    READ_METHODS = FileCatalogClientBase.READ_METHODS + ["isDirectory", "isLink", "getFileSize", "getFileMetadata"]
    WRITE_METHODS = FileCatalogClientBase.WRITE_METHODS + [
        "addFile",
        "addReplica",
        "removeFile",
        "removeReplica",
        "setReplicaStatus",
        "setReplicaProblematic",
        "setReplicaHost",
        "removeDirectory",
        "createDirectory",
        "removeLink",
        "createLink",
    ]

    def __init__(self, **kwargs):
        """Constructor of the Bookkeeping catalogue client."""
        self.splitSize = 1000
        self.name = "BookkeepingDB"
        self.server = BookkeepingClient(timeout=120)

    @checkCatalogArguments
    def addFile(self, lfn):
        """Set the replica flag."""
        return self.__setHasReplicaFlag(lfn)

    @checkCatalogArguments
    def addReplica(self, lfn):
        """Same as addFile."""
        return self.addFile(lfn)

    @checkCatalogArguments
    def removeFile(self, path):
        """Remove the replica flag."""
        return self.__unsetHasReplicaFlag(path)

    @checkCatalogArguments
    def isFile(self, lfn):
        """Returns a dictionary True/False."""
        return self.__exists(lfn)

    @checkCatalogArguments
    def isDirectory(self, lfn):
        """Return Successful dict: True if lfn is a directory, False if a file - Failed dict if not existing"""
        res = self.isFile(lfn)
        if not res["OK"]:
            successful = {}
            failed = dict.fromkeys(lfn, res["Message"])
        else:
            successful = dict.fromkeys([lfn for lfn, val in res["Value"]["Successful"].items() if val], False)
            failed = res["Value"]["Failed"]
            toCheck = [lfn for lfn, val in res["Value"]["Successful"].items() if not val]
            if toCheck:
                # Can't use service directly as
                res = self.server.getDirectoryMetadata_new(toCheck)
                if not res["OK"]:
                    failed.update(dict.fromkeys(toCheck, res["Message"]))
                else:
                    failed.update(dict.fromkeys([lfn for lfn in res["Value"]["Failed"]], "Not a file or directory"))
                    successful.update(dict.fromkeys([lfn for lfn in res["Value"]["Successful"]], True))
        return S_OK({"Successful": successful, "Failed": failed})

    @checkCatalogArguments
    def isLink(self, lfn):
        return self.__returnSuccess(lfn, val=False)

    @checkCatalogArguments
    def __returnSuccess(self, lfn, val=True):
        """Generic method returning success for all input files."""
        return S_OK({"Failed": {}, "Successful": dict.fromkeys(lfn, val)})

    @checkCatalogArguments
    def removeReplica(self, lfn):
        return self.__returnSuccess(lfn)

    @checkCatalogArguments
    def setReplicaStatus(self, lfn):
        return self.__returnSuccess(lfn)

    @checkCatalogArguments
    def setReplicaProblematic(self, lfn, revert=False):
        return self.__returnSuccess(lfn)

    @checkCatalogArguments
    def setReplicaHost(self, lfn):
        return self.__returnSuccess(lfn)

    @checkCatalogArguments
    def removeDirectory(self, lfn, recursive=False):
        return self.__returnSuccess(lfn)

    @checkCatalogArguments
    def createDirectory(self, lfn):
        return self.__returnSuccess(lfn)

    @checkCatalogArguments
    def removeLink(self, lfn):
        return self.__returnSuccess(lfn)

    @checkCatalogArguments
    def createLink(self, lfn):
        return self.__returnSuccess(lfn)

    @checkCatalogArguments
    def exists(self, path):
        """Returns a dictionary of True/False on file existence."""
        return self.__exists(path)

    @checkCatalogArguments
    def getFileMetadata(self, path):
        """Return the metadata dictionary."""
        return self.__getFileMetadata(path)

    @checkCatalogArguments
    def getFileSize(self, path):
        """Return just the file size."""

        res = self.__getFileMetadata(path)
        # Always returns OK
        successful = dict([(lfn, metadata["FileSize"]) for lfn, metadata in res["Value"]["Successful"].items()])
        return S_OK({"Successful": successful, "Failed": res["Value"]["Failed"]})

    ################################################################
    #
    # These are the internal methods used for actual interaction with the BK service
    #

    def __checkArgumentFormat(self, path):
        """Returns a list, either from a string or keys of a dict."""
        if isinstance(path, six.string_types):
            return S_OK([path])
        elif isinstance(path, list):
            return S_OK(path)
        elif isinstance(path, dict):
            return S_OK(list(path))
        else:
            errStr = "BookkeepingDBClient.__checkArgumentFormat: Supplied path is not of the correct format."
            gLogger.error(errStr)
            return S_ERROR(errStr)

    def __toggleReplicaFlag(self, lfns, setflag=True):
        successful = {}
        # Poor man's way to not return an error for user files
        for lfn in [lfn for lfn in lfns if lfn.startswith("/lhcb/user")]:
            lfns.pop(lfn)
            successful[lfn] = True
        failed = {}
        for lfnList in breakListIntoChunks(lfns, self.splitSize):
            res = {True: self.server.addFiles, False: self.server.removeFiles}[setflag](lfnList)
            if not res["OK"]:
                failed.update(dict.fromkeys(lfnList, res["Message"]))
            else:
                # It is dirty, but ...
                failed.update(dict.fromkeys([lfn for lfn in res["Value"]["Failed"]], "File does not exist"))
                successful.update(dict.fromkeys([lfn for lfn in res["Value"]["Successful"]], True))
        return S_OK({"Successful": successful, "Failed": failed})

    def __setHasReplicaFlag(self, lfns):
        """Set replica flags on BKK."""
        return self.__toggleReplicaFlag(lfns, setflag=True)

    def __unsetHasReplicaFlag(self, lfns):
        """Removes replica flags on BKK."""
        return self.__toggleReplicaFlag(lfns, setflag=False)

    def __exists(self, lfns):
        """Checks if lfns exist."""
        successful = {}
        failed = {}
        for lfnList in breakListIntoChunks(lfns, self.splitSize):
            res = self.server.exists(lfnList)
            if not res["OK"]:
                failed.update(dict.fromkeys(lfnList, res["Message"]))
            else:
                successful.update(res["Value"])
        return S_OK({"Successful": successful, "Failed": failed})

    @checkCatalogArguments
    def __getFileMetadata(self, lfns):
        """Returns lfns metadata."""
        successful = {}
        failed = {}
        for lfnList in breakListIntoChunks(lfns, self.splitSize):
            res = self.server.getFileMetadata(lfnList)
            if not res["OK"]:
                failed.update(dict.fromkeys(lfnList, res["Message"]))
            else:
                success = res["Value"].get("Successful", res["Value"])
                failed.update(dict.fromkeys((lfn for lfn in lfnList if lfn not in success), "File does not exist"))
                failed.update(dict((lfn, val) for lfn, val in success.items() if isinstance(val, six.string_types)))
                successful.update(
                    dict((lfn, val) for lfn, val in success.items() if not isinstance(val, six.string_types))
                )
        return S_OK({"Successful": successful, "Failed": failed})
