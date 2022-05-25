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
"""This is the LHCb Online storage."""
from six.moves import xmlrpc_client as xmlrpclib
import os

from DIRAC import gLogger, S_OK, S_ERROR
from DIRAC.Resources.Storage.StorageBase import StorageBase

from DIRAC.Resources.Storage.Utilities import checkArgumentFormat
from DIRAC.Core.Utilities.List import breakListIntoChunks


class LHCbOnlineStorage(StorageBase):
    """Plugin to talk to the xmlrpc of the datamover."""

    def __init__(self, storageName, parameterDict):
        self.isok = True

        super(LHCbOnlineStorage, self).__init__(storageName, parameterDict)
        self.pluginName = "LHCbOnline"
        self.name = storageName
        self.timeout = 100

        serverString = "%s://%s:%s" % (
            self.protocolParameters["Protocol"],
            self.protocolParameters["Host"],
            self.protocolParameters["Port"],
        )
        self.server = xmlrpclib.Server(serverString)

    def getFileSize(self, urls):
        # FIXME: What the hell is this method doing ??
        """Get a fake file size."""
        if not urls:
            return S_ERROR("LHCbOnline.getFileSize: No surls supplied.")
        successful = {}
        failed = {}
        for pfn in urls:
            successful[pfn] = 0
        resDict = {"Failed": failed, "Successful": successful}
        return S_OK(resDict)

    def retransferOnlineFile(self, urls):
        """Tell the Online system that the migration failed and we want to get the
        request again."""

        if not urls:
            return S_ERROR("LHCbOnline.requestRetransfer: No surls supplied.")
        successful = {}
        failed = {}
        for pfn in urls:
            try:
                success, error = self.server.errorMigratingFile(pfn)
                if success:
                    successful[pfn] = True
                    gLogger.info("LHCbOnline.requestRetransfer: Successfully requested file from RunDB.")
                else:
                    errStr = "LHCbOnline.requestRetransfer: Failed to request file from RunDB: %s" % error
                    failed[pfn] = errStr
                    gLogger.error(errStr, pfn)
            except Exception as x:  # pylint: disable=broad-except
                errStr = "LHCbOnline.requestRetransfer: Exception while requesting file from RunDB."
                gLogger.exception(errStr, lException=x)
                failed[pfn] = errStr
        resDict = {"Failed": failed, "Successful": successful}
        return S_OK(resDict)

    def removeFile(self, urls):
        """Remove physically the file specified by its path."""
        if not urls:
            return S_ERROR("LHCbOnline.removeFile: No surls supplied.")
        successful = {}
        failed = {}
        # Here we are sure of the unicity of the basename since it is for raw data only
        filesToUrls = dict((os.path.basename(f), f) for f in urls)
        filenames = list(filesToUrls)

        for filenameChunck in breakListIntoChunks(filenames, 100):

            try:
                success, errorOrFailed = self.server.endMigratingFileBulk(filenameChunck)
                if success:
                    # in case of success, errorOrFailed contains the files for which it failed
                    failedFiles = set(errorOrFailed)
                    for fn in filenameChunck:
                        fullUrl = filesToUrls[fn]
                        if fn in failedFiles:
                            failed[fullUrl] = "Failed to remove, check datamover logs"
                        else:
                            successful[fullUrl] = True
                    gLogger.info("LHCbOnline.getFile: Successfully issued removal to RunDB for chuck.")
                else:
                    errStr = "LHCbOnline.removeFile: Failed to issue removal for chunck to RunDB %s" % errorOrFailed
                    for fn in filenameChunck:
                        fullUrl = filesToUrls[fn]
                        failed[fullUrl] = errStr
                    gLogger.error(errStr, urls)
            except Exception as x:  # pylint: disable=broad-except
                errStr = "LHCbOnline.getFile: Exception for chunck while issuing removal to RunDB."
                gLogger.exception(errStr, lException=x)
                for fn in filenameChunck:
                    fullUrl = filesToUrls[fn]
                    failed[fullUrl] = errStr

        resDict = {"Failed": failed, "Successful": successful}
        return S_OK(resDict)
