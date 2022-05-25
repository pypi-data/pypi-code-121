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
"""LHCbDIRAC.ResourceStatusSystem.Policy.TransferQualityPolicy.

TransferQualityPolicy.__bases__:
  DIRAC.ResourceStatusSystem.PolicySystem.PolicyBase.PolicyBase
"""
from DIRAC import S_OK
from DIRAC.ResourceStatusSystem.PolicySystem.PolicyBase import PolicyBase


class TransferQualityPolicy(PolicyBase):
    """The TransferQualityPolicy class is a policy class to check the transfer
    quality.

    Evaluates the TransferQuality results given by the
    DIRACAccounting.TransferQuality command against a certain set of
    thresholds defined in the CS.
    """

    @staticmethod
    def _evaluate(commandResult):
        """Evaluate policy on Data quality.

        :returns:
            {
              'Status':Error|Unknown|Active|Probing|Banned,
              'Reason':'TransferQuality:None'|'TransferQuality:xx%',
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

        if "Name" not in commandResult:
            result["Status"] = "Error"
            result["Reason"] = 'Missing "Name" key'
            return S_OK(result)

        name = commandResult["Name"]

        if "Mean" not in commandResult:
            result["Status"] = "Error"
            result["Reason"] = 'Missing "Mean" key'
            return S_OK(result)

        mean = commandResult["Mean"]

        if mean is None:
            result["Status"] = "Unknown"
            result["Reason"] = "No values to take a decision"
            return S_OK(result)

        result["Reason"] = "TransferQuality: %d -> " % mean

        # FIXME: policyParameters = Configurations.getPolicyParameters()

        policyParameters = {"Transfer_QUALITY_LOW": 60, "Transfer_QUALITY_HIGH": 90}

        if "FAILOVER".lower() in name.lower():

            if mean < policyParameters["Transfer_QUALITY_LOW"]:
                result["Status"] = "Degraded"
                strReason = "Low"
            elif mean < policyParameters["Transfer_QUALITY_HIGH"]:
                result["Status"] = "Active"
                strReason = "Mean"
            else:
                result["Status"] = "Active"
                strReason = "High"

        else:

            if mean < policyParameters["Transfer_QUALITY_LOW"]:
                result["Status"] = "Degraded"
                strReason = "Low"
            elif mean < policyParameters["Transfer_QUALITY_HIGH"]:
                result["Status"] = "Degraded"
                strReason = "Mean"
            else:
                result["Status"] = "Active"
                strReason = "High"

        result["Reason"] = result["Reason"] + strReason
        return S_OK(result)
