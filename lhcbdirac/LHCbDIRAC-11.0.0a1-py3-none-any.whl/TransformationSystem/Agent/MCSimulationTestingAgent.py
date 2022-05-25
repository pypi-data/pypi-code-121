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
"""An agent to check for MCSimulation productions that have undergone the
testing phase. Productions that have the status Idle and are also in the table
StoredJobDescription have undergone testing. A report is created by the agent
from the results of the test phase and emailed to the Production Manager.

Author: Simon Bidwell
"""

from DIRAC import S_OK, S_ERROR

from DIRAC.Core.Base.AgentModule import AgentModule
from DIRAC.Core.Workflow.Workflow import fromXMLString
from DIRAC.FrameworkSystem.Client.NotificationClient import NotificationClient
from DIRAC.ConfigurationSystem.Client.Helpers.Operations import Operations
from DIRAC.ConfigurationSystem.Client.Helpers.Registry import getUserOption

from LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient import BookkeepingClient
from LHCbDIRAC.ProductionManagementSystem.Client.Production import Production
from LHCbDIRAC.TransformationSystem.Client.TransformationClient import TransformationClient
from LHCbDIRAC.Workflow.Modules.ModulesUtilities import getEventsToProduce, getCPUNormalizationFactorAvg

AGENT_NAME = "Transformation/MCSimulationTestingAgent"


class MCSimulationTestingAgent(AgentModule):
    """An agent to check for MCSimulation productions that have undergone the
    testing phase.

    Productions that have the status Idle and are also in the table
    StoredJobDescription have undergone testing. A report is created by
    the agent from the results of the test phase and emailed to the
    Production Manager
    """

    def __init__(self, *args, **kwargs):
        """c'tor."""
        AgentModule.__init__(self, *args, **kwargs)
        self.transClient = None
        self.bkClient = None
        self.notifyClient = None
        self.operations = None

        self.failedTransIDs = []

    def initialize(self):
        self.transClient = TransformationClient()
        self.bkClient = BookkeepingClient()
        self.notifyClient = NotificationClient()
        self.operations = Operations()

        self.email = self.am_getOption("MailTo", "")

        return S_OK()

    def execute(self):
        # get all the idle transformations
        extendableTTypes = Operations().getValue("Transformations/ExtendableTransfTypes", ["MCSimulation"])
        res = self.transClient.getTransformations(condDict={"Status": "Idle", "Type": extendableTTypes})
        if res["OK"]:
            idleTransformations = res["Value"]
            idleTransformations = [d.get("TransformationID") for d in idleTransformations]
            self.log.verbose("Found %d Idle MC transformations" % len(idleTransformations))
            self.log.debug("Idle transformations found: %s" % ",".join([str(it) for it in idleTransformations]))
        else:
            self.log.error("Call to Transformation Client service failed", res["Message"])
            return res

        # get all the IDs of transformations undergoing a testing phase
        res = self.transClient.getStoredJobDescriptionIDs()
        if res["OK"]:
            testingSimulations = res["Value"]
            testingSimulations = [pair[0] for pair in testingSimulations]
            self.log.verbose("Found %d MC transformations undergoing a testing phase" % len(testingSimulations))
            self.log.debug(
                "MC transformations found undergoing a testing phase: %s"
                % ",".join([str(ts) for ts in testingSimulations])
            )
        else:
            self.log.error("Call to Transformation Client service failed", res["Message"])
            return res

        # get the IDs that occur in both idle transformations and testing phase
        idleSimulations = list(set(testingSimulations).intersection(idleTransformations))
        # remove those that we know failed
        idleSimulations = list(set(idleSimulations).difference(self.failedTransIDs))
        self.log.info(
            "MC transformations under considerations: %s (will loop on them)"
            % ",".join([str(idS) for idS in idleSimulations])
        )
        for transID in idleSimulations:
            self.log.info("Looking into %d" % transID)
            tasks = self.transClient.getTransformationTasks(condDict={"TransformationID": transID})
            if not tasks["OK"]:
                self.log.error("Call to Transformation Client service failed", tasks["Message"])
                continue
            else:
                tasks = tasks["Value"]
                numberOfTasks = len(tasks)
                numberOfDoneTasks = sum(1 for d in tasks if d.get("ExternalStatus") == "Done")
                self.log.verbose(
                    "TransID = %d, numberOfTasks = %d, numberOfDoneTasks = %d"
                    % (transID, numberOfTasks, numberOfDoneTasks)
                )
                if numberOfTasks == numberOfDoneTasks:
                    self.log.info("All tasks have passed so the request can be accepted and the transformation updated")
                    res = self._activateTransformation(transID, tasks)
                    if not res["OK"]:
                        self.log.error("Error Activating Production", res["Message"])
                else:
                    self.log.warn("There are failed tasks")
                    report = self.__createReport(tasks)
                    numberOfFailedTasks = sum(1 for d in tasks if d.get("ExternalStatus") == "Failed")
                    if numberOfFailedTasks == numberOfTasks:
                        # all tasks have failed so the request can be rejected and an email report sent
                        self._sendReport(report)
                        self.log.warn("Transformation " + str(transID) + " failed the testing phase")
                        self.failedTransIDs.append(transID)
                    else:
                        # only some tasks have failed so continue but send a warn email
                        self.log.warn(
                            "Transformation " + str(transID) + " failed partially the testing phase, continuing anyway"
                        )
                        doneTasks = list()
                        for d in tasks:
                            if d.get("ExternalStatus") == "Done":
                                doneTasks.append(d)
                        if not doneTasks:
                            self.log.info("No tasks done for Transformation %d" % transID)
                            continue
                        res = self._activateTransformation(transID, doneTasks)
                        if not res["OK"]:
                            self.log.error("Error Activating Production", res["Message"])
                            continue
                        subject = (
                            "MCSimulation Test Failure Report. TransformationID: "
                            + str(transID)
                            + " - some tasks failed"
                        )
                        report["subject"] = subject
                        self._sendReport(report)

        return S_OK()

    def _activateTransformation(self, transID, tasks):
        """Calculate parameters, update the workflow, then move the production to
        Active."""
        parameters = self._calculateParameters(tasks)
        if not parameters["OK"]:
            self.log.error("Error calculating parameters", parameters["Message"])
            return parameters
        else:
            parameters = parameters["Value"]
            self.log.verbose("TransID = %d, Calculated Parameters: %s" % (transID, str(parameters)))
            workflow = self._updateWorkflow(transID, int(round(float(parameters["CPUe"]))), parameters["MCCpu"])
            if workflow["OK"]:
                workflow = workflow["Value"]
                res = self._updateTransformationsTable(transID, workflow)
                if not res["OK"]:
                    self.log.error("Error updating transformations table", res["Message"])
                    return res
                else:
                    self.log.info(
                        "Transformation " + str(transID) + " passed the testing phase and is now set to active"
                    )

        return S_OK()

    def __createReport(self, tasks):
        """creates a report from a failed task to email to the production
        manager."""
        dateformat = "%d/%m/%Y %H:%M"
        transformationID = tasks[0]["TransformationID"]
        transformation = self.transClient.getTransformations(condDict={"TransformationID": transformationID})
        transformation = transformation["Value"][0]
        subject = "MCSimulation Test Failure Report. TransformationID: " + str(transformationID)
        body = [subject]
        body.append("")
        body.append("Transformation:")
        body.append("----------------------------------------------------------------------")
        body.append("TransformationID: " + str(transformation["TransformationID"]))
        body.append("TransformationName: " + transformation["TransformationName"])
        body.append("LastUpdate: " + transformation["LastUpdate"].strftime(dateformat))
        body.append("Status: " + transformation["Status"])
        body.append("Description: " + transformation["Description"])
        body.append("TransformationFamily: " + str(transformation["TransformationFamily"]))
        body.append("Plugin: " + transformation["Plugin"])
        body.append("Type: " + transformation["Type"])
        body.append("AgentType: " + transformation["AgentType"])
        body.append("GroupSize: " + str(transformation["GroupSize"]))
        body.append("MaxNumberOfTasks: " + str(transformation["MaxNumberOfTasks"]))
        body.append("AuthorDN: " + transformation["AuthorDN"])
        body.append("TransformationGroup: " + transformation["TransformationGroup"])
        body.append("InheritedFrom: " + str(transformation["InheritedFrom"]))
        body.append("CreationDate: " + transformation["CreationDate"].strftime(dateformat))
        body.append("FileMask: " + transformation["FileMask"])
        body.append("EventsPerTask: " + str(transformation["EventsPerTask"]))
        body.append("AuthorGroup: " + transformation["AuthorGroup"])
        body.append("")
        body.append("Number of Tasks: " + str(len(tasks)))
        body.append("Tasks:")
        body.append("----------------------------------------------------------------------")
        for task in tasks:
            body.append("TaskID: " + str(task["TaskID"]))
            body.append("TargetSE: " + task["TargetSE"])
            body.append("LastUpdateTime: " + task["LastUpdateTime"].strftime(dateformat))
            body.append("RunNumber: " + str(task.get("RunNumber", 0)))
            body.append("CreationTime: " + task["CreationTime"].strftime(dateformat))
            body.append("ExternalID: " + str(task["ExternalID"]))
            body.append("ExternalStatus: " + task["ExternalStatus"])
            body.append("")
        return {"subject": subject, "body": body}

    def _sendReport(self, report):
        """sends a given report to the production manager."""
        if not self.email:
            self.email = getUserOption(self.operations.getValue("Shifter/ProductionManager/User"), "Email")
        body = "\n".join(report["body"])
        res = self.notifyClient.sendMail(self.email, report["subject"], body, self.email, localAttempt=False)
        if not res["OK"]:
            self.log.error("sendMail failed", res["Message"])
        else:
            self.log.info("Mail summary sent to production manager")

    def _calculateParameters(self, tasks):
        """Calculates the CPU time per event for the production."""
        jobIds = [int(x["ExternalID"]) for x in tasks]
        res = self.bkClient.bulkJobInfo({"jobId": jobIds})
        if not res["OK"]:
            self.log.error("Error calling bkClient", res["Message"])
            return S_ERROR(res["Message"])
        successful = res["Value"]["Successful"]
        self.log.debug("Successful tasks: %s" % str(successful))
        if not successful:
            self.log.error("There are no successful tasks")
            return S_ERROR("There are no successful tasks")

        successfulJobs = len(successful)

        CPUeJobTotal = 0.0
        for job in successful.values():
            cpuJob = 0
            for bkJob in job:
                if bkJob["ApplicationName"] in ["Gauss", "Boole", "Moore", "Brunel", "DaVinci"]:
                    if bkJob["ApplicationName"] == "Gauss":
                        events = bkJob["NumberOfEvents"]  # This must be there
                    timeInSeconds = bkJob["CPUTIME"]
                    cpuJob += timeInSeconds * bkJob["WNCPUHS06"]
            if not events:  # extreme case of no events produced
                successfulJobs -= 1
                continue
            CPUeJob = cpuJob / events
            self.log.debug("CPUeJob = %d" % CPUeJob)

            CPUeJobTotal += CPUeJob

        CPUe = CPUeJobTotal / successfulJobs
        # We want to produce at least 25 events per job...
        MCCpu = str(25 * int(round(float(CPUe))))
        self.log.verbose("CPUe = %d, MCCpu = %s" % (CPUe, MCCpu))
        return S_OK({"CPUe": CPUe, "MCCpu": MCCpu})

    def _updateWorkflow(self, transID, CPUe, MCCpu):
        """Updates the workflow of a savedProductionDescription to reflect the
        calculated CPUe."""
        res = self.transClient.getStoredJobDescription(transID)
        if res["OK"]:
            workflow = fromXMLString(res["Value"][0][1])
            prod = Production()
            prod.LHCbJob.workflow = workflow
            prod.setParameter("CPUe", "string", str(CPUe), "CPU time per event")
            prod.LHCbJob.setCPUTime(MCCpu)
            self.log.info("Transformation ", str(transID))
            self.log.info("Calculated CPUTime: ", str(CPUe))
            self.log.info("CpuTime: ", str(MCCpu))

            # maximum number of events to produce
            # try to get the CPU parameters from the configuration if possible
            cpuTimeAvg = Operations().getValue("Transformations/CPUTimeAvg")
            if cpuTimeAvg is None:
                self.log.info("Could not get CPUTimeAvg from config, defaulting to %d" % 200000)
                cpuTimeAvg = 200000

            try:
                CPUNormalizationFactorAvg = getCPUNormalizationFactorAvg()
            except RuntimeError:
                self.log.info("Could not get CPUNormalizationFactorAvg, defaulting to %f" % 1.0)
                CPUNormalizationFactorAvg = 1.0

            max_e = getEventsToProduce(CPUe, cpuTimeAvg, CPUNormalizationFactorAvg)
            prod.setParameter("maxNumberOfEvents", "string", str(max_e), "Maximum number of events to produce (Gauss)")
            return S_OK(prod.LHCbJob.workflow.toXML())
        else:
            self.log.error("Call to Transformation Client service failed", res["Message"])
            return res

    def _updateTransformationsTable(self, transID, workflow):
        """Puts the modified workflow from the savedProductionDescription table
        into the transformations table and removes it from the
        savedProductionDescription table."""
        transformation = self.transClient.getTransformations(condDict={"TransformationID": transID})
        if transformation["OK"]:
            body = self.transClient.setTransformationParameter(transID, "Body", workflow)
            status = self.transClient.setTransformationParameter(transID, "Status", "Active")
            if body["OK"] and status["OK"]:
                res = self.transClient.removeStoredJobDescription(transID)
                if not res["OK"]:
                    self.log.error("Call to removeStoredJobDescription failed", res["Message"])
                    return res
                self.log.info("Transformation %s has an updated body and Status set to active" % transID)
                return S_OK()
            else:
                self.log.error(
                    "One of the updates has failed so set them both back to the previous value to ensure atomicity"
                )
                self.log.debug(str(transformation["Value"][0]["Body"]))
                res = self.transClient.setTransformationParameter(transID, "Body", transformation["Value"][0]["Body"])
                if not res["OK"]:
                    self.log.error("Failure calling setTransformationParameter", res["Message"])
                    return res
                res = self.transClient.setTransformationParameter(
                    transID, "Status", transformation["Value"][0]["Status"]
                )
                if not res["OK"]:
                    self.log.error("Failure calling setTransformationParameter", res["Message"])
                    return res
        else:
            self.log.error("Call to getTransformations failed", transformation["Message"])
            return transformation
