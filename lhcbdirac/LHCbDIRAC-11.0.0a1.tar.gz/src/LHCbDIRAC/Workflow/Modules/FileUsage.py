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
"""Module to upload specified job output files according to the parameters
defined in the user workflow."""
import os

from DIRAC import S_OK, S_ERROR, gLogger, gConfig
from DIRAC.Core.Utilities import DEncode
from DIRAC.RequestManagementSystem.Client.Request import Operation
from LHCbDIRAC.Workflow.Modules.ModuleBase import ModuleBase
from LHCbDIRAC.DataManagementSystem.Client.DataUsageClient import DataUsageClient


class FileUsage(ModuleBase):

    #############################################################################

    def __init__(self, bkClient=None, dm=None):
        """Module initialization."""
        self.log = gLogger.getSubLogger("FileUsage")
        super(FileUsage, self).__init__(self.log, bkClientIn=bkClient, dm=dm)
        self.dataUsageClient = DataUsageClient()

    #############################################################################

    def _resolveInputVariables(self):
        """By convention the module parameters are resolved here."""
        super(FileUsage, self)._resolveInputVariables()

        dirDict = {}
        if self.inputDataList:
            for inputFile in self.inputDataList:
                strippedDir = os.path.join(os.path.dirname(inputFile), "")
                if not strippedDir:
                    self.log.error("File specified without directory! ", inputFile)
                else:
                    dirDict[strippedDir] = dirDict.setdefault(strippedDir, 0) + 1
            self.log.info("Popularity report = ", dirDict)
        else:
            self.log.info("No input data specified for this job")

        return S_OK(dirDict)

    #############################################################################

    def execute(
        self,
        production_id=None,
        prod_job_id=None,
        wms_job_id=None,
        workflowStatus=None,
        stepStatus=None,
        wf_commons=None,
        step_commons=None,
        step_id=None,
        step_number=None,
    ):
        """Main execution function."""

        try:

            super(FileUsage, self).execute(
                production_id,
                prod_job_id,
                wms_job_id,
                workflowStatus,
                stepStatus,
                wf_commons,
                step_commons,
                step_number,
                step_id,
            )

            result = self._resolveInputVariables()
            if not result["OK"]:
                self.log.error(result["Message"])
                return S_OK()
            dirDict = result["Value"]

            self.request.RequestName = "job_%d_request.xml" % self.jobID
            self.request.JobID = self.jobID
            self.request.SourceComponent = "Job_%d" % self.jobID

            if dirDict:
                result = self._reportFileUsage(dirDict)
                if not result["OK"]:
                    self.log.error(result["Message"])
                    return S_OK()
                self.log.info("Reporting input file usage successful!")
            else:
                self.log.info("No input data usage to report!")

            return S_OK("File Usage reported successfully")

        except Exception as e:  # pylint:disable=broad-except
            self.log.exception("Failure in FileUsage execute module", lException=e)
            return S_ERROR(str(e))

        finally:
            super(FileUsage, self).finalize()

    #############################################################################

    def _reportFileUsage(self, dirDict):
        """Send the data usage report (site,dirDict) where dirDict = {'Dataset':NumberOfHits}
        example: {'/lhcb/certification/test/ALLSTREAMS.DST/00000002/0000/': 1,
        '/lhcb/LHCb/Collision11/BHADRON.DST/00012957/0000/': 2}
        """
        self.log.verbose("Reporting input file usage:")
        for entry in dirDict:
            self.log.verbose("%s:%s" % (entry, dirDict[entry]))
        localSite = gConfig.getValue("/LocalSite/Site", "UNKNOWN")
        try:
            localSite = localSite.split(".")[1]
        except BaseException:
            pass
        self.log.verbose("Using Site Name: %s" % (localSite))

        if self._enableModule():
            usageStatus = self.dataUsageClient.sendDataUsageReport(localSite, dirDict)
            if not usageStatus["OK"]:
                self.log.error("Could not send data usage report, preparing a DISET failover request object")
                self.log.verbose(usageStatus["rpcStub"])
                forwardDISETOp = Operation()
                forwardDISETOp.Type = "ForwardDISET"
                forwardDISETOp.Arguments = DEncode.encode(usageStatus["rpcStub"])
                self.request.addOperation(forwardDISETOp)
                self.workflow_commons["Request"] = self.request
        else:
            self.log.info("Would have attempted to report %s at %s" % (dirDict, localSite))
            return S_OK()

        return S_OK()


# EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#
