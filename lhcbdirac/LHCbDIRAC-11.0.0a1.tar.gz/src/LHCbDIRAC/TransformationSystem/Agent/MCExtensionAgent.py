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
"""An agent to extend MC productions based on the remaining events to
produce."""
import math
import datetime

from DIRAC import S_OK, S_ERROR
from DIRAC.ConfigurationSystem.Client.Helpers.Operations import Operations
from DIRAC.TransformationSystem.Agent.MCExtensionAgent import MCExtensionAgent as DIRACMCExtensionAgent
from LHCbDIRAC.ProductionManagementSystem.Client.ProductionRequestClient import ProductionRequestClient
from LHCbDIRAC.TransformationSystem.Client.TransformationClient import TransformationClient
from LHCbDIRAC.Workflow.Modules.ModulesUtilities import (
    getCPUNormalizationFactorAvg,
    getEventsToProduce,
    getProductionParameterValue,
)

AGENT_NAME = "Transformation/MCExtensionAgent"


class MCExtensionAgent(DIRACMCExtensionAgent):
    """MCExtensionAgent."""

    def __init__(self, *args, **kwargs):
        """c'tor."""
        DIRACMCExtensionAgent.__init__(self, *args, **kwargs)

        self.rpcProductionRequest = None
        self.transClient = None

        self.enableFlag = True

        # default values
        self.cpuE = 1
        self.cpuTimeAvg = 200000
        self.cpuNormalizationFactorAvg = 1.0

        # Artificial boost of the number of events requested to be created
        self.extensionFactorBoost = 20  # Meaning 20% more than what is calculated

    #############################################################################
    def initialize(self):
        """Logs some parameters and initializes the clients."""
        self.extensionFactorBoost = self.am_getOption("extensionFactorBoost", self.extensionFactorBoost)

        self.rpcProductionRequest = ProductionRequestClient()
        self.transClient = TransformationClient()

        self.log.info("Will consider the following transformation types: %s" % str(self.transformationTypes))
        self.log.info("Will create a maximum of %s tasks per iteration" % self.maxIterationTasks)

        return S_OK()

    #############################################################################
    def execute(self):
        """The MCExtensionAgent execution method."""

        self.enableFlag = self.am_getOption("EnableFlag", "True")
        if not self.enableFlag == "True":
            self.log.info("MCExtensionAgent is disabled by configuration option EnableFlag")
            return S_OK("Disabled via CS flag")

        # done every cycle, as they may have changed
        self._getCPUParameters()

        # get the production requests in which we are interested
        productionRequests = self.rpcProductionRequest.getProductionRequestSummary("Active", "Simulation")
        if productionRequests["OK"]:
            productionRequests = productionRequests["Value"]
            self.log.info("Requests considered: %s" % ", ".join([str(prod) for prod in productionRequests]))
        else:
            message = "RPC call to ProductionRequest service failed : %s" % productionRequests["Message"]
            self.log.error(message)
            return S_ERROR(message)

        for productionRequestID, productionRequestSummary in productionRequests.items():
            ret = self._checkProductionRequest(productionRequestID, productionRequestSummary)
            if not ret["OK"]:
                return ret

        return S_OK()

    #############################################################################

    def _getCPUParameters(self):
        """Get the CPUTimeAvg and CPUNormalizationFactorAvg from config, or as a
        fail-over, there are some defaults."""

        op = Operations()
        self.cpuTimeAvg = op.getValue("Transformations/cpuTimeAvg", self.cpuTimeAvg)
        self.log.verbose("cpuTimeAvg = %d" % self.cpuTimeAvg)

        try:
            self.cpuNormalizationFactorAvg = getCPUNormalizationFactorAvg()
            self.log.verbose("cpuNormalizationFactorAvg = %d" % self.cpuNormalizationFactorAvg)
        except RuntimeError:
            self.log.info(
                "Could not get CPUNormalizationFactorAvg from config, defaulting to %d" % self.cpuNormalizationFactorAvg
            )

    #############################################################################
    def _checkProductionRequest(self, productionRequestID, productionRequestSummary):
        """Check if a production request need to be extended and do it if
        needed."""

        # check if enough events have been produced
        missingEvents = productionRequestSummary["reqTotal"] - productionRequestSummary["bkTotal"]
        self.log.info("Missing events for production request %d: %d" % (productionRequestID, missingEvents))
        if productionRequestSummary["bkTotal"] > 0 and missingEvents <= 0:
            message = "Enough events produced for production request %d" % productionRequestID
            self.log.verbose(message)
            return S_OK(message)

        # get the associated productions/transformations progress
        productionsProgress = self.rpcProductionRequest.getProductionProgressList(int(productionRequestID))
        if productionsProgress["OK"]:
            productionsProgress = productionsProgress["Value"]
        else:
            message = "Failed to get productions progress : %s" % productionsProgress["Message"]
            self.log.error(message)
            return S_ERROR(message)
        productionsProgress = productionsProgress["Rows"]
        self.log.verbose("Progress for production request %d: %s" % (productionRequestID, str(productionsProgress)))

        # get the informations for the productions/transformations
        productions = []
        simulation = None
        for productionProgress in productionsProgress:
            productionID = productionProgress["ProductionID"]
            production = self.transClient.getTransformation(productionID)
            if not production["OK"]:
                message = "Failed to get informations on production %d : %s" % (productionID, production["Message"])
                self.log.error(message)
                return S_ERROR(message)
            production = production["Value"]
            productions.append(production)

            # determine which one is the simulation production
            if production["Type"] in self.transformationTypes:
                simulation = production
                simulationID = productionID
                for prodProgress in productionsProgress:
                    if prodProgress["ProductionID"] == simulationID:
                        simulationProgress = prodProgress
                        self.log.info(
                            "Progress for the simulation production %d of request %d: %s"
                            % (simulationID, productionRequestID, str(simulationProgress))
                        )

        if simulation is None:
            message = "Failed to get simulation production for request %d" % productionRequestID
            self.log.error(message)
            return S_ERROR(message)

        if simulation["Status"].lower() != "idle":
            # the simulation is still producing events
            message = "Simulation for production request %d is not Idle (%s)" % (
                productionRequestID,
                simulation["Status"],
            )
            self.log.verbose(message)
            return S_OK(message)

        # Checking how long ago this production became 'Idle'
        res = self.transClient.getTransformationLogging(simulationID)
        if not res["OK"]:
            return res
        lastLoggingEntry = res["Value"][-1]
        if ("idle" in lastLoggingEntry["Message"].lower()) and (
            (datetime.datetime.utcnow() - lastLoggingEntry["MessageDate"]).seconds < 900
        ):
            self.log.verbose("Prod %d is in 'Idle' for less than 15 minutes, waiting a bit" % simulationID)
            return S_OK("Prod %d is in 'Idle' for less than 15 minutes, waiting a bit" % simulationID)

        if simulationProgress["BkEvents"] < productionRequestSummary["reqTotal"]:
            # the number of events produced by the simulation is of the order of the number of events requested
            # -> there is probably no stripping production, no extension factor necessary
            return self._extendProduction(simulation, 1.0, missingEvents)
        else:
            # the number of events produced by the simulation is more than the number
            # of events requested, yet events are missing -> there is probably a
            # stripping production, an extension factor is needed to account for
            # stripped events some events may still be processed (eg. merged), so
            # wait that all the productions are idle
            if all(production["Status"].lower() == "idle" for production in productions):
                try:
                    extensionFactor = float(simulationProgress["BkEvents"]) / float(productionRequestSummary["bkTotal"])
                    return self._extendProduction(simulation, extensionFactor, missingEvents)
                except ZeroDivisionError:
                    return S_OK()
            else:
                return S_OK()

    #############################################################################
    def _extendProduction(self, production, extensionFactor, eventsNeeded):
        """Extends a production to produce eventsNeeded*extensionFactor more
        events."""
        productionID = production["TransformationID"]

        cpuEProd = getProductionParameterValue(production["Body"], "CPUe")
        if cpuEProd is None:
            self.log.warn("CPUe for transformation %d is not set, skipping for now" % productionID)
            return S_OK()
        cpuE = int(round(float(cpuEProd)))

        self.log.info(
            "Extending production %d, that is still missing %d events. \
                    Extension factor = %d, boost = %d"
            % (productionID, eventsNeeded, extensionFactor, self.extensionFactorBoost)
        )

        eventsToProduce = eventsNeeded * extensionFactor * (float(100 + self.extensionFactorBoost) / 100)
        max_e = getEventsToProduce(cpuE, self.cpuTimeAvg, self.cpuNormalizationFactorAvg)
        numberOfTasks = int(math.ceil(float(eventsToProduce) / float(max_e)))
        self.log.info("Extending production %d by %d tasks" % (productionID, numberOfTasks))

        # extend the transformation by the determined number of tasks
        res = self.transClient.extendTransformation(productionID, numberOfTasks)
        if not res["OK"]:
            message = "Failed to extend transformation %d : %s" % (productionID, res["Message"])
            self.log.error(message)
            return S_ERROR(message)
        else:
            message = "Successfully extended transformation %d by %d tasks" % (productionID, numberOfTasks)
            self.log.info(message)

            res = self.transClient.setTransformationParameter(productionID, "Status", "Active")
            if not res["OK"]:
                message = "Failed to set transformation %d to Active" % productionID
                self.log.error(message)
                return S_ERROR(message)

            return S_OK(message)
