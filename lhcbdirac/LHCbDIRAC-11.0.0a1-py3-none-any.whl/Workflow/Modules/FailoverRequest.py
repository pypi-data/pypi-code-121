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
"""Create and send a combined request for any pending operations at the end of
a job:

fileReport (for the transformation) jobReport (for jobs) accounting
request (for failover)
"""
from DIRAC import S_OK, S_ERROR, gLogger

from LHCbDIRAC.Workflow.Modules.ModuleBase import ModuleBase


class FailoverRequest(ModuleBase):

    #############################################################################

    def __init__(self, bkClient=None, dm=None):
        """Module initialization."""

        self.log = gLogger.getSubLogger("FailoverRequest")
        super(FailoverRequest, self).__init__(self.log, bkClientIn=bkClient, dm=dm)

    #############################################################################

    def _resolveInputVariables(self):
        """By convention the module input parameters are resolved here."""
        super(FailoverRequest, self)._resolveInputVariables()
        super(FailoverRequest, self)._resolveInputStep()

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
    ):
        """Main execution function."""

        try:

            super(FailoverRequest, self).execute(
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

            if not self._enableModule():
                return S_OK()

            self._resolveInputVariables()

            # preparing the request, just in case
            self.request.RequestName = "job_%d_request.xml" % self.jobID
            self.request.JobID = self.jobID
            self.request.SourceComponent = "Job_%d" % self.jobID

            # report on the status of the input data, by default they are 'Processed', unless the job failed
            # failures happening before (e.g. in previous steps, or while inspecting the XML summary) are not touched.

            # The FileReport object is normally empty, unless there are some Problematic files,
            # or if there are files found to have descendants
            filesInFileReport = self.fileReport.getFiles()

            if not self._checkWFAndStepStatus(noPrint=True):
                # if the job fails, the input files will be reset to 'Unused'
                for lfn in self.inputDataList:
                    if lfn not in filesInFileReport:
                        self.log.info("Set status of input files to 'Unused' due to workflow failure", lfn)
                        self.fileReport.setFileStatus(int(self.production_id), lfn, "Unused")
            else:
                for lfn in self.inputDataList:
                    if lfn not in filesInFileReport:
                        self.log.verbose("No status populated for input data, setting to 'Processed'", lfn)
                        self.fileReport.setFileStatus(int(self.production_id), lfn, "Processed")

            res_fileReportCommit = self.fileReport.commit()
            # If there are still files to set, try a second time and generate a request if it fails again
            if not res_fileReportCommit["OK"]:
                self.log.error("Something went wrong trying fileReport.commit()", res_fileReportCommit["Message"])
            else:
                if res_fileReportCommit["Value"]:
                    self.log.info("Status of files have been properly updated in the TransformationDB")
                else:
                    self.log.warn("No file status update reported. There are no input files?")

            if self.fileReport.getFiles():
                self.log.error("On first attempt, failed to report file status to TransformationDB")
                # This will try a second time a commit, before generating a SetFileStatus operation
                result = self.fileReport.generateForwardDISET()
                if not result["OK"]:
                    self.log.warn(
                        "Could not generate Operation for file report", "with result:\n%s" % (result["Message"])
                    )
                else:
                    if result["Value"] is None:  # Means the FileReport managed to report, no need for a new operation
                        self.log.info("On second attempt, files correctly reported to TransformationDB")
                    else:
                        self.log.error("On second attempt, SetFileStatus definitely failed")
                        if self.workflowStatus["OK"] and self.stepStatus["OK"]:  # the job will be in "Completing"
                            self.log.info("Adding a SetFileStatus operation to the request")
                            self.request.addOperation(result["Value"])
                        else:
                            self.log.info("The job should fail: do not set requests, as the DRA will take care")

            # Must ensure that the local job report instance is used to report the final status
            # in case of failure and a subsequent failover operation
            if self.workflowStatus["OK"] and self.stepStatus["OK"]:
                self.setApplicationStatus("Job Finished Successfully")

            self.generateFailoverFile()

            return S_OK()

        except Exception as e:  # pylint:disable=broad-except
            self.log.exception("Failure in FailoverRequest execute module", lException=e)
            self.setApplicationStatus(repr(e))
            return S_ERROR(str(e))

        finally:
            super(FailoverRequest, self).finalize()


# EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#
