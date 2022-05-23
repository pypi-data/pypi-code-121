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
"""OutputDataPolicy generates the output data that will be created by a
workflow task.

DIRAC assumes an execute() method will exist during usage.
"""
from DIRAC import gLogger
from LHCbDIRAC.Interfaces.API.LHCbJob import LHCbJob
from LHCbDIRAC.Core.Utilities.ProductionData import preSubmissionLFNs


class OutputDataPolicy(object):
    """class to generate the output Data."""

    def __init__(self, paramDict):
        """Constructor."""
        self.paramDict = paramDict

    def execute(self):
        """main loop."""
        jobDescription = self.paramDict["Job"]
        prodID = self.paramDict["TransformationID"]
        jobID = self.paramDict["TaskID"]

        job = LHCbJob(jobDescription)
        result = preSubmissionLFNs(job._getParameters(), job.workflow.createCode(), productionID=prodID, jobID=jobID)
        if not result["OK"]:
            gLogger.error(result)
        return result
