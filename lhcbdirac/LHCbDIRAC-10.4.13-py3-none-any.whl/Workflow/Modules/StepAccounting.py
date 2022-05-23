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
"""StepAccounting module performs several common operations at the end of a
workflow step, in particular prepares and sends the step accounting data."""
from DIRAC import S_OK, S_ERROR, gConfig, gLogger
from DIRAC.Core.Utilities import Time
from DIRAC.Workflow.Utilities.Utils import getStepCPUTimes

import LHCbDIRAC
from LHCbDIRAC.Workflow.Modules.ModuleBase import ModuleBase
from LHCbDIRAC.AccountingSystem.Client.Types.JobStep import JobStep


class StepAccounting(ModuleBase):
    """StepAccounting class."""

    def __init__(self, bkClient=None, dm=None):

        self.log = gLogger.getSubLogger("StepAccounting")
        super(StepAccounting, self).__init__(self.log, bkClientIn=bkClient, dm=dm)

        self.dsc = None
        self.stepStat = None

        self.version = LHCbDIRAC.version

    ########################################################################

    def _resolveInputVariables(self, dsc=None):
        """By convention all workflow parameters are resolved here."""

        super(StepAccounting, self)._resolveInputVariables()
        super(StepAccounting, self)._resolveInputStep()

        if dsc is not None:
            self.dsc = dsc
        else:
            self.dsc = self.workflow_commons["AccountingReport"]

        if self.stepStatus["OK"]:
            self.stepStat = "Done"
        else:
            self.stepStat = "Failed"

    ########################################################################

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
        js=None,
        xf_o=None,
        dsc=None,
    ):

        try:
            super(StepAccounting, self).execute(
                self.version,
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

            # Check if the step is worth accounting
            if "applicationName" not in self.step_commons:
                self.log.info("Not an application step: it will not be accounted")
                return S_OK()

            ########################################################################
            # Timing
            execTime, cpuTime = getStepCPUTimes(self.step_commons)
            normCPU = cpuTime
            cpuNormFactor = gConfig.getValue("/LocalSite/CPUNormalizationFactor", 0.0)
            if cpuNormFactor:
                normCPU = cpuTime * cpuNormFactor

            if not js:
                jobStep = JobStep()
            else:
                jobStep = js

            if not xf_o:
                try:
                    xf_o = self.step_commons["XMLSummary_o"]
                except KeyError:
                    self.log.error("XML Summary object could not be found (not produced?), skipping the report")
                    return S_OK()

            self._resolveInputVariables(dsc)

            now = Time.dateTime()
            jobStep.setStartTime(now)
            jobStep.setEndTime(now)

            dataDict = {
                "JobGroup": str(self.production_id),
                "RunNumber": self.runNumber,
                "EventType": self.eventType,
                "ProcessingType": self.stepProcPass,  # this is the processing pass of the step
                "ProcessingStep": self.BKstepID,  # the step ID
                "Site": self.siteName,
                "FinalStepState": self.stepStat,
                "CPUTime": cpuTime,
                "NormCPUTime": normCPU,
                "ExecTime": execTime * self.numberOfProcessors,
                "InputData": sum(xf_o.inputFileStats.values()),
                "OutputData": sum(xf_o.outputFileStats.values()),
                "InputEvents": xf_o.inputEventsTotal,
                "OutputEvents": xf_o.outputEventsTotal,
            }

            jobStep.setValuesFromDict(dataDict)

            res = jobStep.checkValues()
            if not res["OK"]:
                self.log.error("Values for StepAccounting are wrong", res["Message"], dataDict)
                return S_ERROR("Values for StepAccounting are wrong")

            if not self._enableModule():
                self.log.info("Not enabled, would have accounted for %s" % dataDict)
                return S_OK()

            self.dsc.addRegister(jobStep)

            return S_OK()

        except Exception as e:  # pylint:disable=broad-except
            self.log.exception("Failure in StepAccounting execute module", lException=e)
            return S_ERROR(str(e))

        finally:
            super(StepAccounting, self).finalize(self.version)
