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
"""Production API.

A production is an augmented version of an LHCbJob

Notes:

- Supports all workflows
- create() method that takes a workflow or Production object
  and publishes to the production management system, in addition this
  can automatically construct and publish the BK pass info and transformations
- Uses __getOutputLFNs() function to add production output directory parameter
"""
import shutil
import re
import os

from DIRAC import gLogger, S_OK, S_ERROR
from DIRAC.Core.Workflow.Workflow import Workflow, fromXMLString
from DIRAC.ConfigurationSystem.Client.Helpers.Operations import Operations
from DIRAC.ConfigurationSystem.Client.Helpers.Resources import getSites, getSiteTier
from DIRAC.Workflow.Utilities.Utils import getStepDefinition

from LHCbDIRAC.Core.Utilities.ProductionData import preSubmissionLFNs
from LHCbDIRAC.Interfaces.API.LHCbJob import LHCbJob
from LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient import BookkeepingClient
from LHCbDIRAC.ProductionManagementSystem.Client.ProductionRequestClient import ProductionRequestClient
from LHCbDIRAC.TransformationSystem.Client.Transformation import Transformation


class Production(object):
    """Production uses an LHCbJob object, as well as few clients."""

    #############################################################################

    def __init__(self, script=None):
        """Instantiates the Workflow object and some default parameters."""

        self.LHCbJob = LHCbJob(script)
        self.bkkClient = BookkeepingClient()
        self.transformation = Transformation()
        self.opsHelper = Operations()

        self.bkSteps = {}
        self.prodGroup = ""
        self.plugin = ""
        self.inputFileMask = ""
        self.inputBKSelection = {}
        self.jobFileGroupSize = 0
        self.ancestorProduction = 0
        self.transformationFamily = 0
        self.priority = 1
        self.gaudiSteps = []

        # a dictionary with 'FileType':'SEName'. All the file types should be present. HISTs are present by default
        histogramSE = self.opsHelper.getValue("Productions/HistogramSE", "CERN-HIST")
        histoTypes = self.opsHelper.getValue(
            "Productions/HistogramTypes", ["HIST", "BRUNELHIST", "DAVINCIHIST", "GAUSSHIST"]
        )
        self.outputSEs = dict((ht, histogramSE) for ht in histoTypes)

        if not script:
            self.__setDefaults()

    #############################################################################

    def __setDefaults(self):
        """Sets some default parameters."""

        self.LHCbJob.stepCount = 0
        self.LHCbJob.setOutputSandbox(
            self.opsHelper.getValue("Productions/inOutputSandbox", ["std.out", "std.err", "*.log"])
        )
        self.setJobParameters(
            {
                "Type": "MCSimulation",
                "Platform": "ANY",
                "CPUTime": "1000000",
                "LogLevel": "verbose",
                "JobGroup": "@{PRODUCTION_ID}",
            }
        )

        self.setFileMask("")

        # General workflow parameters
        self.setParameter("PRODUCTION_ID", "string", "00012345", "ProductionID")
        self.setParameter("JOB_ID", "string", "00006789", "ProductionJobID")
        self.setParameter("poolXMLCatName", "string", "pool_xml_catalog.xml", "POOLXMLCatalogName")
        self.setParameter("outputMode", "string", "Any", "SEResolutionPolicy")
        self.setParameter("outputDataFileMask", "string", "", "outputDataFileMask")

        # BK related parameters
        self.setParameter("configName", "string", "MC", "ConfigName")
        self.setParameter("configVersion", "string", "2009", "ConfigVersion")
        self.setParameter("conditions", "string", "", "SimOrDataTakingCondsString")

    #############################################################################

    def setJobParameters(self, parametersDict):
        """Set an (LHCb)Job parameter.

        The parametersDict is in the form {'parameterName': 'value'} Each
        parameter calls LHCbJob.setparameterName(value)
        """

        for parameter in parametersDict:
            getattr(self.LHCbJob, "set" + parameter)(parametersDict[parameter])

    #############################################################################

    def setParameter(self, name, parameterType, parameterValue, description):
        """Set parameters checking in CS in case some defaults need to be
        changed."""
        proposedParam = self.opsHelper.getValue("Productions/%s" % name, "")
        if proposedParam:
            gLogger.debug("Setting %s from CS defaults = %s" % (name, proposedParam))
            self.LHCbJob._addParameter(
                self.LHCbJob.workflow, name, parameterType, proposedParam, description
            )  # pylint: disable=protected-access
        else:
            gLogger.debug("Setting parameter %s = %s" % (name, parameterValue))
            self.LHCbJob._addParameter(
                self.LHCbJob.workflow, name, parameterType, parameterValue, description
            )  # pylint: disable=protected-access

    #############################################################################

    @staticmethod
    def __checkArguments(extraPackages, optionsFile):
        """Checks for typos in the structure of standard arguments to workflows.

        In case of any non-standard settings will raise an exception
        preventing creation of the production. Must be called after setting
        the first event type of the production.
        """
        if not extraPackages:
            extraPackages = []

        if not optionsFile:
            optionsFile = []

        if extraPackages:
            if not re.search(";", extraPackages):
                extraPackages = [extraPackages]
            else:
                extraPackages = extraPackages.split(";")
        if optionsFile:
            if not re.search(";", optionsFile):
                optionsFile = [optionsFile]

        for package in extraPackages:
            gLogger.verbose("Checking extra package: %s" % (package))
            if not re.search(".", package):
                raise TypeError("Must have extra packages in the following format 'Name.Version' not %s" % (package))

        gLogger.verbose("Extra packages and event type options are correctly specified")
        return S_OK()

    #############################################################################

    def addApplicationStep(self, stepDict, inputData=None, modulesList=None, extraModulesList=None):
        """Adds an application step to the workflow.

        stepDict contains everything that is in the step, for this production, e.g.::

          {'ApplicationName': 'DaVinci', 'Usable': 'Yes', 'StepId': 13718, 'ApplicationVersion': 'v28r3p1',
           'ExtraPackages': 'AppConfig.v3r104', 'StepName': 'Stripping14-Merging', 'ExtraOptions': '',
           'ProcessingPass': 'Merging', 'Visible': 'N', 'OptionsFormat': '',
           'OptionFiles': '$APPCONFIGOPTS/Merging/DV-Stripping14-Merging.py',
           'DDDB': 'head-20110302', 'CONDDB': 'head-20110407', 'DQTag': '',
           'isMulticore': 'N', 'SystemConfig': '', 'mcTCK': '',
           'fileTypesIn': ['SDST'],
           'visibilityFlag': [{'Visible': 'Y', 'FileType': 'BHADRON.DST'}],
           'fileTypesOut': ['BHADRON.DST', 'CALIBRATION.DST', 'CHARM.MDST', 'CHARMCOMPLETEEVENT.DST']}

        Note: this step treated here does not necessarily corresponds to a step of the BKK:
        the case where they might be different is the merging case.

        :param dict stepDict: contains everything that is in the step, for this production
        :param str inputData: the input data of the step. Either None, or 'previousStep', or the input to the step
        :param list modulesList: the list of module names (str) this step is made of. If None, a default is taken.

        :returns: the name (str) of the step added
        """

        appName = stepDict["ApplicationName"]
        appVersion = stepDict["ApplicationVersion"]
        optionsFile = stepDict["OptionFiles"]
        stepID = stepDict["StepId"]
        stepName = stepDict["StepName"]
        stepVisible = stepDict["Visible"]
        extraPackages = stepDict["ExtraPackages"]
        optionsLine = stepDict["ExtraOptions"]
        fileTypesIn = stepDict["fileTypesIn"]
        fileTypesOut = stepDict["fileTypesOut"]
        stepPass = stepDict["ProcessingPass"]
        optionsFormat = stepDict["OptionsFormat"]
        dddbOpt = stepDict["DDDB"]
        conddbOpt = stepDict["CONDDB"]
        dqOpt = stepDict["DQTag"]
        multicore = stepDict["isMulticore"]
        sysConfig = stepDict["SystemConfig"]
        outputVisibility = stepDict["visibilityFlag"]
        if sysConfig == "None" or sysConfig == "NULL" or not sysConfig or sysConfig is None:
            sysConfig = "ANY"
        mcTCK = stepDict["mcTCK"]

        if extraPackages:
            if isinstance(extraPackages, list):
                extraPackages = ";".join(extraPackages)
            if not isinstance(extraPackages, str):
                raise TypeError("extraPackages is not a string (nor a list)")
            if "," in extraPackages:
                extraPackages = ";".join(extraPackages.split(","))
            if "ProdConf" not in extraPackages:
                extraPackages = extraPackages + ";ProdConf"
            extraPackages = extraPackages.replace(" ", "")
        else:
            extraPackages = "ProdConf"

        self.__checkArguments(extraPackages, optionsFile)

        try:
            if not dddbOpt.lower() == "global":
                gLogger.verbose("Specific DDDBTag setting found for %s step, setting to: %s" % (appName, dddbOpt))
                dddbOpt = dddbOpt.replace(" ", "")
        except AttributeError:
            pass
        try:
            if not conddbOpt.lower() == "global":
                gLogger.verbose("Specific CondDBTag setting found for %s step, setting to: %s" % (appName, conddbOpt))
                conddbOpt = conddbOpt.replace(" ", "")
        except AttributeError:
            pass
        try:
            if not dqOpt.lower() == "global":
                gLogger.verbose("Specific DQTag setting found for %s step, setting to: %s" % (appName, dqOpt))
                dqOpt = dqOpt.replace(" ", "")
        except AttributeError:
            pass

        # starting real stuff
        self.LHCbJob.stepCount += 1

        if "Gaudi_App_Step" not in self.LHCbJob.workflow.step_definitions:

            gLogger.debug("Determining the modules of the steps (modulesList = %s)" % modulesList)
            if modulesList is None:  # we assume it's a standard list of modules for Gaudi steps
                gaudiPath = "Productions/GaudiStep_Modules"
                modulesList = self.opsHelper.getValue(
                    gaudiPath,
                    ["GaudiApplication", "AnalyseXMLSummary", "ErrorLogging", "BookkeepingReport", "StepAccounting"],
                )
            if extraModulesList:
                modulesList += extraModulesList

            # pName, pType, pValue, pDesc
            parametersList = [
                ["inputData", "string", "", "StepInputData"],
                ["inputDataType", "string", "", "InputDataType"],
                ["applicationName", "string", "", "ApplicationName"],
                ["applicationVersion", "string", "", "ApplicationVersion"],
                ["applicationType", "string", "", "ApplicationType"],
                ["optionsFile", "string", "", "OptionsFile"],
                ["extraOptionsLine", "string", "", "extraOptionsLines"],
                ["listoutput", "list", [], "StepOutputList"],
                ["extraPackages", "string", "", "ExtraPackages"],
                ["BKStepID", "string", "", "BKKStepID"],
                ["StepProcPass", "string", "", "StepProcessingPass"],
                ["optionsFormat", "string", "", "ProdConf configuration"],
                ["CondDBTag", "string", "", "ConditionDatabaseTag"],
                ["DDDBTag", "string", "", "DetDescTag"],
                ["DQTag", "string", "", "DataQualityTag"],
                ["multiCore", "string", "", "MultiCore Flag"],
                ["SystemConfig", "string", "", "system config"],
                ["mcTCK", "string", "", "TCK to be simulated"],
            ]

            gaudiStepDef = getStepDefinition(
                "Gaudi_App_Step",
                modulesNameList=modulesList,
                importLine="LHCbDIRAC.Workflow.Modules",
                parametersList=parametersList,
            )
            self.LHCbJob.workflow.addStep(gaudiStepDef)

        # create the step instance add it to the wf, and return it
        name = "%s_%s" % (appName, self.LHCbJob.stepCount)
        gaudiStepInstance = self.LHCbJob.workflow.createStepInstance("Gaudi_App_Step", name)

        valuesToSet = [
            ["applicationName", appName],
            ["applicationVersion", appVersion],
            ["optionsFile", optionsFile],
            ["extraOptionsLine", optionsLine],
            ["extraPackages", extraPackages],
            ["BKStepID", str(stepID)],
            ["StepProcPass", stepPass],
            ["optionsFormat", optionsFormat],
            ["CondDBTag", conddbOpt],
            ["DDDBTag", dddbOpt],
            ["DQTag", dqOpt],
            ["multiCore", multicore],
            ["SystemConfig", sysConfig],
            ["mcTCK", mcTCK],
        ]

        if fileTypesIn:
            valuesToSet.append(["inputDataType", ";".join(ftIn.upper() for ftIn in fileTypesIn)])

        if inputData is None:
            gLogger.verbose("%s step has no data requirement or is linked to the overall input data" % appName)
            gaudiStepInstance.setLink("inputData", "self", "InputData")
        elif inputData == "previousStep":
            gLogger.verbose("Taking input data as output from previous Gaudi step")
            valuesToSet.append(["inputData", inputData])
        else:
            gLogger.verbose("Assume input data requirement should be added to job")
            self.LHCbJob.setInputData(inputData)
            gaudiStepInstance.setLink("inputData", "self", "InputData")

        for pName, value in valuesToSet:
            if value:
                gaudiStepInstance.setValue(pName, value)

        outputFilesList = self._constructOutputFilesList(fileTypesOut)
        gaudiStepInstance.setValue("listoutput", (outputFilesList))

        # to construct the BK processing pass structure, starts from step '0'
        stepIDInternal = "Step%s" % (self.LHCbJob.stepCount - 1)
        bkOptionsFile = optionsFile

        stepBKInfo = {
            "ApplicationName": appName,
            "ApplicationVersion": appVersion,
            "OptionFiles": bkOptionsFile,
            "DDDb": dddbOpt,
            "CondDb": conddbOpt,
            "DQTag": dqOpt,
            "ExtraPackages": extraPackages,
            "BKStepID": stepID,
            "StepName": stepName,
            "StepVisible": stepVisible,
            "OutputFileTypes": outputVisibility,
        }

        self.bkSteps[stepIDInternal] = stepBKInfo
        self.__addBKPassStep()

        return name

    #############################################################################

    def _constructOutputFilesList(self, filesTypesList):
        """Build list of dictionary of output file types, including HIST case.

        :param list filesTypesList: a list of file types (str)
        :returns: a list with a dictionary of file types, lowered
        """

        outputList = []

        for fileType in filesTypesList:
            fileDict = {}
            fileDict["outputDataType"] = fileType.lower()
            outputList.append(fileDict)

        return outputList

    #############################################################################

    def __addBKPassStep(self):
        """Internal method to add BKK parameters."""
        bkPass = "BKProcessingPass"
        description = "BKProcessingPassInfo"
        self.LHCbJob._addParameter(
            self.LHCbJob.workflow, bkPass, "dict", self.bkSteps, description
        )  # pylint: disable=protected-access

    #############################################################################

    def addFinalizationStep(self, modulesList=None):
        """Add the finalization step to the workflow (some defaults are inserted)

        :param list modulesList: the list of modules names this step is made of. If None, a default is taken.
        :returns: None
        """
        if modulesList is None:
            modulesList = ["UploadOutputData", "UploadLogFile", "UploadMC", "FailoverRequest"]

        if "Job_Finalization" not in self.LHCbJob.workflow.step_definitions:

            jobFinalizationStepDef = getStepDefinition(
                "Job_Finalization", importLine="LHCbDIRAC.Workflow.Modules", modulesNameList=modulesList
            )
            self.LHCbJob.workflow.addStep(jobFinalizationStepDef)

        # create the step instance add it to the wf
        self.LHCbJob.workflow.createStepInstance("Job_Finalization", "finalization")

    #############################################################################

    def _lastParameters(self):
        """Add the last parameters before creating the xml file containing the
        workflow."""

        self.LHCbJob._addParameter(
            self.LHCbJob.workflow, "gaudiSteps", "list", self.gaudiSteps, "list of Gaudi Steps"
        )  # pylint: disable=protected-access
        self.LHCbJob._addParameter(
            self.LHCbJob.workflow, "outputSEs", "dict", self.outputSEs, "dictionary of output SEs"
        )  # pylint: disable=protected-access

    def __createWorkflow(self, name=""):
        """Create XML of the workflow."""
        self._lastParameters()

        if not name:
            name = self.LHCbJob.workflow.getName()
        if not re.search("xml$", name):
            name = "%s.xml" % name
        if os.path.exists(name):
            shutil.move(name, "%s.backup" % name)
        name = name.replace("/", "").replace("\\", "")
        self.LHCbJob.workflow.toXMLFile(name)

        return name

    #############################################################################

    def runLocal(self):
        """Create XML workflow for local testing then reformulate as a job and run
        locally."""

        xmlFileName = self.__createWorkflow()
        # it makes a job (a Worklow, with Parameters), out of the xml file
        return LHCbJob(xmlFileName).runLocal()

    #############################################################################

    def __getProductionParameters(
        self, prodXMLFile, prodID, groupDescription="", bkPassInfo={}, derivedProd=0, reqID=0
    ):
        """This method will publish production parameters."""

        prodWorkflow = Workflow(prodXMLFile)

        parameters = {}
        info = []

        for parameterName in (
            "Priority",
            "CondDBTag",
            "DDDBTag",
            "DQTag",
            "eventType",
            "processingPass",
            "FractionToProcess",
            "MinFilesToProcess",
            "configName",
            "configVersion",
            "outputDataFileMask",
            "JobType",
            "MaxNumberOfTasks",
        ):
            try:
                parameters[parameterName] = prodWorkflow.findParameter(parameterName).getValue()
                info.append("%s: %s" % (parameterName, prodWorkflow.findParameter(parameterName).getValue()))
            except AttributeError:
                continue

        parameters["SizeGroup"] = self.jobFileGroupSize

        if prodWorkflow.findParameter("InputData"):  # now only comes from BK query
            prodWorkflow.findParameter("InputData").setValue("")
            gLogger.verbose("Resetting input data for production to null, this comes from a BK query...")
            prodXMLFile = self.__createWorkflow(prodXMLFile)
            # prodWorkflow.toXMLFile(prodXMLFile)

        if self.transformationFamily:
            parameters["TransformationFamily"] = self.transformationFamily

        if not bkPassInfo:
            bkPassInfo = prodWorkflow.findParameter("BKProcessingPass").getValue()
        if not groupDescription:
            groupDescription = prodWorkflow.findParameter("groupDescription").getValue()

        parameters["BKCondition"] = prodWorkflow.findParameter("conditions").getValue()
        parameters["BKProcessingPass"] = bkPassInfo
        parameters["groupDescription"] = groupDescription
        parameters["RequestID"] = reqID
        parameters["DerivedProduction"] = derivedProd

        result = self.__getOutputLFNs(prodID, "99999999", prodXMLFile)
        if not result["OK"]:
            gLogger.error("Could not create production LFNs", result)

        outputLFNs = result["Value"]
        parameters["OutputLFNs"] = outputLFNs

        # the list of output directories is later used for consistency check and for removing output data
        outputDirectories = []
        del outputLFNs["BookkeepingLFNs"]  # since ProductionOutputData uses the file mask
        for i in outputLFNs.values():
            for j in i:
                outputDir = "%s%s" % (j.split(str(prodID))[0], prodID)
                if outputDir not in outputDirectories:
                    outputDirectories.append(outputDir)

        parameters["OutputDirectories"] = outputDirectories

        # Now for the steps of the workflow
        stepKeys = sorted(bkPassInfo)
        for step in stepKeys:
            info.append(
                "====> %s %s %s" % (bkPassInfo[step]["ApplicationName"], bkPassInfo[step]["ApplicationVersion"], step)
            )
            info.append("%s Option Files:" % (bkPassInfo[step]["ApplicationName"]))
            if bkPassInfo[step]["OptionFiles"]:
                for opts in bkPassInfo[step]["OptionFiles"].split(";"):
                    info.append("%s" % opts)
            if bkPassInfo[step]["ExtraPackages"]:
                info.append("ExtraPackages: %s" % (bkPassInfo[step]["ExtraPackages"]))

        try:
            if parameters["BkQuery"]:
                info.append("\nBK Input Data Query:")
                for bkn, bkv in parameters["BkQuery"].items():
                    info.append("%s= %s" % (bkn, bkv))
        except KeyError:
            pass

        # BK output directories (very useful)
        bkPaths = []
        bkOutputPath = "%s/%s/%s/%s/%s/%s" % (
            parameters["configName"],
            parameters["configVersion"],
            parameters["BKCondition"],
            parameters.get("processingPass", ""),
            parameters["groupDescription"],
            parameters["eventType"],
        )
        fileTypes = parameters["outputDataFileMask"]
        fileTypes = [a.upper() for a in fileTypes.split(";")]

        # Annoying that histograms are extension root
        if "ROOT" in fileTypes:
            fileTypes.remove("ROOT")
            fileTypes.append("HIST")

        for ft in fileTypes:
            bkPaths.append("%s/%s" % (bkOutputPath, ft))
        parameters["BKPaths"] = bkPaths
        info.append("\nBK Browsing Paths:\n%s" % ("\n".join(bkPaths)))
        infoString = "\n".join(info)
        parameters["DetailedInfo"] = infoString

        gLogger.verbose("Parameters that will be added: %s" % parameters)

        return parameters

    #############################################################################

    def create(self, publish=True, wfString="", requestID=0, reqUsed=0):
        """Will create the production and subsequently publish to the BK.
        Production parameters are also added at this point.

        publish = True - will add production to the production management system
                  False - does not publish the production

        The workflow XML is created regardless of the flags.
        """

        if wfString:
            self.LHCbJob.workflow = fromXMLString(wfString)
        #      self.name = self.LHCbJob.workflow.getName()

        bkConditions = self.LHCbJob.workflow.findParameter("conditions").getValue()

        bkSteps = self.LHCbJob.workflow.findParameter("BKProcessingPass").getValue()

        bkDictStep = {}

        # Add the BK conditions metadata / name
        simConds = self.bkkClient.getSimConditions()
        if not simConds["OK"]:
            gLogger.error("Could not retrieve conditions data from BK:\n%s" % simConds)
            return simConds
        simulationDescriptions = []
        for record in simConds["Value"]:
            simulationDescriptions.append(str(record[1]))

        if bkConditions not in simulationDescriptions:
            gLogger.verbose("Assuming BK conditions %s are DataTakingConditions" % bkConditions)
            bkDictStep["DataTakingConditions"] = bkConditions
        else:
            gLogger.verbose("Found simulation conditions for %s" % bkConditions)
            bkDictStep["SimulationConditions"] = bkConditions

        descShort = self.LHCbJob.workflow.getDescrShort()
        descLong = self.LHCbJob.workflow.getDescription()

        prodID = 0
        if publish:

            self.setParameter("ProcessingType", "JDL", str(self.prodGroup), "ProductionGroupOrType")
            self.setParameter("Priority", "JDL", str(self.priority), "UserPriority")

            try:
                fileName = self.__createWorkflow()
            except Exception as x:  # pylint: disable=broad-except
                gLogger.error(x)
                return S_ERROR("Could not create workflow")

            gLogger.verbose("Workflow XML file name is: %s" % fileName)

            workflowBody = ""
            if os.path.exists(fileName):
                with open(fileName, "r") as fopen:
                    workflowBody = fopen.read()
            else:
                return S_ERROR("Could not get workflow body")

            # Standard parameters
            self.transformation.setTransformationName(fileName)
            self.transformation.setTransformationGroup(self.prodGroup)
            self.transformation.setDescription(descShort)
            self.transformation.setLongDescription(descLong)
            self.transformation.setType(self.LHCbJob.type)
            self.transformation.setBody(workflowBody)
            self.transformation.setPlugin(self.plugin)
            self.transformation.setBkQuery(self.inputBKSelection)
            self.transformation.setTransformationFamily(self.transformationFamily)
            self.transformation.setFileMask(self.inputFileMask)
            self.transformation.setGroupSize(int(self.jobFileGroupSize))
            self.transformation.setInheritedFrom(int(self.ancestorProduction))

            result = self.transformation.addTransformation()

            if not result["OK"]:
                gLogger.error("Problem creating production:\n%s" % result)
                return result
            prodID = result["Value"]
            gLogger.info("Production %s successfully created" % prodID)

            # All other parameters
            groupDesc = self.LHCbJob.workflow.findParameter("groupDescription").getValue()
            paramsDict = self.__getProductionParameters(
                prodID=prodID,
                prodXMLFile=fileName,
                groupDescription=groupDesc,
                bkPassInfo=bkSteps,
                reqID=requestID,
                derivedProd=self.ancestorProduction,
            )
            for parName, parValue in paramsDict.items():
                result = getattr(self.transformation, "set" + parName)(parValue)

        else:
            gLogger.verbose("Publish flag is disabled, using default production ID")

        bkDictStep["Production"] = int(prodID)

        if self.inputBKSelection:
            queryProdID = int(self.inputBKSelection.get("ProductionID", 0))
            queryProcPass = (
                self.inputBKSelection.get("ProcessingPass", "")
                if self.inputBKSelection.get("ProcessingPass", "") != "All"
                else ""
            )

            if queryProdID:
                inputPass = self.bkkClient.getProductionProcessingPass(queryProdID)
                if not inputPass["OK"]:
                    gLogger.error(inputPass)
                    gLogger.error(
                        "Production %s was created but BK processing pass for %d was not found" % (prodID, queryProdID)
                    )
                    return inputPass
                inputPass = inputPass["Value"]
                gLogger.info(
                    "Setting %d as BK input production for %s with processing pass %s"
                    % (queryProdID, prodID, inputPass)
                )
                bkDictStep["InputProductionTotalProcessingPass"] = inputPass
            elif queryProcPass:
                gLogger.info(
                    "Adding input BK processing pass for production %s from input data query: %s"
                    % (prodID, queryProcPass)
                )
                bkDictStep["InputProductionTotalProcessingPass"] = queryProcPass
        else:
            # has to account for an input processing pass anyway, if there is one,
            # or output files may not have the output processing pass correctly computed
            try:
                bkDictStep["InputProductionTotalProcessingPass"] = self.LHCbJob.workflow.findParameter(
                    "processingPass"
                ).getValue()
            except AttributeError:
                pass

        stepList = []
        stepKeys = sorted(bkSteps)
        # The BK needs an ordered list of steps
        for step in stepKeys:
            stepID = bkSteps[step]["BKStepID"]
            if stepID:
                stepName = bkSteps[step]["StepName"]
                stepVisible = bkSteps[step]["StepVisible"]
                outputFileTypes = bkSteps[step]["OutputFileTypes"]
                stepList.append(
                    {
                        "StepId": int(stepID),
                        "OutputFileTypes": outputFileTypes,
                        "StepName": stepName,
                        "Visible": stepVisible,
                    }
                )

        # This is the last component necessary for the BK publishing (post reorganisation)
        bkDictStep["Steps"] = stepList
        bkDictStep["EventType"] = paramsDict["eventType"]

        bkDictStep["ConfigName"] = self.LHCbJob.workflow.findParameter("configName").getValue()
        bkDictStep["ConfigVersion"] = self.LHCbJob.workflow.findParameter("configVersion").getValue()

        if publish:
            gLogger.verbose("Attempting to publish production %s to the BK" % (prodID))
            result = self.bkkClient.addProduction(bkDictStep)
            if not result["OK"]:
                gLogger.error(result)
                return result

        if requestID and publish:
            reqDict = {"ProductionID": int(prodID), "RequestID": requestID, "Used": reqUsed, "BkEvents": 0}
            result = ProductionRequestClient(timeout=120).addProductionToRequest(reqDict)
            if not result["OK"]:
                gLogger.error(
                    "Attempt to add production %s to request %s failed: %s " % (prodID, requestID, result["Message"])
                )
                gLogger.error("Dictionary below:\n%s" % reqDict)
            else:
                gLogger.info(
                    "Successfully added production %s to request %s with flag set to %s" % (prodID, requestID, reqUsed)
                )

        return S_OK(prodID)

    #############################################################################

    def __getOutputLFNs(self, prodID="12345", prodJobID="6789", prodXMLFile=""):
        """Will construct the output LFNs for the production for visual
        inspection."""
        if not prodXMLFile:
            gLogger.verbose("Using workflow object to generate XML file")
            prodXMLFile = self.__createWorkflow()

        job = LHCbJob(prodXMLFile)
        result = preSubmissionLFNs(
            job._getParameters(),
            job.workflow.createCode(),  # pylint: disable=protected-access
            productionID=prodID,
            jobID=prodJobID,
        )
        if not result["OK"]:
            return result
        lfns = result["Value"]
        gLogger.verbose(lfns)
        return result

    #############################################################################

    def setFileMask(self, fileMask="", stepMask=""):
        """Output data related parameters."""
        if fileMask:
            if isinstance(fileMask, list):
                fileMask = ";".join(fileMask)
            self.setParameter("outputDataFileMask", "string", fileMask, "outputDataFileMask")

        if stepMask:
            if isinstance(stepMask, list):
                stepMask = ";".join(stepMask)
            self.LHCbJob._addParameter(
                self.LHCbJob.workflow, "outputDataStep", "string", stepMask, "outputDataStep Mask"
            )  # pylint: disable=protected-access

    #############################################################################

    def banTier1s(self):
        """Sets Tier1s as banned."""
        tier1s = []
        sites = getSites()
        if not sites["OK"]:
            return sites

        for site in sites["Value"]:
            tier = getSiteTier(site)
            if not tier["OK"]:
                return tier
            if int(tier["Value"]) in (0, 1):
                tier1s.append(site)

        self.LHCbJob.setBannedSites(tier1s)

    #############################################################################

    def banSites(self, listOfSites):
        """Sets Sites as banned."""
        sitesToBan = []
        sites = getSites()
        if not sites["OK"]:
            return sites

        sites = sites["Value"]
        for site in listOfSites:
            if site in sites:
                sitesToBan.append(site)

        self.LHCbJob.setBannedSites(sitesToBan)

    #############################################################################

    def setOutputMode(self, outputMode):
        """Sets output mode for all jobs, this can be 'Local' or 'Any'."""
        if not outputMode.lower().capitalize() in ("Local", "Any", "Run"):
            raise TypeError("Output mode must be 'Local' or 'Any' or 'Run'")
        self.setParameter("outputMode", "string", outputMode.lower().capitalize(), "SEResolutionPolicy")

    #############################################################################

    def setBKParameters(self, configName, configVersion, groupDescriptionOrStepsList, conditions):
        """Sets BK parameters for production."""
        self.setParameter("configName", "string", configName, "ConfigName")
        self.setParameter("configVersion", "string", configVersion, "ConfigVersion")
        if isinstance(groupDescriptionOrStepsList, list):
            # in this case we assume it is a list of steps (stepsListDict in
            # ProductionRequest module), so we calculate the BK path
            groupDescription = ""
            for step in groupDescriptionOrStepsList:
                if step["Visible"] == "Y":
                    groupDescription = os.path.sep.join([groupDescription, step["ProcessingPass"]])
        else:
            groupDescription = groupDescriptionOrStepsList
        self.setParameter("groupDescription", "string", groupDescription, "GroupDescription")
        self.setParameter("conditions", "string", conditions, "SimOrDataTakingCondsString")
        self.setParameter("simDescription", "string", conditions, "SimDescription")

    #############################################################################
    # properties

    def set_transformationFamily(self, value):
        if isinstance(value, int):
            value = str(value)
        self._transformationFamily = value

    def get_transformationFamily(self):
        return self._transformationFamily

    startRun = property(get_transformationFamily, set_transformationFamily)
