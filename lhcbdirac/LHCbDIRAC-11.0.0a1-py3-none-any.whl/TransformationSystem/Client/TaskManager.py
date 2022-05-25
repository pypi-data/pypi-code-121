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
"""Extension of DIRAC Task Manager."""
from DIRAC.TransformationSystem.Client.WorkflowTasks import WorkflowTasks

COMPONENT_NAME = "LHCbTaskManager"


class LHCbWorkflowTasks(WorkflowTasks):
    """A simple LHCb extension to the task manager, for now only used to set the
    runNumber and runMetadata."""

    def _handleInputs(self, oJob, paramsDict):
        """set job inputs (+ metadata)"""
        try:
            if paramsDict["InputData"]:
                self.log.verbose("Setting input data to %s" % paramsDict["InputData"])
                self.log.verbose("Setting run number to %s" % str(paramsDict.get("RunNumber")))
                oJob.setInputData(paramsDict["InputData"], runNumber=paramsDict.get("RunNumber"))

                try:
                    runMetadata = paramsDict["RunMetadata"]
                    self.log.verbose("Setting run metadata information to %s" % str(runMetadata))
                    oJob.setRunMetadata(runMetadata)
                except KeyError:
                    pass

        except KeyError:
            self.log.exception("Could not find input data or a run number")
            raise KeyError("Could not found an input data or a run number")

    #############################################################################

    def _handleRest(self, oJob, paramsDict):
        """add as JDL parameters all the other parameters that are not for inputs
        or destination."""

        for paramName, paramValue in paramsDict.items():
            if paramName not in ("InputData", "RunNumber", "RunMetadata", "Site", "TargetSE"):
                if paramValue:
                    self.log.verbose("Setting %s to %s" % (paramName, paramValue))
                    oJob._addJDLParameter(paramName, paramValue)

    #############################################################################
