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
import random
import re

from DIRAC import S_OK, S_ERROR, gLogger, gConfig
from DIRAC.Core.Utilities.File import getGlobbedFiles
from DIRAC.DataManagementSystem.Client.FailoverTransfer import FailoverTransfer
from DIRAC.DataManagementSystem.Utilities.DMSHelpers import resolveSEGroup

from LHCbDIRAC.Core.Utilities.ProductionData import constructUserLFNs
from LHCbDIRAC.Workflow.Modules.ModuleBase import ModuleBase
from LHCbDIRAC.Core.Utilities.ResolveSE import getDestinationSEList


class UserJobFinalization(ModuleBase):
    """Finalization of user jobs."""

    #############################################################################
    def __init__(self, bkClient=None, dm=None):
        """Module initialization."""

        self.log = gLogger.getSubLogger("UserJobFinalization")
        super(UserJobFinalization, self).__init__(self.log, bkClientIn=bkClient, dm=dm)

        self.enable = True
        self.defaultOutputSE = resolveSEGroup(gConfig.getValue("/Resources/StorageElementGroups/Tier1-USER", []))
        self.failoverSEs = resolveSEGroup(gConfig.getValue("/Resources/StorageElementGroups/Tier1-Failover", []))
        # List all parameters here
        self.request = None
        # Always allow any files specified by users
        self.outputDataFileMask = ""
        self.userOutputData = []
        self.userOutputSE = ""
        self.userOutputPath = ""
        self.failoverTransfer = None
        self.replicateUserOutputData = False
        self.userPrependString = ""

    #############################################################################
    def _resolveInputVariables(self):
        """By convention the module parameters are resolved here."""
        super(UserJobFinalization, self)._resolveInputVariables()

        # Use LHCb utility for local running via dirac-jobexec
        if "UserOutputData" in self.workflow_commons:
            userOutputData = self.workflow_commons["UserOutputData"]
            if not isinstance(userOutputData, list):
                userOutputData = [i.strip() for i in userOutputData.split(";")]
            self.userOutputData = userOutputData

        if "UserOutputSE" in self.workflow_commons:
            specifiedSE = self.workflow_commons["UserOutputSE"]
            if not isinstance(specifiedSE, list):
                self.userOutputSE = [i.strip() for i in specifiedSE.split(";")]
        else:
            self.log.verbose("No UserOutputSE specified, using default value: %s" % (", ".join(self.defaultOutputSE)))
            self.userOutputSE = []

        if "UserOutputPath" in self.workflow_commons:
            self.userOutputPath = self.workflow_commons["UserOutputPath"]

        if "ReplicateUserOutputData" in self.workflow_commons and self.workflow_commons["ReplicateUserOutputData"]:
            self.replicateUserOutputData = True

        if "UserOutputLFNPrepend" in self.workflow_commons:
            self.userPrependString = self.workflow_commons["UserOutputLFNPrepend"]

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
        step_number=None,
        step_id=None,
        orderedSEs=None,
    ):
        """Main execution function."""

        try:

            super(UserJobFinalization, self).execute(
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

            self._resolveInputVariables()

            # Earlier modules may have populated the report objects
            self.request.RequestName = "job_%d_request.xml" % self.jobID
            self.request.JobID = self.jobID
            self.request.SourceComponent = "Job_%d" % self.jobID

            if not self._checkWFAndStepStatus():
                return S_OK()

            if not self.userOutputData:
                self.log.info("No user output data is specified for this job, nothing to do")
                return S_OK("No output data to upload")

            self.log.info("User specified output file list is: %s" % (", ".join(self.userOutputData)))

            globList = []
            for i in self.userOutputData:
                if re.search(r"\*", i):
                    globList.append(i)

            # Check whether list of userOutputData is a globbable pattern
            if globList:
                for i in globList:
                    self.userOutputData.remove(i)

                globbedOutputList = list(set(getGlobbedFiles(globList)))
                if globbedOutputList:
                    self.log.info(
                        "Found a pattern in the output data file list, \
          extra files to upload are: %s"
                        % (", ".join(globbedOutputList))
                    )
                    self.userOutputData += globbedOutputList
                else:
                    self.log.info(
                        "No files were found on the local disk for the following patterns: %s" % (", ".join(globList))
                    )

            self.log.info("Final list of files to upload are: %s" % (", ".join(self.userOutputData)))

            # Determine the final list of possible output files for the workflow
            # and all the parameters needed to upload them.
            outputList = []
            for i in self.userOutputData:
                outputList.append({"outputDataType": (".".split(i)[-1]).upper(), "outputDataName": os.path.basename(i)})

            userOutputLFNs = []
            if self.userOutputData:
                self.log.info("Constructing user output LFN(s) for %s" % (", ".join(self.userOutputData)))

                userOutputLFNs = constructUserLFNs(
                    self.jobID,
                    self._getCurrentOwner(),
                    self.userOutputData,
                    self.userOutputPath,
                    self.userPrependString,
                )

            self.log.verbose(
                "Calling getCandidateFiles( %s, %s, %s)" % (outputList, userOutputLFNs, self.outputDataFileMask)
            )
            try:
                fileDict = self.getCandidateFiles(outputList, userOutputLFNs, self.outputDataFileMask)
            except os.error as e:
                self.setApplicationStatus(e)
                return S_OK()

            try:
                fileMetadata = self.getFileMetadata(fileDict)
            except RuntimeError as e:
                self.setApplicationStatus(e)
                return S_OK()

            if not fileMetadata:
                self.log.info("No output data files were determined to be uploaded for this workflow")
                self.setApplicationStatus("No Output Data Files To Upload")
                return S_OK()

            if not orderedSEs:
                orderedSEs = self._getOrderedSEsList()

            self.log.info("Ordered list of output SEs is: %s" % (", ".join(orderedSEs)))
            final = {}
            for fileName, metadata in fileMetadata.items():
                final[fileName] = metadata
                final[fileName]["resolvedSE"] = orderedSEs

            # At this point can exit and see exactly what the module will upload
            if not self._enableModule():
                self.log.info("Module disabled would have attempted to upload the files %s" % ", ".join(final))
                for fileName, metadata in final.items():
                    self.log.info("--------%s--------" % fileName)
                    for n, v in metadata.items():
                        self.log.info("%s = %s" % (n, v))

                return S_OK("Module is disabled by control flag")

            # Disable the watchdog check in case the file uploading takes a long time
            self._disableWatchdogCPUCheck()

            # Instantiate the failover transfer client with the global request object
            if not self.failoverTransfer:
                self.failoverTransfer = FailoverTransfer(self.request)

            # One by one upload the files with failover if necessary
            replication = {}
            failover = {}
            uploaded = []
            for fileName, metadata in final.items():
                self.log.info(
                    "Attempting to store %s to the following SE(s): %s" % (fileName, ", ".join(metadata["resolvedSE"]))
                )
                fileMetaDict = {
                    "Size": metadata["filedict"]["Size"],
                    "LFN": metadata["filedict"]["LFN"],
                    "GUID": metadata["filedict"]["GUID"],
                    "Checksum": metadata["filedict"]["Checksum"],
                    "ChecksumType": metadata["filedict"]["ChecksumType"],
                }
                result = self.failoverTransfer.transferAndRegisterFile(
                    fileName=fileName,
                    localPath=metadata["localpath"],
                    lfn=metadata["filedict"]["LFN"],
                    destinationSEList=metadata["resolvedSE"],
                    fileMetaDict=fileMetaDict,
                    masterCatalogOnly=True,
                )
                if not result["OK"]:
                    self.log.error("Could not transfer and register %s with metadata:\n %s" % (fileName, metadata))
                    failover[fileName] = metadata
                else:
                    # Only attempt replication after successful upload
                    lfn = metadata["lfn"]
                    uploaded.append(lfn)
                    seList = metadata["resolvedSE"]
                    replicateSE = ""
                    uploadedSE = result["Value"].get("uploadedSE", "")
                    if uploadedSE:
                        for se in seList:
                            if not se == uploadedSE:
                                replicateSE = se
                                break

                    if replicateSE and lfn and self.replicateUserOutputData:
                        self.log.info("Will attempt to replicate %s to %s" % (lfn, replicateSE))
                        replication[lfn] = (uploadedSE, replicateSE, fileMetaDict)

            cleanUp = False
            for fileName, metadata in failover.items():
                random.shuffle(self.failoverSEs)
                targetSE = metadata["resolvedSE"][0]
                if len(metadata["resolvedSE"]) > 1:
                    replicateSE = metadata["resolvedSE"][1]
                else:
                    replicateSE = ""
                metadata["resolvedSE"] = self.failoverSEs
                fileMetaDict = {
                    "Size": metadata["filedict"]["Size"],
                    "LFN": metadata["filedict"]["LFN"],
                    "GUID": metadata["filedict"]["GUID"],
                }
                result = self.failoverTransfer.transferAndRegisterFileFailover(
                    fileName,
                    metadata["localpath"],
                    metadata["lfn"],
                    targetSE,
                    metadata["resolvedSE"],
                    fileMetaDict=fileMetaDict,
                    masterCatalogOnly=True,
                )
                if not result["OK"]:
                    self.log.error("Could not transfer and register %s with metadata:\n %s" % (fileName, metadata))
                    cleanUp = True
                    continue  # for users can continue even if one completely fails
                else:
                    lfn = metadata["lfn"]
                    uploaded.append(lfn)
                    # Even when using Failover, one needs to replicate to a second SE
                    if replicateSE and self.replicateUserOutputData:
                        replication[lfn] = (targetSE, replicateSE, fileMetaDict)

            # For files correctly uploaded must report LFNs to job parameters
            if uploaded:
                report = ", ".join(uploaded)
                self.setJobParameter("UploadedOutputData", report)

            # Now after all operations, retrieve potentially modified request object
            self.request = self.failoverTransfer.request

            # If some or all of the files failed to be saved to failover
            if cleanUp:
                self.workflow_commons["Request"] = self.request
                # Leave any uploaded files just in case it is useful for the user
                # do not try to replicate any files.
                return S_ERROR("Failed To Upload Output Data")

            for lfn, (uploadedSE, repSE, fileMetaDictItem) in replication.items():
                self.failoverTransfer._setFileReplicationRequest(lfn, repSE, fileMetaDictItem, uploadedSE)

            self.workflow_commons["Request"] = self.failoverTransfer.request

            self.generateFailoverFile()

            self.setApplicationStatus("Job Finished Successfully")

            return S_OK("Output data uploaded")

        except Exception as e:  # pylint:disable=broad-except
            self.log.exception("Failure in UserJobFinalization execute module", lException=e)
            self.setApplicationStatus(repr(e))
            return S_ERROR(str(e))

        finally:
            super(UserJobFinalization, self).finalize()

    #############################################################################

    def _getOrderedSEsList(self):
        """Returns list of ordered SEs to which trying to upload."""
        # FIXME: remove all banned SEs (not the force ones)
        # First get the local (or assigned) SE to try first for upload and others in random fashion
        localSEs = set(getDestinationSEList("Tier1-USER", self.siteName, outputmode="local"))
        self.log.verbose("Site Local SE for user outputs is: %s" % (list(localSEs)))
        userSEs = set(self.userOutputSE)
        otherSEs = set(self.defaultOutputSE) - localSEs - userSEs
        # If a user SE is  local set it first
        topSEs = userSEs & localSEs
        # reordered user SEs, setting local first
        userSEs = list(topSEs) + list(userSEs - topSEs)
        localSEs = list(localSEs - topSEs)
        if len(userSEs) < 2 and localSEs:
            # Set a local SE first
            orderedSEs = localSEs[0:1] + userSEs + localSEs[1:]
        else:
            orderedSEs = userSEs + localSEs
        random.shuffle(list(otherSEs))
        orderedSEs += otherSEs

        return orderedSEs
