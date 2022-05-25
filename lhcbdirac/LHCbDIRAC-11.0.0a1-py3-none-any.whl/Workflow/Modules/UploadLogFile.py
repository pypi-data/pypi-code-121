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
"""UploadLogFile module is used to upload the files present in the working
directory."""
import os
import shutil
import glob
import random
import stat
import shlex

from DIRAC import S_OK, S_ERROR, gLogger
from DIRAC.Core.Utilities.Subprocess import systemCall
from DIRAC.Core.Utilities.File import mkDir
from DIRAC.DataManagementSystem.Client.FailoverTransfer import FailoverTransfer
from DIRAC.RequestManagementSystem.Client.Operation import Operation
from DIRAC.RequestManagementSystem.Client.File import File
from DIRAC.Resources.Storage.StorageElement import StorageElement
from DIRAC.Core.Utilities.ReturnValues import returnSingleResult

from LHCbDIRAC.Workflow.Modules.ModuleBase import ModuleBase
from LHCbDIRAC.Workflow.Modules.ModulesUtilities import zipFiles
from LHCbDIRAC.Core.Utilities.ProductionData import getLogPath
from LHCbDIRAC.Core.Utilities.ResolveSE import getDestinationSEList


class UploadLogFile(ModuleBase):
    """Upload to LogSE."""

    #############################################################################

    def __init__(self, bkClient=None, dm=None):
        """Module initialization."""

        self.log = gLogger.getSubLogger("UploadLogFile")
        super(UploadLogFile, self).__init__(self.log, bkClientIn=bkClient, dm=dm)

        self.logSE = self.opsH.getValue("LogStorage/LogSE", "LogSE")
        self.logSizeLimit = self.opsH.getValue("LogFiles/SizeLimit", 1 * 1024 * 1024)
        self.logExtensions = self.opsH.getValue("LogFiles/Extensions", [])
        self.logFilePath = ""
        self.logLFNPath = ""
        self.logdir = ""
        self.failoverTransfer = None
        self.failoverSEs = []

    ######################################################################

    def _resolveInputVariables(self):

        super(UploadLogFile, self)._resolveInputVariables()

        if "LogTargetPath" in self.workflow_commons:
            self.logLFNPath = self.workflow_commons["LogTargetPath"]
        else:
            self.log.info("LogFilePath parameter not found, creating on the fly")
            result = getLogPath(self.workflow_commons, self.bkClient)
            if not result["OK"]:
                self.log.error("Could not create LogFilePath", result["Message"])
                return result
            self.logLFNPath = result["Value"]["LogTargetPath"][0]

        if not isinstance(self.logLFNPath, str):
            self.logLFNPath = self.logLFNPath[0]

    ######################################################################

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
    ):
        """Main executon method."""

        try:

            super(UploadLogFile, self).execute(
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

            self.request.RequestName = "job_%d_request.xml" % self.jobID
            self.request.JobID = self.jobID
            self.request.SourceComponent = "Job_%d" % self.jobID

            res = systemCall(0, shlex.split("ls -al"))
            if res["OK"] and res["Value"][0] == 0:
                self.log.info("The contents of the working directory...")
                self.log.info(str(res["Value"][1]))
            else:
                self.log.error("Failed to list the log directory", str(res["Value"][2]))

            self.log.debug("PRODUCTION_ID = %s, JOB_ID = %s " % (self.production_id, self.prod_job_id))
            self.logdir = os.path.realpath("./job/log/%s/%s" % (self.production_id, self.prod_job_id))
            self.log.info("Selected log files will be temporarily stored", "in %s" % self.logdir)

            ##########################################
            # First determine the files which should be saved
            self.log.info("Determining the files to be saved in the logs.")
            res = self._determineRelevantFiles()
            if not res["OK"]:
                self.log.error("Completely failed to select relevant log files.", res["Message"])
                return S_OK()
            selectedFiles = res["Value"]
            self.log.info("The following files were selected to be saved", "\n".join(selectedFiles))

            #########################################
            # Create a temporary directory containing these files
            self.log.info("Populating a temporary directory for selected files.")
            res = self.__populateLogDirectory(selectedFiles)
            if not res["OK"]:
                self.log.error("Completely failed to populate temporary log file directory.", res["Message"])
                self.setApplicationStatus("Failed To Populate Log Dir")
                return S_OK()
            self.log.debug("%s populated with log files." % self.logdir)

            #########################################
            # Make sure all the files in the log directory have the correct permissions
            result = self.__setLogFilePermissions(self.logdir)
            if not result["OK"]:
                self.log.error(
                    "Could not set permissions of log files to 0755", "with message:\n%s" % (result["Message"])
                )

            # zip all files
            zipFileName = os.path.basename(str(self.prod_job_id) + ".zip")
            try:
                res = zipFiles(zipFileName, selectedFiles, str(self.prod_job_id))
                if not res["OK"]:
                    self.log.error("Failed to create zip of log files", res["Message"])
                    self.setApplicationStatus("Failed to create zip of log files")
                    # We do not fail the job for this case
                    return S_OK()
            except IOError:
                self.log.error("Failed to create zip of log files", res["Message"])
                self.setApplicationStatus("Failed to create zip of log files")
                # We do not fail the job for this case
                return S_OK()

            # Instantiate the failover transfer client with the global request object
            if not self.failoverTransfer:
                self.failoverTransfer = FailoverTransfer(self.request)

            # Attempt to uplaod the zippped logs to the LogSE
            self.log.info("Transferring zipped log files", "to the %s" % self.logSE)

            if not self._enableModule():
                self.log.info("Would have attempted to upload the zipped log files, but there's not JobID")
                return S_OK()

            # self.logFilePath is something like /lhcb/MC/2016/LOG/00095376/0000/00000381
            # the zipFileName should have the same name, e.g. 00000381.zip
            zipPath = os.path.join(self.logFilePath, zipFileName)
            res = returnSingleResult(StorageElement(self.logSE).getURL(zipPath, protocol="https"))
            if not res["OK"]:
                self.log.warn("Could not get dynamic URL for log", res)
                logHttpsURL = "https://lhcb-dirac-logse.web.cern.ch/lhcb-dirac-logse/%s" % zipPath
            else:
                logHttpsURL = res["Value"]

            self.log.info("putFile", "%s to %s" % (zipFileName, self.logSE))
            # What is uploaded should be something like /lhcb/MC/2016/LOG/00095376/0000/00000381.zip
            # (so, removing the last directory, that is the same same of the .zip file)
            # The rule for interpreting what is to be deflated can be found in /eos/lhcb/grid/prod/lhcb/logSE/.htaccess
            uploadPath = os.path.join(os.path.dirname(self.logFilePath.rstrip("/")), zipFileName)
            res = returnSingleResult(StorageElement(self.logSE).putFile({uploadPath: zipFileName}))
            if res["OK"]:
                self.log.info("Successfully upload log file", "to %s" % self.logSE)
                self.log.info("Logs for this job may be retrieved", "from %s" % logHttpsURL)
            else:
                self.log.error(
                    "Failed to upload log files", "with message '%s', now uploading to failover SE" % res["Message"]
                )
                self._uploadLogToFailoverSE(zipFileName)

            # While it's the zip file that is uploaded, we set in job parameters its directory,
            # as the .zip is deflated automatically
            self.setJobParameter("Log URL", '<a href="%s">Log file directory</a>' % logHttpsURL.rstrip(zipFileName))

            self.workflow_commons["Request"] = self.request

            return S_OK("Log Files uploaded")

        except Exception as e:  # pylint:disable=broad-except
            self.log.exception("Failure in UploadLogFile execute module", lException=e)
            return S_ERROR(str(e))

        finally:
            super(UploadLogFile, self).finalize()

    #############################################################################

    def _uploadLogToFailoverSE(self, zipFileName):
        """Recover the logs to a failover storage element."""

        # here because self.siteName is not known until execute() is invoked
        self.failoverSEs = getDestinationSEList("Tier1-Failover", self.siteName, outputmode="Any")
        random.shuffle(self.failoverSEs)
        self.log.info(
            "Attempting to store file", "%s to the following SE(s):\n%s" % (zipFileName, ", ".join(self.failoverSEs))
        )

        fileDict = {zipFileName: {"lfn": self.logLFNPath, "workflowSE": self.failoverSEs}}
        metadata = self.getFileMetadata(fileDict)
        fileMetaDict = {
            "Size": metadata[zipFileName]["filedict"]["Size"],
            "LFN": metadata[zipFileName]["filedict"]["LFN"],
            "GUID": metadata[zipFileName]["filedict"]["GUID"],
            "Checksum": metadata[zipFileName]["filedict"]["Checksum"],
            "ChecksumType": metadata[zipFileName]["filedict"]["ChecksumType"],
        }

        result = self.failoverTransfer.transferAndRegisterFile(
            fileName=zipFileName,
            localPath="%s/%s" % (os.getcwd(), zipFileName),
            lfn=self.logLFNPath,
            destinationSEList=self.failoverSEs,
            fileMetaDict=fileMetaDict,
            masterCatalogOnly=True,
        )

        if not result["OK"]:
            self.log.error("Failed to upload logs to all failover destinations (the job will not fail for this reason")
            self.setApplicationStatus("Failed To Upload Logs")
        else:
            uploadedSE = result["Value"]["uploadedSE"]
            self.log.info("Uploaded logs to failover SE", uploadedSE)

            self.request = self.failoverTransfer.request

            self.__createLogUploadRequest(self.logSE, self.logLFNPath, uploadedSE)
            self.log.verbose("Successfully created failover request")

    def _determineRelevantFiles(self):
        """The files which are below a configurable size will be stored in the
        logs.

        This will typically pick up everything in the working directory
        minus the output data files.
        """
        logFileExtensions = [
            "*.txt",
            "*.log",
            "*.out",
            "*.output",
            "*.xml",
            "*.sh",
            "*.info",
            "*.err",
            # TODO: Remove once the prodConf migration is done
            "prodConf*.py",
            "prodConf*.json",
        ]  # '*.root',
        if self.logExtensions:
            self.log.debug("Using list of log extensions from CS:\n%s" % (", ".join(self.logExtensions)))
            logFileExtensions = self.logExtensions
        else:
            self.log.debug("Using default list of log extensions:\n%s" % (", ".join(logFileExtensions)))

        candidateFiles = []
        for ext in logFileExtensions:
            self.log.debug("Looking at log file wildcard: %s" % ext)
            globList = glob.glob(ext)
            for check in globList:
                if os.path.isfile(check):
                    self.log.debug("Found locally existing log file: %s" % check)
                    candidateFiles.append(check)

        return S_OK(candidateFiles)

    #############################################################################

    def __populateLogDirectory(self, selectedFiles):
        """A temporary directory is created for all the selected files.

        These files are then copied into this directory before being
        uploaded
        """
        # Create the temporary directory
        mkDir(self.logdir)
        # Set proper permissions
        self.log.info("Changing log directory permissions to 0755")
        try:
            os.chmod(self.logdir, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH + stat.S_IXOTH)
        except OSError as x:
            self.log.error("Could not set logdir permissions to 0755:", "%s (%s)" % (self.logdir, str(x)))
        # Populate the temporary directory
        try:
            for fileS in selectedFiles:
                destinationFile = "%s/%s" % (self.logdir, os.path.basename(fileS))
                shutil.copy(fileS, destinationFile)
        except shutil.Error:
            self.log.warn("src and dst are the same")
        except IOError as x:
            self.log.exception("Exception while trying to copy file.", str(fileS) + str(x))
            self.log.info("The following files will be skipped and can be considered lost", str(fileS))

        # Now verify the contents of our target log dir
        successfulFiles = os.listdir(self.logdir)
        if not successfulFiles:
            self.log.info("Failed to copy any files to the target directory.")
            return S_ERROR()

        self.log.debug("Prepared %s files in the temporary directory." % self.logdir)
        return S_OK()

    #############################################################################

    def __createLogUploadRequest(self, targetSE, logFileLFN, uploadedSE):
        """Set a request to upload job log files from the output sandbox."""
        self.log.info("Setting log upload request", "for %s at %s" % (logFileLFN, targetSE))

        logUpload = Operation()
        logUpload.Type = "LogUpload"
        logUpload.TargetSE = targetSE

        logFile = File()
        logFile.LFN = logFileLFN

        logUpload.addFile(logFile)
        self.request.addOperation(logUpload)

        logRemoval = Operation()
        logRemoval.Type = "RemoveFile"
        logRemoval.TargetSE = uploadedSE

        logRemoval.addFile(logFile)
        self.request.addOperation(logRemoval)

    #############################################################################

    def __setLogFilePermissions(self, logDir):
        """Sets the permissions of all the files in the log directory to ensure
        they are readable."""
        try:
            for toChange in os.listdir(logDir):
                if not os.path.islink("%s/%s" % (logDir, toChange)):
                    self.log.debug("Changing permissions of %s/%s to 0755" % (logDir, toChange))
                    os.chmod(
                        "%s/%s" % (logDir, toChange),
                        stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH + stat.S_IXOTH,
                    )
        except OSError as x:
            self.log.error("Problem changing shared area permissions", str(x))
            return S_ERROR(x)

        return S_OK()


# EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#
