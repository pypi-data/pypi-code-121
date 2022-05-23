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
:mod: LogUpload

.. module: LogUpload

:synopsis: logUpload operation handler

LogUpload operation handler
"""
# # imports
import os
from DIRAC import S_OK, S_ERROR
from DIRAC.FrameworkSystem.Client.MonitoringClient import gMonitor
from DIRAC.DataManagementSystem.Agent.RequestOperations.DMSRequestOperationsBase import DMSRequestOperationsBase


class LogUpload(DMSRequestOperationsBase):
    """.. class:: LogUpload.

    LogUpload operation handler
    """

    def __init__(self, operation=None, csPath=None):
        """c'tor.

        :param self: self reference
        :param Operation operation: Operation instance
        :param str csPath: CS path for this handler
        """
        # # base class ctor
        super(LogUpload, self).__init__(operation=operation, csPath=csPath)
        # # gMonitor stuff
        gMonitor.registerActivity(
            "LogUploadAtt", "Log upload attempted", "RequestExecutingAgent", "Files/min", gMonitor.OP_SUM
        )
        gMonitor.registerActivity(
            "LogUploadOK", "Replications successful", "RequestExecutingAgent", "Files/min", gMonitor.OP_SUM
        )
        gMonitor.registerActivity(
            "LogUploadFail", "Replications failed", "RequestExecutingAgent", "Files/min", gMonitor.OP_SUM
        )
        self.workDirectory = os.environ.get("LOGUPLOAD_CACHE", os.environ.get("AGENT_WORKDIRECTORY", "/tmp/LogUpload"))

    def __call__(self):
        """LogUpload operation processing."""
        # # list of targetSEs

        if len(self.operation.targetSEList) != 1:
            self.log.error(
                "wrong value for TargetSE list = %s, should contain only one target!" % self.operation.targetSEList
            )
            self.operation.Error = "Wrong parameters: TargetSE should contain only one targetSE"
            for opFile in self.operation:

                opFile.Status = "Failed"
                opFile.Error = "Wrong parameters: TargetSE should contain only one targetSE"

                gMonitor.addMark("LogUploadAtt", 1)
                gMonitor.addMark("LogUploadFail", 1)

            return S_ERROR("TargetSE should contain only one target, got %s" % self.operation.targetSEList)

        # # check targetSEs for write
        bannedTargets = self.checkSEsRSS()
        if not bannedTargets["OK"]:
            gMonitor.addMark("LogUploadAtt", 1)
            gMonitor.addMark("LogUploadFail", 1)
            return bannedTargets

        # # get waiting files
        waitingFiles = self.getWaitingFilesList()

        # # loop over files
        for opFile in waitingFiles:
            # # get LFN
            lfn = opFile.LFN
            self.log.info("processing file %s" % lfn)
            gMonitor.addMark("LogUploadAtt", 1)

            destination = "/".join(lfn.split("/")[0:-1]) + "/" + (os.path.basename(lfn)).split("_")[1].split(".")[0]
            logUpload = self.dm.replicate(
                lfn, self.operation.targetSEList[0], destPath=destination, localCache=self.workDirectory
            )
            if not logUpload["OK"]:
                gMonitor.addMark("LogUploadFail", 1)
                #         self.dataLoggingClient().addFileRecord( lfn, "LogUploadFail", targetSE, "", "LogUpload" )
                self.log.error("completely failed to upload log file: %s" % logUpload["Message"])
                opFile.Error = str(logUpload["Message"])
                opFile.Attempt += 1
                self.operation.Error = opFile.Error
                if "No such file or directory" in opFile.Error:
                    opFile.Status = "Failed"
                continue

            if lfn in logUpload["Value"]:
                gMonitor.addMark("LogUploadOK", 1)
                #         self.dataLoggingClient().addFileRecord( lfn, "LogUpload", targetSE, "", "LogUpload" )
                opFile.Status = "Done"
                self.log.info("Uploaded %s to %s" % (lfn, self.operation.targetSEList[0]))

        return S_OK()
