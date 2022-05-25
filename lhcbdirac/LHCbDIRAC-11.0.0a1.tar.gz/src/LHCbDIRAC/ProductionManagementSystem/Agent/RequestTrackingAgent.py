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
"""Production requests agent perform all periodic task with requests.

Currently it updates the number of Input Events for processing productions.
"""
from DIRAC import S_OK, S_ERROR, gLogger
from DIRAC.Core.Base.AgentModule import AgentModule
from LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient import BookkeepingClient
from LHCbDIRAC.ProductionManagementSystem.Client.ProductionRequestClient import ProductionRequestClient

AGENT_NAME = "ProductionManagement/RequestTrackingAgent"


class RequestTrackingAgent(AgentModule):
    def __init__(self, *args, **kwargs):
        """c'tor."""
        AgentModule.__init__(self, *args, **kwargs)

        self.bkClient = None
        self.prodReq = None

    def initialize(self):
        """Just initializing the clients."""
        self.bkClient = BookkeepingClient()
        self.prodReq = ProductionRequestClient()

        return S_OK()

    def execute(self):
        """The RequestTrackingAgent execution method."""
        result = self.prodReq.getTrackedInput()
        update = []
        if result["OK"]:
            gLogger.verbose("Requests tracked: %s" % (",".join([str(req["RequestID"]) for req in result["Value"]])))
            for request in result["Value"]:
                result = self.bkInputNumberOfEvents(request)
                if result["OK"]:
                    update.append({"RequestID": request["RequestID"], "RealNumberOfEvents": result["Value"]})
                else:
                    gLogger.error("Input of %s is not updated: %s" % (str(request["RequestID"]), result["Message"]))
        else:
            gLogger.error("Request service: %s" % result["Message"])
        if update:
            result = self.prodReq.updateTrackedInput(update)
            if not result["OK"]:
                gLogger.error(result["Message"])

        return S_OK("Request Tracking information updated")

    def bkInputNumberOfEvents(self, request):
        """Extremely dirty way..."""
        dq = request.get("inDataQualityFlag", "ALL")
        if dq != "ALL":
            dq = [str(idq) for idq in dq.replace(" ", "").split(",")]
        try:
            condition = {
                "ProcessingPass": str(request.get("inProPass", "")).strip(),
                "FileType": [str(ift) for ift in request.get("inFileType", "").replace(" ", "").split(",")],
                "EventType": str(request.get("EventType", "")).replace(" ", ""),
                "ConfigName": str(request.get("configName", "")).replace(" ", ""),
                "ConfigVersion": str(request.get("configVersion", "")).replace(" ", ""),
                "DataQualityFlag": dq,
            }
        except KeyError as ke:
            gLogger.error("%s is incomplete: %s" % (request["RequestID"], repr(ke)))
            return S_ERROR(repr(ke))

        if "condType" in request and request["condType"] == "Run":
            condition["DataTakingConditions"] = str(request["SimCondition"])
        else:
            condition["SimulationConditions"] = str(request["SimCondition"])
        if str(request["inProductionID"]) not in ("0", "ALL"):
            condition["Production"] = [int(x) for x in str(request["inProductionID"]).split(",")]
        if "inTCKs" in request and str(request["inTCKs"]) != "":
            condition["TCK"] = [str(x) for x in str(request["inTCKs"]).split(",")]
        condition["NbOfEvents"] = True

        gLogger.verbose("Requesting: ", str(condition))
        result = self.bkClient.getFiles(condition)
        if not result["OK"]:
            gLogger.error("Error requesting files from BK", result["Message"])
            return result
        if not result["Value"][0]:
            return S_OK(0)
        try:
            sum_nr = int(result["Value"][0])
        except ValueError as e:
            return S_ERROR("Can not convert result from BK call: %s" % str(e))
        return S_OK(sum_nr)
