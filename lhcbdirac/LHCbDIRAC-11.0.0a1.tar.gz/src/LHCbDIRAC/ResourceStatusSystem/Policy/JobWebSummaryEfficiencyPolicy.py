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
"""LHCbDIRAC.ResourceStatusSystem.Policy.JobEfficiencyPolicy.

JobWebSummaryEfficiencyPolicy.__bases__:
  DIRAC.ResourceStatusSystem.PolicySystem.PolicyBase.PolicyBase
"""
from DIRAC import S_OK
from DIRAC.ResourceStatusSystem.PolicySystem.PolicyBase import PolicyBase


class JobWebSummaryEfficiencyPolicy(PolicyBase):
    """The JobEfficiencyPolicy class is a policy that checks the efficiency of
    the jobs according to what is on WMS.

    Evaluates the JobEfficiency results given by the JobCommand.JobCommand
    """

    @staticmethod
    def _evaluate(commandResult):
        """Evaluate policy on jobs stats, using args (tuple).

        :returns:
          {
            'Status':Unknown|Active|Probing|Bad,
            'Reason':'JobsEff:Good|JobsEff:Fair|JobsEff:Poor|JobsEff:Bad|JobsEff:Idle',
          }
        """

        result = {"Status": None, "Reason": None}

        if not commandResult["OK"]:
            result["Status"] = "Error"
            result["Reason"] = commandResult["Message"]
            return S_OK(result)

        commandResult = commandResult["Value"]

        if not commandResult:
            result["Status"] = "Unknown"
            result["Reason"] = "No values to take a decision"
            return S_OK(result)

        # The command returns a list of dictionaries, with only one if thre is something,
        # otherwise an empty list.
        commandResult = commandResult[0]

        if "Status" not in commandResult:
            result["Status"] = "Error"
            result["Reason"] = '"Status" key missing'
            return S_OK(result)

        if "Efficiency" not in commandResult:
            result["Status"] = "Error"
            result["Reason"] = '"Efficiency" key missing'
            return S_OK(result)

        status = commandResult["Status"]
        efficiency = commandResult["Efficiency"]

        if status == "Good":
            result["Status"] = "Active"
        elif status == "Fair":
            result["Status"] = "Active"
        elif status == "Poor":
            result["Status"] = "Degraded"
        elif status == "Idle":
            result["Status"] = "Unknown"
        elif status == "Bad":
            result["Status"] = "Banned"
        else:
            result["Status"] = "Error"
            result["Reason"] = 'Unknown status "%s"' % status
            return S_OK(result)

        result["Reason"] = "Jobs Efficiency: %s with status %s" % (efficiency, status)

        return S_OK(result)
