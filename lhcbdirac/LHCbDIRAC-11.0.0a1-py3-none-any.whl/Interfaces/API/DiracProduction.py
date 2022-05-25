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
"""DIRAC Production Management Class.

This class allows to monitor the progress of productions operationally.

Of particular use are the monitoring functions allowing to drill down
by site, minor status and application status for a given transformation.
"""
import os
import six

from DIRAC import gLogger, S_OK, S_ERROR
from DIRAC.Core.Utilities.Time import toString
from DIRAC.Core.Utilities.PromptUser import promptUser
from DIRAC.WorkloadManagementSystem.Client.JobMonitoringClient import JobMonitoringClient

from LHCbDIRAC.Interfaces.API.DiracLHCb import DiracLHCb
from LHCbDIRAC.TransformationSystem.Client.TransformationClient import TransformationClient


class DiracProduction(DiracLHCb):
    """class for managing productions."""

    def __init__(self, tsClientIn=None):
        """Instantiates the Workflow object and some default parameters."""

        super(DiracProduction, self).__init__()

        if tsClientIn is None:
            self.transformationClient = TransformationClient()
        else:
            self.transformationClient = tsClientIn

        self.prodHeaders = {
            "AgentType": "SubmissionMode",
            "Status": "Status",
            "CreationDate": "Created",
            "TransformationName": "Name",
            "Type": "Type",
        }
        self.prodAdj = 22
        self.commands = {
            "start": ["Active", "Manual"],
            "stop": ["Stopped", "Manual"],
            "automatic": ["Active", "Automatic"],
            "manual": ["Active", "Manual"],
            "mctestmode": ["Testing", "Automatic"],
            "completed": ["Completed", "Manual"],
            "completing": ["Completing", "Automatic"],
            "cleaning": ["Cleaning", "Manual"],
            "flush": ["Flush", "Automatic"],
            "deleted": ["Deleted", "Manual"],
            "cleaned": ["Cleaned", "Manual"],
            "archived": ["Archived", "Manual"],
            "valinput": ["ValidatingInput", "Manual"],
            "valoutput": ["ValidatingOutput", "Manual"],
            "remove": ["RemovingFiles", "Manual"],
            "validated": ["ValidatedOutput", "Manual"],
            "removed": ["RemovedFiles", "Manual"],
        }

    def getProduction(self, productionID, printOutput=False):
        """Returns the metadata associated with a given production ID.

        Protects against
        LFN: being prepended and different types of production ID.
        """
        if not isinstance(productionID, (six.integer_types, six.string_types)):
            return self._errorReport("Expected string, long or int for production ID")

        result = self.transformationClient.getTransformation(int(productionID))
        if not result["OK"]:
            return result

        # to fix TODO
        if printOutput:
            adj = self.prodAdj
            prodInfo = result["Value"]
            top = ""
            for i in self.prodHeaders.values():
                top += i.ljust(adj)
            message = ["ProductionID".ljust(adj) + top + "\n"]
            # very painful to make this consistent, better improved first on the server side
            productionID = str(productionID)
            info = (
                productionID.ljust(adj)
                + prodInfo["Status"].ljust(adj)
                + prodInfo["Type"].ljust(adj)
                + prodInfo["AgentType"].ljust(adj)
                + toString(prodInfo["CreationDate"]).ljust(adj)
                + prodInfo["TransformationName"].ljust(adj)
            )
            message.append(info)
            print("\n".join(message))
        return S_OK(result["Value"])

    def getProductionLoggingInfo(self, productionID, printOutput=False):
        """The logging information for the given production is returned.

        This includes the operation performed, any messages associated with
        the operation and the DN of the production manager performing it.
        """
        if not isinstance(productionID, (six.integer_types, six.string_types)):
            return self._errorReport("Expected string, long or int for production ID")

        result = self.transformationClient.getTransformationLogging(int(productionID))
        if not result["OK"]:
            self.log.warn("Could not get transformation logging information for productionID %s" % (productionID))
            return result
        if not result["Value"]:
            self.log.warn("No logging information found for productionID %s" % (productionID))
            return result

        if not printOutput:
            return result

        infoM = (
            "ProdID".ljust(int(0.5 * self.prodAdj))
            + "Message".ljust(3 * self.prodAdj)
            + "DateTime [UTC]".ljust(self.prodAdj)
            + "AuthorCN".ljust(2 * self.prodAdj)
        )
        message = [infoM]
        for line in result["Value"]:
            infoL = (
                str(line["TransformationID"]).ljust(int(0.5 * self.prodAdj))
                + line["Message"].ljust(3 * self.prodAdj)
                + toString(line["MessageDate"]).ljust(self.prodAdj)
                + line["AuthorDN"].split("/")[-1].ljust(2 * self.prodAdj)
            )
            message.append(infoL)

        print("\nLogging summary for productionID " + str(productionID) + "\n\n" + "\n".join(message))

        return result

    def getProductionSummary(self, productionID=None, printOutput=False):
        """Returns a detailed summary for the productions in the system.

        If production ID is specified, the result is restricted to this
        value. If printOutput is specified, the result is printed to the
        screen.
        """
        if not isinstance(productionID, (six.integer_types, six.string_types)):
            return self._errorReport("Expected string, long or int for production ID")

        result = self.transformationClient.getTransformationSummary()
        if not result["OK"]:
            return result

        if productionID:
            if int(productionID) in result["Value"]:
                newResult = S_OK()
                newResult["Value"] = {}
                newResult["Value"][int(productionID)] = result["Value"][int(productionID)]
                result = newResult
            else:
                self.log.info(
                    "Specified productionID was not found, \
          the list of active productions is:\n%s"
                    % ", ".join(str(pID) for pID in result["Value"])
                )
                return S_ERROR("Production ID %s was not found" % (productionID))

        if printOutput:
            self._prettyPrint(result["Value"])

        return result

    def getProductionApplicationSummary(self, productionID, status=None, minorStatus=None, printOutput=False):
        """Returns an application status summary for the productions in the system.

        If printOutput is specified, the result is printed to the screen.
        This queries the WMS for the given productionID and provides an up-
        to-date snapshot of the application status combinations and
        associated WMS JobIDs.
        """
        if not isinstance(productionID, (six.integer_types, six.string_types)):
            return self._errorReport("Expected string, long or int for production ID")

        statusDict = self.getProdJobMetadata(productionID, status, minorStatus)
        if not statusDict["OK"]:
            self.log.warn("Could not get production metadata information")
            return statusDict

        jobIDs = list(statusDict["Value"])
        if not jobIDs:
            return S_ERROR("No JobIDs with matching conditions found")

        self.log.verbose("Considering %s jobs with selected conditions" % (len(jobIDs)))
        # now need to get the application status information
        result = JobMonitoringClient().getJobsApplicationStatus(jobIDs)
        if not result["OK"]:
            self.log.warn("Could not get application status for jobs list")
            return result

        appStatus = result["Value"]
        #    self._prettyPrint(appStatus)
        #    self._prettyPrint(statusDict['Value'])
        # Now format the result.
        summary = {}
        submittedJobs = 0
        doneJobs = 0
        for job, atts in statusDict["Value"].items():
            for key, val in atts.items():
                if key == "Status":
                    uniqueStatus = val.capitalize()
                    if uniqueStatus not in summary:
                        summary[uniqueStatus] = {}
                    if atts["MinorStatus"] not in summary[uniqueStatus]:
                        summary[uniqueStatus][atts["MinorStatus"]] = {}
                    if appStatus[job]["ApplicationStatus"] not in summary[uniqueStatus][atts["MinorStatus"]]:
                        summary[uniqueStatus][atts["MinorStatus"]][appStatus[job]["ApplicationStatus"]] = {}
                        summary[uniqueStatus][atts["MinorStatus"]][appStatus[job]["ApplicationStatus"]]["Total"] = 1
                        submittedJobs += 1
                        if uniqueStatus == "Done":
                            doneJobs += 1
                        summary[uniqueStatus][atts["MinorStatus"]][appStatus[job]["ApplicationStatus"]]["JobList"] = [
                            job
                        ]
                    else:
                        if appStatus[job]["ApplicationStatus"] not in summary[uniqueStatus][atts["MinorStatus"]]:
                            summary[uniqueStatus][atts["MinorStatus"]] = {}
                            summary[uniqueStatus][atts["MinorStatus"]][appStatus[job]["ApplicationStatus"]] = {}
                            summary[uniqueStatus][atts["MinorStatus"]][appStatus[job]["ApplicationStatus"]]["Total"] = 1
                            submittedJobs += 1
                            if uniqueStatus == "Done":
                                doneJobs += 1
                            summary[uniqueStatus][atts["MinorStatus"]][appStatus[job]["ApplicationStatus"]][
                                "JobList"
                            ] = [job]
                        else:
                            current = summary[uniqueStatus][atts["MinorStatus"]][appStatus[job]["ApplicationStatus"]][
                                "Total"
                            ]
                            summary[uniqueStatus][atts["MinorStatus"]][appStatus[job]["ApplicationStatus"]]["Total"] = (
                                current + 1
                            )
                            submittedJobs += 1
                            if uniqueStatus == "Done":
                                doneJobs += 1
                            jobList = summary[uniqueStatus][atts["MinorStatus"]][appStatus[job]["ApplicationStatus"]][
                                "JobList"
                            ]
                            jobList.append(job)
                            summary[uniqueStatus][atts["MinorStatus"]][appStatus[job]["ApplicationStatus"]][
                                "JobList"
                            ] = jobList

        if not printOutput:
            result = S_OK()
            if not status and not minorStatus:
                result["Totals"] = {"Submitted": int(submittedJobs), "Done": int(doneJobs)}
            result["Value"] = summary
            return result

        # If a printed summary is requested
        statAdj = int(0.5 * self.prodAdj)
        mStatAdj = int(2.0 * self.prodAdj)
        totalAdj = int(0.5 * self.prodAdj)
        exAdj = int(0.5 * self.prodAdj)
        message = "\nJob Summary for ProductionID %s considering status %s" % (productionID, status)
        if minorStatus:
            message += "and MinorStatus = %s" % (minorStatus)

        message += ":\n\n"
        message += (
            "Status".ljust(statAdj)
            + "MinorStatus".ljust(mStatAdj)
            + "ApplicationStatus".ljust(mStatAdj)
            + "Total".ljust(totalAdj)
            + "Example".ljust(exAdj)
            + "\n"
        )
        for stat, metadata in summary.items():
            message += "\n"
            for minor, appInfo in metadata.items():
                message += "\n"
                for appStat, jobInfo in appInfo.items():
                    message += (
                        stat.ljust(statAdj)
                        + minor.ljust(mStatAdj)
                        + appStat.ljust(mStatAdj)
                        + str(jobInfo["Total"]).ljust(totalAdj)
                        + str(jobInfo["JobList"][0]).ljust(exAdj)
                        + "\n"
                    )

        # self._prettyPrint(summary)
        if status or minorStatus:
            return S_OK(summary)

        result = self.getProductionProgress(productionID)
        if not result["OK"]:
            self.log.warn("Could not get production progress information")
            return result

        if "Created" in result["Value"]:
            createdJobs = int(result["Value"]["Created"]) + submittedJobs
        else:
            createdJobs = submittedJobs

        percSub = int(100 * submittedJobs / createdJobs)
        percDone = int(100 * doneJobs / createdJobs)
        print("\nCurrent status of production %s:\n" % productionID)
        print(
            "Submitted".ljust(12)
            + str(percSub).ljust(3)
            + "%  ( "
            + str(submittedJobs).ljust(7)
            + "Submitted / ".ljust(15)
            + str(createdJobs).ljust(7)
            + " Created jobs )"
        )
        print(
            "Done".ljust(12)
            + str(percDone).ljust(3)
            + "%  ( "
            + str(doneJobs).ljust(7)
            + "Done / ".ljust(15)
            + str(createdJobs).ljust(7)
            + " Created jobs )"
        )
        result = S_OK()
        result["Totals"] = {"Submitted": int(submittedJobs), "Created": int(createdJobs), "Done": int(doneJobs)}
        result["Value"] = summary
        # self.pPrint(result)
        return result

    def getProductionJobSummary(self, productionID, status=None, minorStatus=None, printOutput=False):
        """Returns a job summary for the productions in the system.

        If printOutput is specified, the result is printed to the screen.
        This queries the WMS for the given productionID and provides an up-
        to-date snapshot of the job status combinations and associated WMS
        JobIDs.
        """
        if not isinstance(productionID, (six.integer_types, six.string_types)):
            return self._errorReport("Expected string, long or int for production ID")

        statusDict = self.getProdJobMetadata(productionID, status, minorStatus)
        if not statusDict["OK"]:
            self.log.warn("Could not get production metadata information")
            return statusDict

        # Now format the result.
        summary = {}
        submittedJobs = 0
        doneJobs = 0
        for job, atts in statusDict["Value"].ietritems():
            for key, val in atts.items():
                if key == "Status":
                    uniqueStatus = val.capitalize()
                    if uniqueStatus not in summary:
                        summary[uniqueStatus] = {}
                    if atts["MinorStatus"] not in summary[uniqueStatus]:
                        summary[uniqueStatus][atts["MinorStatus"]] = {}
                        summary[uniqueStatus][atts["MinorStatus"]]["Total"] = 1
                        submittedJobs += 1
                        if uniqueStatus == "Done":
                            doneJobs += 1
                        summary[uniqueStatus][atts["MinorStatus"]]["JobList"] = [job]
                    else:
                        current = summary[uniqueStatus][atts["MinorStatus"]]["Total"]
                        summary[uniqueStatus][atts["MinorStatus"]]["Total"] = current + 1
                        submittedJobs += 1
                        if uniqueStatus == "Done":
                            doneJobs += 1
                        jobList = summary[uniqueStatus][atts["MinorStatus"]]["JobList"]
                        jobList.append(job)
                        summary[uniqueStatus][atts["MinorStatus"]]["JobList"] = jobList

        if not printOutput:
            result = S_OK()
            if not status and not minorStatus:
                result["Totals"] = {"Submitted": int(submittedJobs), "Done": int(doneJobs)}
            result["Value"] = summary
            return result

        # If a printed summary is requested
        statAdj = int(0.5 * self.prodAdj)
        mStatAdj = int(2.0 * self.prodAdj)
        totalAdj = int(0.5 * self.prodAdj)
        exAdj = int(0.5 * self.prodAdj)
        message = "\nJob Summary for ProductionID %s considering" % (productionID)
        if status:
            message += " Status = %s" % (status)
        if minorStatus:
            message += " MinorStatus = %s" % (minorStatus)
        if not status and not minorStatus:
            message += " all status combinations"

        message += ":\n\n"
        message += (
            "Status".ljust(statAdj)
            + "MinorStatus".ljust(mStatAdj)
            + "Total".ljust(totalAdj)
            + "Example".ljust(exAdj)
            + "\n"
        )
        for stat, metadata in summary.items():
            message += "\n"
            for minor, jobInfo in metadata.items():
                message += (
                    stat.ljust(statAdj)
                    + minor.ljust(mStatAdj)
                    + str(jobInfo["Total"]).ljust(totalAdj)
                    + str(jobInfo["JobList"][0]).ljust(exAdj)
                    + "\n"
                )

        print(message)
        # self._prettyPrint(summary)
        if status or minorStatus:
            return S_OK(summary)

        result = self.getProductionProgress(productionID)
        if not result["OK"]:
            return result

        if "Created" in result["Value"]:
            createdJobs = int(result["Value"]["Created"]) + submittedJobs
        else:
            createdJobs = submittedJobs

        percSub = int(100 * submittedJobs / createdJobs)
        percDone = int(100 * doneJobs / createdJobs)
        print("\nCurrent status of production %s:\n" % productionID)
        print(
            "Submitted".ljust(12)
            + str(percSub).ljust(3)
            + "%  ( "
            + str(submittedJobs).ljust(7)
            + "Submitted / ".ljust(15)
            + str(createdJobs).ljust(7)
            + " Created jobs )"
        )
        print(
            "Done".ljust(12)
            + str(percDone).ljust(3)
            + "%  ( "
            + str(doneJobs).ljust(7)
            + "Done / ".ljust(15)
            + str(createdJobs).ljust(7)
            + " Created jobs )"
        )
        result = S_OK()
        result["Totals"] = {"Submitted": int(submittedJobs), "Created": int(createdJobs), "Done": int(doneJobs)}
        result["Value"] = summary
        return result

    def getProductionSiteSummary(self, productionID, site=None, printOutput=False):
        """Returns a site summary for the productions in the system.

        If printOutput is specified, the result is printed to the screen.
        This queries the WMS for the given productionID and provides an up-
        to-date snapshot of the sites that jobs were submitted to.
        """
        if not isinstance(productionID, (six.integer_types, six.string_types)):
            return self._errorReport("Expected string, long or int for production ID")

        statusDict = self.getProdJobMetadata(productionID, None, None, site)
        if not statusDict["OK"]:
            self.log.warn("Could not get production metadata information")
            return statusDict

        summary = {}
        submittedJobs = 0
        doneJobs = 0

        for job, atts in statusDict["Value"].items():
            for key, val in atts.items():
                if key == "Site":
                    uniqueSite = val
                    currentStatus = atts["Status"].capitalize()
                    if uniqueSite not in summary:
                        summary[uniqueSite] = {}
                    if currentStatus not in summary[uniqueSite]:
                        summary[uniqueSite][currentStatus] = {}
                        summary[uniqueSite][currentStatus]["Total"] = 1
                        submittedJobs += 1
                        if currentStatus == "Done":
                            doneJobs += 1
                        summary[uniqueSite][currentStatus]["JobList"] = [job]
                    else:
                        current = summary[uniqueSite][currentStatus]["Total"]
                        summary[uniqueSite][currentStatus]["Total"] = current + 1
                        submittedJobs += 1
                        if currentStatus == "Done":
                            doneJobs += 1
                        jobList = summary[uniqueSite][currentStatus]["JobList"]
                        jobList.append(job)
                        summary[uniqueSite][currentStatus]["JobList"] = jobList

        if not printOutput:
            result = S_OK()
            if not site:
                result = self.getProductionProgress(productionID)
                if not result["OK"]:
                    return result
                if "Created" in result["Value"]:
                    createdJobs = result["Value"]["Created"]
                result["Totals"] = {"Submitted": int(submittedJobs), "Done": int(doneJobs)}
            result["Value"] = summary
            return result

        # If a printed summary is requested
        siteAdj = int(1.0 * self.prodAdj)
        statAdj = int(0.5 * self.prodAdj)
        totalAdj = int(0.5 * self.prodAdj)
        exAdj = int(0.5 * self.prodAdj)
        message = "\nSummary for ProductionID %s" % (productionID)
        if site:
            message += " at Site %s" % (site)
        else:
            message += " at all Sites"
        message += ":\n\n"
        message += (
            "Site".ljust(siteAdj) + "Status".ljust(statAdj) + "Total".ljust(totalAdj) + "Example".ljust(exAdj) + "\n"
        )
        for siteStr, metadata in summary.items():
            message += "\n"
            for stat, jobInfo in metadata.items():
                message += (
                    siteStr.ljust(siteAdj)
                    + stat.ljust(statAdj)
                    + str(jobInfo["Total"]).ljust(totalAdj)
                    + str(jobInfo["JobList"][0]).ljust(exAdj)
                    + "\n"
                )

        print(message)
        # self._prettyPrint(summary)
        result = self.getProductionProgress(productionID)

        if not result["OK"]:
            return result

        if "Created" in result["Value"]:
            createdJobs = int(result["Value"]["Created"]) + submittedJobs
        else:
            createdJobs = submittedJobs

        percSub = int(100 * submittedJobs / createdJobs)
        percDone = int(100 * doneJobs / createdJobs)
        if not site:
            print("\nCurrent status of production %s:\n" % productionID)
            print(
                "Submitted".ljust(12)
                + str(percSub).ljust(3)
                + "%  ( "
                + str(submittedJobs).ljust(7)
                + "Submitted / ".ljust(15)
                + str(createdJobs).ljust(7)
                + " Created jobs )"
            )
            print(
                "Done".ljust(12)
                + str(percDone).ljust(3)
                + "%  ( "
                + str(doneJobs).ljust(7)
                + "Done / ".ljust(15)
                + str(createdJobs).ljust(7)
                + " Created jobs )"
            )
        result = S_OK()
        result["Totals"] = {"Submitted": int(submittedJobs), "Created": int(createdJobs), "Done": int(doneJobs)}
        result["Value"] = summary
        return result

    def getProductionProgress(self, productionID=None, printOutput=False):
        """Returns the status of jobs as seen by the production management
        infrastructure."""
        if not isinstance(productionID, (six.integer_types, six.string_types)):
            return self._errorReport("Expected string, long or int for production ID")

        productionID = int(productionID)

        if not productionID:
            result = self._getActiveProductions()
            if not result["OK"]:
                return result
            productionID = result["Value"]
        else:
            productionID = [productionID]

        productionID = [str(x) for x in productionID]
        self.log.verbose("Will check progress for production(s):\n%s" % (", ".join(productionID)))
        progress = {}
        for prod in productionID:
            # self._prettyPrint(result)
            result = self.transformationClient.getTransformationTaskStats(int(prod))
            if not result["Value"]:
                self.log.error(result)
                return result
            progress[int(prod)] = result["Value"]

        if not printOutput:
            return result
        idAdj = int(self.prodAdj)
        statAdj = int(self.prodAdj)
        countAdj = int(self.prodAdj)
        message = "ProductionID".ljust(idAdj) + "Status".ljust(statAdj) + "Count".ljust(countAdj) + "\n\n"
        for prod, info in progress.items():
            for status, count in info.items():
                message += str(prod).ljust(idAdj) + status.ljust(statAdj) + str(count).ljust(countAdj) + "\n"
            message += "\n"

        print(message)
        return result

    def _getActiveProductions(self, printOutput=False):
        """Returns a dictionary of active production IDs and their status, e.g.
        automatic, manual."""
        result = self.transformationClient.getTransformations()
        if not result["OK"]:
            return result
        prodList = result["Value"]
        currentProductions = {}
        for prodDict in prodList:
            self.log.debug(prodDict)
            if "AgentType" in prodDict and "TransformationID" in prodDict:
                prodID = prodDict["TransformationID"]
                status = prodDict["AgentType"]
                currentProductions[prodID] = status
                if status.lower() == "automatic":
                    self.log.verbose("Found active production %s eligible to submit jobs" % prodID)

        if printOutput:
            self._prettyPrint(currentProductions)

        return S_OK(currentProductions)

    def getProductionCommands(self):
        """Returns the list of possible commands and their meaning."""
        prodCommands = {}
        for keyword, statusSubMode in self.commands.items():
            prodCommands[keyword] = {"Status": statusSubMode[0], "SubmissionMode": statusSubMode[1]}
        return S_OK(prodCommands)

    def production(self, productionID, command, disableCheck=True):
        """Allows basic production management by supporting the following commands:

        - start : set production status to Active, job submission possible
        - stop : set production status to Stopped, no job submissions
        - automatic: set production submission mode to Automatic, e.g. submission via Agent
        - manual: set produciton submission mode to manual, e.g. dirac-production-submit
        """
        commands = self.commands

        if not isinstance(productionID, (six.integer_types, six.string_types)):
            return self._errorReport("Expected string, long or int for production ID")

        productionID = int(productionID)
        if not isinstance(command, str):
            return self._errorReport("Expected string, for command")
        if not command.lower() in commands:
            return self._errorReport("Expected one of: %s for command string" % (", ".join(commands)))

        self.log.verbose(
            'Requested to change production %s with command "%s"' % (productionID, command.lower().capitalize())
        )
        if not disableCheck:
            result = promptUser(
                'Do you wish to change production %s with command "%s"? ' % (productionID, command.lower().capitalize())
            )
            if not result["OK"]:
                self.log.info("Action cancelled")
                return S_OK("Action cancelled")
            if result["Value"] != "y":
                self.log.info("Doing nothing")
                return S_OK("Doing nothing")

        actions = commands[command]
        self.log.info(
            "Setting production status to %s and submission mode to %s for productionID %s"
            % (actions[0], actions[1], productionID)
        )
        result = self.transformationClient.setTransformationParameter(int(productionID), "Status", actions[0])
        if not result["OK"]:
            self.log.warn("Problem updating transformation status with result:\n%s" % result)
            return result
        self.log.verbose("Setting transformation status to %s successful" % (actions[0]))
        result = self.transformationClient.setTransformationParameter(int(productionID), "AgentType", actions[1])
        if not result["OK"]:
            self.log.warn("Problem updating transformation agent type with result:\n%s" % result)
            return result
        self.log.verbose("Setting transformation agent type to %s successful" % (actions[1]))
        return S_OK("Production %s status updated" % productionID)

    def productionFileSummary(
        self, productionID, selectStatus=None, outputFile=None, orderOutput=True, printSummary=False, printOutput=False
    ):
        """Allows to investigate the input files for a given production
        transformation and provides summaries / selections based on the file status
        if desired."""
        adj = 18
        ordering = "TaskID"
        if not orderOutput:
            ordering = "LFN"
        fileSummary = self.transformationClient.getTransformationFiles(
            condDict={"TransformationID": int(productionID)}, orderAttribute=ordering
        )
        if not fileSummary["OK"]:
            return fileSummary

        toWrite = ""
        totalRecords = 0
        summary = {}
        selected = 0
        if fileSummary["OK"]:
            for lfnDict in fileSummary["Value"]:
                totalRecords += 1
                record = ""
                recordStatus = ""
                for n, v in lfnDict.items():
                    record += str(n) + " = " + str(v).ljust(adj) + " "
                    if n == "Status":
                        recordStatus = v
                        if selectStatus == recordStatus:
                            selected += 1
                        if v in summary:
                            new = summary[v] + 1
                            summary[v] = new
                        else:
                            summary[v] = 1

                if outputFile and selectStatus:
                    if selectStatus == recordStatus:
                        toWrite += record + "\n"
                        if printOutput:
                            print(record)
                elif outputFile:
                    toWrite += record + "\n"
                    if printOutput:
                        print(record)
                else:
                    if printOutput:
                        print(record)

        if printSummary:
            print("\nSummary for %s files in production %s\n" % (totalRecords, productionID))
            print("Status".ljust(adj) + " " + "Total".ljust(adj) + "Percentage".ljust(adj) + "\n")
            for n, v in summary.items():
                percentage = int(100 * int(v) / totalRecords)
                print(str(n).ljust(adj) + " " + str(v).ljust(adj) + " " + str(percentage).ljust(2) + " % ")
            print("\n")

        if selectStatus and not selected:
            return S_ERROR('No files were selected for production %s and status "%s"' % (productionID, selectStatus))
        elif selectStatus and selected:
            print(
                '%s / %s files (%s percent) were found for production %s in status "%s"'
                % (selected, totalRecords, int(100 * int(selected) / totalRecords), productionID, selectStatus)
            )

        if outputFile:
            if os.path.exists(outputFile):
                print("Requested output file %s already exists, please remove this file to continue" % outputFile)
                return fileSummary

            with open(outputFile, "w") as fopen:
                fopen.write(toWrite)
            if not selectStatus:
                print("Wrote %s lines to file %s" % (totalRecords, outputFile))
            else:
                print('Wrote %s lines to file %s for status "%s"' % (selected, outputFile, selectStatus))

        return fileSummary

    def checkFilesStatus(self, lfns, productionID="", printOutput=False):
        """Checks the given LFN(s) status in the productionDB.

        All productions are considered by default but can restrict to
        productionID.
        """
        if not isinstance(productionID, (six.integer_types, six.string_types)):
            return self._errorReport("Expected string, long or int for production ID")

        if isinstance(lfns, six.string_types):
            lfns = lfns.replace("LFN:", "")
        elif isinstance(lfns, list):
            try:
                lfns = [str(lfnName.replace("LFN:", "")) for lfnName in lfns]
            except Exception as x:
                return self._errorReport(str(x), "Expected strings for LFN(s)")
        else:
            return self._errorReport("Expected single string or list of strings for LFN(s)")

        fileStatus = self.transformationClient.getFileSummary(lfns, int(productionID))
        if printOutput:
            self._prettyPrint(fileStatus["Value"])
        return fileStatus

    def getWMSProdJobID(self, jobID, printOutput=False):
        """This method takes the DIRAC WMS JobID and returns the Production JobID
        information."""
        result = self.getJobAttributes(jobID)
        if not result["OK"]:
            return result
        if "JobName" not in result["Value"]:
            return S_ERROR("Could not establish ProductionID / ProductionJobID, missing JobName")

        wmsJobName = result["Value"]["JobName"]
        prodID = wmsJobName.split("_")[0]
        prodJobID = wmsJobName.split("_")[1]
        info = {"WMSJobID": jobID, "JobName": wmsJobName, "ProductionID": prodID, "JobID": prodJobID}
        if printOutput:
            self._prettyPrint(info)
        return S_OK(info)

    def getProdJobInfo(self, productionID, jobID, printOutput=False):
        """Retrieve production job information from Production Manager service."""
        res = self.transformationClient.getTransformationTasks(
            condDict={"TransformationID": productionID, "TaskID": jobID}, inputVector=True
        )
        if not res["OK"]:
            return res
        if not res["Value"]:
            return S_ERROR("Job %s not found for production %s" % (jobID, productionID))
        jobInfo = res["Value"][0]
        if printOutput:
            self._prettyPrint(jobInfo)
        return S_OK(jobInfo)

    def selectProductionJobs(
        self, productionID, status=None, minorStatus=None, applicationStatus=None, site=None, owner=None, date=None
    ):
        """Wraps around DIRAC API selectJobs().

        Arguments correspond to the web page selections. By default, the
        date is the creation date of the production.
        """
        if not date:
            self.log.verbose("No Date supplied, setting old date for production %s" % productionID)
            date = "2001-01-01"
        return self.selectJobs(status, minorStatus, applicationStatus, site, owner, str(productionID).zfill(8), date)

    def extendProduction(self, productionID, numberOfJobs, printOutput=False):
        """Extend Simulation type Production by number of jobs.

        Usage: extendProduction <ProductionNameOrID> nJobs
        """
        if not isinstance(productionID, (six.integer_types, six.string_types)):
            return self._errorReport("Expected string, long or int for production ID")

        if isinstance(numberOfJobs, six.string_types):
            try:
                numberOfJobs = int(numberOfJobs)
            except Exception as x:
                return self._errorReport(str(x), "Expected integer or string for number of jobs to submit")

        result = self.transformationClient.extendTransformation(int(productionID), numberOfJobs)
        if not result["OK"]:
            return self._errorReport(result, "Could not extend production %s by %s jobs" % (productionID, numberOfJobs))

        if printOutput:
            print("Extended production %s by %s jobs" % (productionID, numberOfJobs))

        return result

    def getProdJobMetadata(self, productionID, status=None, minorStatus=None, site=None):
        """Function to get the WMS job metadata for selected fields.

        Given a production ID will return the current WMS status information
        for all jobs in that production starting from the creation date.
        """
        result = self.transformationClient.getTransformationParameters(int(productionID), ["CreationDate"])
        if not result["OK"]:
            self.log.warn("Problem getting production metadata for ID %s:\n%s" % (productionID, result))
            return result

        creationDate = toString(result["Value"]).split()[0]
        result = self.selectProductionJobs(
            productionID, status=status, minorStatus=minorStatus, site=site, date=creationDate
        )
        if not result["OK"]:
            self.log.warn("Problem selecting production jobs for ID %s:\n%s" % (productionID, result))
            return result

        jobsList = result["Value"]
        return self.getJobStatus(jobsList)

    def launchProduction(self, prod, publishFlag, testFlag, requestID, extend=0, tracking=0, MCsimflag=False):
        """Given a production object (prod), launch it It returns the productionID
        created."""

        if publishFlag is False and testFlag:
            gLogger.info("Test prod will be launched locally")
            result = prod.runLocal()
            if result["OK"]:
                gLogger.info("Template finished successfully")
                return S_OK()
            gLogger.error("Launching production: something wrong with execution!")
            return S_ERROR("Something wrong with execution!")

        result = prod.create(publish=publishFlag, requestID=requestID, reqUsed=tracking)

        if not result["OK"]:
            gLogger.error("Error during prod creation:\n%s\ncheck that the wkf name is unique." % (result["Message"]))
            return result

        if publishFlag:
            prodID = result["Value"]
            msg = "Production %s successfully created " % (prodID)

            if extend:
                self.extendProduction(prodID, extend, printOutput=True)
                msg += ", extended by %s jobs" % extend
            if MCsimflag:
                self.production(prodID, "mctestmode")
                msg = msg + " and started in mctestmode."
            elif testFlag:
                self.production(prodID, "manual")
                msg = msg + " and started in manual mode."
            else:
                self.production(prodID, "automatic")
                msg = msg + " and started in automatic mode."
            gLogger.notice(msg)

        else:
            prodID = 1
            gLogger.notice(
                "Production creation completed but not published (publishFlag was %s). \
      Setting ID = %s (useless, just for the test)"
                % (publishFlag, prodID)
            )

        return S_OK(prodID)
