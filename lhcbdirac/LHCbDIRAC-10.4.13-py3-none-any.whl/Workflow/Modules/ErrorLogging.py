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
"""The ErrorLogging module is used to perform error analysis using AppConfig
utilities. This occurs at the end of each workflow step such that the
step_commons dictionary can be utilized.

Since not all projects are instrumented to work with the AppConfig error
suite any failures will not be propagated to the workflow.
"""
import os

from DIRAC import S_OK, S_ERROR, gLogger

import LHCbDIRAC
import LHCbDIRAC.Core.Utilities.LogErr as LogErr
from LHCbDIRAC.Workflow.Modules.ModuleBase import ModuleBase


class ErrorLogging(ModuleBase):

    #############################################################################

    def __init__(self):
        """c'tor."""

        self.log = gLogger.getSubLogger("ErrorLogging")
        super(ErrorLogging, self).__init__(self.log)

        self.version = LHCbDIRAC.version
        # Internal parameters
        self.errorLogNameHTML = ""
        self.errorLogNamejson = ""

    #############################################################################

    def _resolveInputVariables(self):
        """By convention the module input parameters are resolved here."""
        super(ErrorLogging, self)._resolveInputVariables()
        super(ErrorLogging, self)._resolveInputStep()

        self.errorLogNamejson = "%d_Errors_%s.json" % (self.jobID, self.applicationName)

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
        """Main execution function. Always return S_OK() because we don't want the
        job execution result to depend on retrieving errors from logs.

        This module will run regardless of the workflow status.
        """

        try:

            super(ErrorLogging, self).execute(
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

            self._resolveInputVariables()

            if self.applicationName.lower() not in ("gauss", "boole"):
                self.log.info("Not Gauss nor Boole, exiting")
                return S_OK()

            self.log.info(
                "Executing ErrorLogging module for: %s %s %s"
                % (self.applicationName, self.applicationVersion, self.applicationLog)
            )
            if not os.path.exists(self.applicationLog):
                self.log.info("Application log file from previous module not found locally: %s" % self.applicationLog)
                return S_OK()

            # Now really running
            # self.step_commons['extraPackages'] is something like 'AppConfig.v3r360;TurboStreamProd.v4r2p9;ProdConf'
            appConfigVersion = [
                x.split(".")[1] for x in self.step_commons["extraPackages"].split(";") if "AppConfig" in x
            ][0]
            result = LogErr.readLogFile(
                logFile=self.applicationLog,
                project=self.applicationName,
                version=self.applicationVersion,
                appConfigVersion=appConfigVersion,
                jobID=self.prod_job_id,
                prodID=self.production_id,
                wmsID=self.jobID,
                name=self.errorLogNamejson,
            )

            if not result["OK"]:
                self.log.error(
                    "Error logging for %s %s step %s completed with errors:"
                    % (self.applicationName, self.applicationVersion, self.step_number)
                )
                self.log.warn("Exiting without affecting workflow status")
                return S_OK()

            if not os.path.exists(self.errorLogNamejson):
                self.log.error(
                    "%s not found locally, exiting without affecting workflow status" % self.errorLogNamejson
                )
                return S_OK()

            self.log.info(
                "Error logging for %s %s step %s completed successfully:"
                % (self.applicationName, self.applicationVersion, self.step_number)
            )

            return S_OK()

        except Exception as e:
            self.log.exception("Failure in ErrorLogging execute module", lException=e)
            return S_ERROR("Error in ErrorLogging module")

        finally:
            super(ErrorLogging, self).finalize(self.version)
