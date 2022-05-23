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
"""Module for creating, describing and managing production requests objects."""
import itertools
import copy
import re
import six

from DIRAC import gLogger, S_OK

from DIRAC.Core.Utilities.DAG import DAG
from DIRAC.Core.Workflow.Workflow import fromXMLString
from DIRAC.ConfigurationSystem.Client.Helpers.Operations import Operations

from LHCbDIRAC.Interfaces.API.DiracProduction import DiracProduction
from LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient import BookkeepingClient
from LHCbDIRAC.ProductionManagementSystem.Client.Production import Production
from LHCbDIRAC.ProductionManagementSystem.Client.ProductionRequestClient import ProductionRequestClient
from LHCbDIRAC.TransformationSystem.Client.TransformationClient import TransformationClient


class ProductionRequest(object):
    """Production request class - objects are usually created starting from a production request"""

    def __init__(self, bkkClientIn=None, diracProdIn=None):
        """c'tor.

        Some variables are defined here. A production request is made of:
        stepsList, productionsTypes, and various parameters of those
        productions
        """

        if bkkClientIn is None:
            self.bkkClient = BookkeepingClient()
        else:
            self.bkkClient = bkkClientIn

        if diracProdIn is None:
            self.diracProduction = DiracProduction()
        else:
            self.diracProduction = diracProdIn

        self.rpcProductionRequest = ProductionRequestClient()
        self.tc = TransformationClient()

        self.logger = gLogger.getSubLogger("ProductionRequest")

        self.opsH = Operations()

        # parameters of the request
        self.requestID = 0
        self.parentRequestID = 0
        self.appendName = "1"
        self.outConfigName = ""
        self.prodsToLaunch = []  # productions to launch
        self.stepsListDict = []  # list of dict of steps
        self.stepsInProds = []  # a list of lists
        self.mcTesting = True
        # parameters of the input data
        self.processingPass = ""
        self.dataTakingConditions = ""
        self.eventType = ""
        self.bkFileType = []
        self.dqFlag = ""
        self.startRun = 1
        self.endRun = 2
        self.runsList = ""
        self.configName = "test"
        self.configVersion = "certification"
        # parameters of the first production
        self.publishFlag = True
        self.testFlag = False
        self.derivedProduction = 0
        self.previousProdID = 0  # optional prod from which to start
        self.fullListOfOutputFileTypes = []

        # parameters that are the same for each productions
        self.prodGroup = ""  # This ends up being 'ProcessingType', workflow parameter, and it is used for accounting
        self.visibility = ""  # For BKQuery
        self.fractionToProcess = 0
        self.minFilesToProcess = 0
        self.modulesList = None  # Usually:
        # ['GaudiApplication', 'AnalyseXMLSummary',
        # 'ErrorLogging', 'BookkeepingReport', 'StepAccounting' ]
        self.extraModulesList = None

        # parameters of each production (the length of each list has to be the same as the number of productions
        self.events = []
        self.stepsList = []
        self.extraOptions = {}
        self.prodsTypeList = []
        self.bkQueries = []  # list of bk queries
        self.removeInputsFlags = []
        self.priorities = []
        self.cpus = []
        self.inputs = []  # list of lists
        self.outputModes = []
        self.targets = []
        self.outputFileMasks = []
        self.outputFileSteps = []
        self.groupSizes = []
        self.plugins = []
        self.inputDataPolicies = []
        self.previousProds = [None]  # list of productions from which to take the inputs (the first is always None)
        self.multicore = []  # list of flags to override the multi core flags of the steps
        # list of tuples with min and max number of processors allowed for the jobs ((0,0) = unlimited)
        self.processors = []

        self.outputSEs = []  # a list of StorageElements
        self.specialOutputSEs = []  # a list of dictionaries - might be empty
        self.outputSEsPerFileType = []  # a list of dictionaries - filled later
        self.ancestorDepths = []
        self.compDict = {"HIGH": "Compression-LZMA-4", "LOW": "Compression-ZLIB-1"}
        self.compressionLvl = [""]  # List: one compression level each step
        self.appConfig = "$APPCONFIGOPTS/Persistency/"  # Default location of the compression level configuration files
        #
        # These lists define the visibility of the output files produced by each step. For MC productions, the visibility
        # is tied to compression level. VIsible files are compressed at the highest level
        #
        self.outputVisFlag = []  # List of dictionary with default visibility flag of the output files per single step
        self.specialOutputVisFlag = []  # List of dictionaries with special visibility flag for given file type

    #############################################################################

    def resolveSteps(self):
        """Given a list of steps in strings, some of which might be missing,
        resolve it into a list of dictionary of steps (self.stepsListDict)"""
        outputVisFlag = dict(
            [k, v] for el in self.outputVisFlag for k, v in el.items()
        )  # Transform the list of dictionaries in a dictionary
        specialOutputVisFlag = dict([k, v] for el in self.specialOutputVisFlag for k, v in el.items())
        count = 0  # Needed to add correctly the optionFiles to the list of dictonaries of steps
        for stepID in self.stepsList:

            stepDict = self.bkkClient.getAvailableSteps({"StepId": stepID})
            if not stepDict["OK"]:
                raise ValueError(stepDict["Message"])
            else:
                stepDict = stepDict["Value"]

            stepsListDictItem = {}

            s_in = self.bkkClient.getStepInputFiles(stepID)
            if not s_in["OK"]:
                raise ValueError(s_in["Message"])
            stepsListDictItem["fileTypesIn"] = [fileType[0].strip() for fileType in s_in["Value"]["Records"]]

            s_out = self.bkkClient.getStepOutputFiles(stepID)
            if not s_out["OK"]:
                raise ValueError(s_out["Message"])
            fileTypesList = [fileType[0].strip() for fileType in s_out["Value"]["Records"]]
            self.fullListOfOutputFileTypes = self.fullListOfOutputFileTypes + fileTypesList
            stepsListDictItem["fileTypesOut"] = fileTypesList

            for parameter, value in zip(stepDict["ParameterNames"], stepDict["Records"][0]):
                if parameter.lower() in ["conddb", "dddb", "dqtag"] and value:
                    if value.lower() == "frompreviousstep":
                        value = self.stepsListDict[-1][parameter]

                if parameter == "OptionFiles":  # Modifying the OptionFiles (for setting the compression level)
                    if (
                        "MDF" not in stepsListDictItem["fileTypesOut"]
                    ):  # certain MC produce MDF, which shouldn't be compressed
                        #
                        # If the prod manager sets a compression level for a particular step, either we append the option file
                        # or we overwrite the existing one inherited with the step
                        #
                        if len(self.compressionLvl) > count and self.compressionLvl[count] != "":
                            persist = re.compile("Compression-[A-Z]{4}-[1-9]")
                            # self.compressionLvl[count] = self.appConfig + self.compressionLvl[count] + '.py'
                            self.compressionLvl[count] = (
                                self.appConfig + self.compDict[self.compressionLvl[count].upper()] + ".py"
                            )
                            if not persist.search(value):
                                if value == "":
                                    value = self.compressionLvl[count]
                                else:
                                    value = ";".join((value, self.compressionLvl[count]))
                            else:
                                value = persist.sub(persist.search(self.compressionLvl[count]).group(), value)
                        #
                        # If instead the prod manager doesn't declare a compression level, e.g. for intermediate steps,
                        # we check if there is one in the options and in case we delete it. This leaves the default zip level
                        # defined inside Gaudi
                        #
                        elif len(self.compressionLvl) > count and self.compressionLvl[count] == "":
                            persist = re.compile(r"\$\w+/Persistency/Compression-[A-Z]{4}-[1-9].py;?")
                            if persist.search(value):
                                value = persist.sub("", value)

                if parameter == "SystemConfig" and value is not None and re.search("slc5", value):
                    p = re.compile(r"\$\w+/Persistency/Compression-[A-Z]{4}-[1-9].py;?")
                    if p.search(stepsListDictItem["OptionFiles"]):
                        stepsListDictItem["OptionFiles"] = p.sub("", stepsListDictItem["OptionFiles"])

                stepsListDictItem[parameter] = value  # Fixing what decided

            if stepsListDictItem["StepId"] in self.extraOptions:
                stepsListDictItem["ExtraOptions"] = self.extraOptions[stepsListDictItem["StepId"]]
            else:
                stepsListDictItem["ExtraOptions"] = ""

            stepsListDictItem["prodStepID"] = str(stepID) + str(stepsListDictItem["fileTypesIn"])

            if "isMulticore" not in stepsListDictItem:
                stepsListDictItem["isMulticore"] = "N"

            if "SystemConfig" not in stepsListDictItem:
                stepsListDictItem["SystemConfig"] = ""

            if "mcTCK" not in stepsListDictItem:
                stepsListDictItem["mcTCK"] = ""

            # Add visibility info during step resolution
            if "visibilityFlag" not in stepsListDictItem:
                outputVisList = list(
                    {"Visible": outputVisFlag[str(count + 1)], "FileType": ftype}
                    for ftype in stepsListDictItem["fileTypesOut"]
                )
                if str(count + 1) in specialOutputVisFlag:
                    for it in outputVisList:
                        if it["FileType"] in specialOutputVisFlag[str(count + 1)]:
                            it["Visible"] = specialOutputVisFlag[str(count + 1)][it["FileType"]]

                stepsListDictItem["visibilityFlag"] = outputVisList

            self.stepsListDict.append(stepsListDictItem)
            count += 1

    #############################################################################

    def buildAndLaunchRequest(self):
        """uses _applyOptionalCorrections, _getProdsDescriptionDict,
        _buildProduction, and DiracProduction.launchProduction."""

        if not self.stepsListDict:
            self.resolveSteps()

        self._applyOptionalCorrections()

        self._determineOutputSEs()

        prodsDict = self._getProdsDescriptionDict()

        stepsListDict = list(self.stepsListDict)

        fromProd = self.previousProdID
        prodsLaunched = []

        self.logger.debug(prodsDict)
        # now we build and launch each productions
        for prodIndex, prodDict in prodsDict.items():

            if self.prodsToLaunch:
                if prodIndex not in self.prodsToLaunch:
                    continue

            # build the list of steps in a production
            stepsInProd = []
            for stepID in prodDict["stepsInProd-ProdName"]:
                for step in stepsListDict:
                    if step["prodStepID"] == stepID:
                        stepsInProd.append(stepsListDict.pop(stepsListDict.index(step)))
            # NOT READY (alternative to previous 5 lines)
            # build the DAG of steps in a production
            # stepsInProdDAG = self._getStepsInProdDAG( prodDict, stepsListDict )
            # Here, for today it is just convert to a list
            # TODO: fix this in order to properly use DAGs (now it's only sequential)
            # FIXME: using getIndexNodes we can't assure the order is respected
            # stepsInProd = stepsInProdDAG.getIndexNodes()

            if prodDict["previousProd"] is not None:
                fromProd = prodsLaunched[prodDict["previousProd"] - 1]
                self.previousProdID = fromProd

            prod = self._buildProduction(
                prodType=prodDict["productionType"],
                stepsInProd=stepsInProd,
                outputSE=prodDict["outputSE"],
                priority=prodDict["priority"],
                cpu=prodDict["cpu"],
                inputDataList=prodDict["input"],
                outputMode=prodDict["outputMode"],
                inputDataPolicy=prodDict["inputDataPolicy"],
                outputFileMask=prodDict["outputFileMask"],
                outputFileStep=prodDict["outputFileStep"],
                target=prodDict["target"],
                removeInputData=prodDict["removeInputsFlag"],
                groupSize=prodDict["groupSize"],
                bkQuery=prodDict["bkQuery"],
                plugin=prodDict["plugin"],
                previousProdID=fromProd,
                derivedProdID=prodDict["derivedProduction"],
                transformationFamily=prodDict["transformationFamily"],
                events=prodDict["events"],
                multicore=prodDict["multicore"],
                processors=prodDict["processors"],
                ancestorDepth=prodDict["ancestorDepth"],
            )

            # if the production is a simulation production type, submit it to the automated testing
            if (
                prodDict["productionType"]
                in self.opsH.getValue("Transformations/ExtendableTransfTypes", ["MCSimulation"])
                and self.mcTesting
            ):
                prodID = self._mcSpecialCase(prod, prodDict)

            else:
                res = self.diracProduction.launchProduction(
                    prod=prod,
                    publishFlag=self.publishFlag,
                    testFlag=self.testFlag,
                    requestID=self.requestID,
                    tracking=prodDict["tracking"],
                )
                if not res["OK"]:
                    raise RuntimeError(res["Message"])

                prodID = res["Value"]

            prodsLaunched.append(prodID)

            if self.publishFlag:
                self.logger.notice(
                    "For request %d, submitted Production" % self.requestID,
                    "%d, of type %s, ID = %s" % (prodIndex, prodDict["productionType"], str(prodID)),
                )
        return S_OK(prodsLaunched)

    #############################################################################

    def _getStepsInProdDAG(self, prodDict, stepsListDict, stepsOrder="sequential"):
        """Builds the DAG of steps in a production.

        :params dict prodDict: dictionary representing one production
        :params list stepsListDict: list of steps (which are dictionaries) that should be in the production

        :returns: stepsInProd (DAG)
        """
        stepsInProd = DAG()

        inserted = None
        for stepID in prodDict["stepsInProd-ProdName"]:
            for step in stepsListDict:
                if step["prodStepID"] == stepID:
                    ind = stepsListDict.index(step)
                    step = stepsListDict.pop(ind)
                    stepsInProd.addNode(step)
                    if inserted and stepsOrder == "sequential":
                        stepsInProd.addEdge(inserted, step)
                    inserted = step

        return stepsInProd

    def _mcSpecialCase(self, prod, prodDict):
        """Treating the MC special case for putting MC productions in status
        "Testing"."""

        # save the original xml before it is edited for testing
        prod._lastParameters()  # pylint: disable=protected-access

        # launchProduction adds extra parameters, as we 'hot swap' the xml, we
        # need to get these parameters for the un-edited version
        originalProcessingType = prod.prodGroup
        originalPriority = prod.priority

        prodXML = prod.LHCbJob.workflow.toXML()

        prodID = self._modifyAndLaunchMCXML(prod, prodDict)

        # load a production from the original xml to save the priority and processing type
        workflowToSave = fromXMLString(prodXML)
        prod.LHCbJob.workflow = workflowToSave
        prod.setParameter("ProcessingType", "JDL", str(originalProcessingType), "ProductionGroupOrType")
        prod.setParameter("Priority", "JDL", str(originalPriority), "Job Priority")

        # original xml to save
        descriptionToStore = prod.LHCbJob.workflow.toXML()

        # saving the original xml in the StoredJobDescription table.
        res = self.tc.addStoredJobDescription(prodID, descriptionToStore)
        if not res["OK"]:
            self.logger.error("Error calling addStoredJobDescription", res["Message"])
            self.logger.info("Cleaning created production and exiting")
            self.diracProduction.production(res["Value"], "cleaning")
            raise RuntimeError(res["Message"])

        return prodID

    def _modifyAndLaunchMCXML(self, prod, prodDict):
        """Apply modifications to the workflow XML for MC testing case.

        :param Production prod: Production object
        :param dict prodDict: dictionary with production info

        :returns: res['OK'] or res['ERROR']
        """
        # set the destination and number of events for testing
        destination = self.opsH.getValue("Productions/MCTesting/MCTestingDestination", "DIRAC.Test.ch")
        numberOfEvents = self.opsH.getValue("Productions/MCTesting/numberOfEvents", "500")
        extendBy = self.opsH.getValue("Productions/MCTesting/extendBy", 20)

        prod.setJobParameters({"Destination": destination})
        prod.LHCbJob.workflow.removeParameter("BannedSites")
        prod.setParameter("numberOfEvents", "string", str(numberOfEvents), "Number of events to test")

        # add '1' to the stepMask and add GAUSSHIST to the fileMask
        fileTypesOutLastStep = (
            prod.LHCbJob.workflow.step_instances[-2].findParameter("listoutput").getValue()[0]["outputDataType"]
        )
        newFileMask = ["GAUSSHIST"] + [ftOut.upper() for ftOut in fileTypesOutLastStep.split(";")]
        stepMaskParameter = prod.LHCbJob.workflow.findParameter("outputDataStep")
        if stepMaskParameter:
            stepMask = stepMaskParameter.getValue().replace(" ", "").split(";")
            newOutputFileStep = ";".join(sorted(list(set(["1"]).union(set(stepMask)))))
        else:
            newOutputFileStep = "1"
        prod.setFileMask(newFileMask, newOutputFileStep)

        # find the file types out already built, append GAUSSHIST and set the new listoutput
        fileTypesOut = (
            prod.LHCbJob.workflow.step_instances[0].findParameter("listoutput").getValue()[0]["outputDataType"]
        )
        fileTypesOut = fileTypesOut.split(", ")
        fileTypesOut.append("GAUSSHIST")
        outputFilesList = prod._constructOutputFilesList(fileTypesOut)  # pylint: disable=protected-access
        prod.LHCbJob.workflow.step_instances[0].setValue("listoutput", outputFilesList)

        # increase the priority to 10
        prod.priority = 10

        # launch the test production
        res = self.diracProduction.launchProduction(
            prod=prod,
            publishFlag=self.publishFlag,
            testFlag=self.testFlag,
            requestID=self.requestID,
            extend=extendBy,
            tracking=prodDict["tracking"],
            MCsimflag=True,
        )
        if not res["OK"]:
            self.logger.error("Error launching production", res["Message"])
            raise RuntimeError(res["Message"])

        return res["Value"]

    def _determineOutputSEs(self):
        """Fill outputSEsPerFileType based on outputSEs, fullListOfOutputFileTypes
        and specialOutputSEs."""
        for outputSE, specialOutputSEs in zip(self.outputSEs, self.specialOutputSEs):
            outputSEDict = {}
            if not self.fullListOfOutputFileTypes:
                raise ValueError("No steps defined")
            outputSEDict = dict([(fType, outputSE) for fType in self.fullListOfOutputFileTypes])
            if specialOutputSEs:
                outputSEDict.update(specialOutputSEs)
            self.outputSEsPerFileType.append(outputSEDict)

    def _applyOptionalCorrections(self):
        """if needed, calls _splitIntoProductionSteps.

        It also applies other changes
        """
        if len(self.bkQueries) != len(self.prodsTypeList):
            self.bkQueries += ["fromPreviousProd"] * (len(self.prodsTypeList) - len(self.bkQueries))

        if len(self.previousProds) != len(self.prodsTypeList):
            self.previousProds += range(1, len(self.prodsTypeList))

        if len(self.events) != len(self.prodsTypeList):
            self.events += ["-1"] * (len(self.prodsTypeList) - len(self.events))

        if not self.removeInputsFlags:
            removeInputsFlags = []
            for prodType in self.prodsTypeList:
                if prodType.lower() == "merge":
                    removeInputsFlags.append(True)
                else:
                    removeInputsFlags.append(False)
            self.removeInputsFlags = removeInputsFlags

        if not self.outputFileMasks:
            self.outputFileMasks = [""] * len(self.prodsTypeList)

        if not self.outputFileSteps:
            self.outputFileSteps = [""] * len(self.prodsTypeList)

        if not self.inputs:
            self.inputs = [[]] * len(self.prodsTypeList)

        if not self.outputModes:
            self.outputModes = ["Any"] * len(self.prodsTypeList)

        if not self.targets:
            self.targets = [""] * len(self.prodsTypeList)

        if not self.inputDataPolicies:
            self.inputDataPolicies = ["download"] * len(self.prodsTypeList)

        if not self.multicore:
            self.multicore = ["True"] * len(self.prodsTypeList)

        if not self.processors:
            self.processors = [(0, 0)] * len(self.prodsTypeList)

        if not self.specialOutputSEs:
            self.specialOutputSEs = [{}] * len(self.prodsTypeList)

        if not self.ancestorDepths:
            self.ancestorDepths = [0] * len(self.prodsTypeList)

        # Checking if we need to split the merging step into many productions
        if "merge" in [pt.lower() for pt in self.prodsTypeList]:
            i = 0
            indexes = []
            for pt in self.prodsTypeList:
                if pt.lower() == "merge":
                    indexes.append(i)
                i += 1

            for index in indexes:
                # In this case and only in this case I have to split the merging in many productions
                plugin = self.plugins[index]
                outputSE = self.outputSEs[index]
                specialOutputSE = self.specialOutputSEs[index]
                priority = self.priorities[index]
                cpu = self.cpus[index]
                bkQuery = self.bkQueries[index]
                groupSize = self.groupSizes[index]
                preProd = self.previousProds[index]
                removeInputsFlag = self.removeInputsFlags[index]
                outputFileMask = self.outputFileMasks[index]
                outputFileStep = self.outputFileSteps[index]
                inputs = self.inputs[index]
                idp = self.inputDataPolicies[index]
                stepID = self.stepsList[index]
                events = self.events[index]
                targets = self.targets[index]
                multicore = self.multicore[index]
                processors = self.processors[index]
                outputMode = self.outputModes[index]
                ancestorDepth = self.ancestorDepths[index]
                if plugin.lower() != "byrunfiletypesizewithflush" and "rootmerging" not in plugin.lower():
                    stepToSplit = self.stepsListDict[index]
                    numberOfProdsToInsert = len(stepToSplit["fileTypesOut"])
                    self.prodsTypeList.remove("Merge")
                    self.plugins.pop(index)
                    self.outputSEs.pop(index)
                    self.specialOutputSEs.pop(index)
                    self.priorities.pop(index)
                    self.cpus.pop(index)
                    self.bkQueries.pop(index)
                    self.previousProds.pop(index)
                    self.groupSizes.pop(index)
                    self.removeInputsFlags.pop(index)
                    self.outputFileMasks.pop(index)
                    self.outputFileSteps.pop(index)
                    self.inputs.pop(index)
                    self.inputDataPolicies.pop(index)
                    self.stepsList.pop(index)
                    self.events.pop(index)
                    self.targets.pop(index)
                    self.multicore.pop(index)
                    self.processors.pop(index)
                    self.outputModes.pop(index)
                    self.ancestorDepths.pop(index)
                    newSteps = _splitIntoProductionSteps(stepToSplit)
                    newSteps.reverse()
                    self.stepsListDict.remove(stepToSplit)
                    last = self.stepsInProds.pop(index)[0]
                    for x in range(numberOfProdsToInsert):
                        self.prodsTypeList.insert(index, "Merge")
                        self.plugins.insert(index, plugin)
                        self.outputSEs.insert(index, outputSE)
                        self.specialOutputSEs.insert(index, specialOutputSE)
                        self.priorities.insert(index, priority)
                        self.cpus.insert(index, cpu)
                        self.bkQueries.insert(index, bkQuery)
                        self.groupSizes.insert(index, groupSize)
                        self.removeInputsFlags.insert(index, removeInputsFlag)
                        self.outputFileMasks.insert(index, outputFileMask)
                        self.outputFileSteps.insert(index, outputFileStep)
                        self.inputs.insert(index, inputs)
                        self.inputDataPolicies.insert(index, idp)
                        self.stepsList.insert(index, stepID)
                        self.previousProds.insert(index, preProd)
                        self.stepsListDict.insert(index, newSteps[x])
                        self.stepsInProds.insert(index + x, [last + x])
                        self.events.insert(index, events)
                        self.targets.insert(index, targets)
                        self.multicore.insert(index, multicore)
                        self.processors.insert(index, processors)
                        self.outputModes.insert(index, outputMode)
                        self.ancestorDepths.insert(index, ancestorDepth)

        correctedStepsInProds = []
        toInsert = self.stepsInProds[0][0]
        lengths = [len(x) for x in self.stepsInProds]
        for length in lengths:
            li = [toInsert + x for x in range(length)]
            toInsert += length
            correctedStepsInProds.append(li)

        self.stepsInProds = correctedStepsInProds

    #############################################################################

    def _getProdsDescriptionDict(self):
        """Returns a dictionary representing the description of the request (of all
        the productions in it)"""

        prodsDict = {}

        prodNumber = 1

        for (
            prodType,
            stepsInProd,
            bkQuery,
            removeInputsFlag,
            outputSE,
            priority,
            cpu,
            inputD,
            outputMode,
            outFileMask,
            outFileStep,
            target,
            groupSize,
            plugin,
            idp,
            previousProd,
            events,
            multicore,
            processors,
            ancestorDepth,
        ) in zip(
            self.prodsTypeList,
            self.stepsInProds,
            self.bkQueries,
            self.removeInputsFlags,
            self.outputSEsPerFileType,
            self.priorities,
            self.cpus,
            self.inputs,
            self.outputModes,
            self.outputFileMasks,
            self.outputFileSteps,
            self.targets,
            self.groupSizes,
            self.plugins,
            self.inputDataPolicies,
            self.previousProds,
            self.events,
            self.multicore,
            self.processors,
            self.ancestorDepths,
        ):

            if not self.parentRequestID and self.requestID:
                transformationFamily = self.requestID
            else:
                transformationFamily = self.parentRequestID

            stepsInProdProdNameList = [
                str(self.stepsList[index - 1]) + str(self.stepsListDict[index - 1]["fileTypesIn"])
                for index in stepsInProd
            ]
            prodsDict[prodNumber] = {
                "productionType": prodType,
                "stepsInProd": [self.stepsList[index - 1] for index in stepsInProd],
                "bkQuery": bkQuery,
                "removeInputsFlag": removeInputsFlag,
                "tracking": 0,
                "outputSE": outputSE,
                "priority": priority,
                "cpu": cpu,
                "input": inputD,
                "outputMode": outputMode,
                "outputFileMask": outFileMask,
                "outputFileStep": outFileStep,
                "target": target,
                "groupSize": groupSize,
                "plugin": plugin,
                "inputDataPolicy": idp,
                "derivedProduction": 0,
                "transformationFamily": transformationFamily,
                "previousProd": previousProd,
                "stepsInProd-ProdName": stepsInProdProdNameList,
                "events": events,
                "multicore": multicore,
                "processors": processors,
                "ancestorDepth": ancestorDepth,
            }
            prodNumber += 1

        # tracking the last production(s)
        prodsDict[prodNumber - 1]["tracking"] = 1
        typeOfLastProd = prodsDict[prodNumber - 1]["productionType"]
        index = 2
        try:
            while prodsDict[prodNumber - index]["productionType"] == typeOfLastProd:
                prodsDict[prodNumber - index]["tracking"] = 1
                index += 1
        except KeyError:
            pass

        # production derivation, if necessary
        if self.derivedProduction:
            prodsDict[1]["derivedProduction"] = self.derivedProduction

        return prodsDict

    #############################################################################

    def _buildProduction(
        self,
        prodType,
        stepsInProd,
        outputSE,
        priority,
        cpu,
        inputDataList=None,
        outputMode="Any",
        inputDataPolicy="download",
        outputFileMask="",
        outputFileStep="",
        target="",
        removeInputData=False,
        groupSize=1,
        bkQuery=None,
        plugin="",
        previousProdID=0,
        derivedProdID=0,
        transformationFamily=0,
        events=-1,
        multicore="True",
        processors=(0, 0),
        ancestorDepth=0,
    ):
        """Wrapper around Production API to build a production, given the needed
        parameters.

        Args:
          prodType (str): production type (e.g. 'DataStripping')
          stepsInProd (list): list of steps in the production
          outputSE (dict): dictionary that holds relation between file type and output SE
          priority (int): production priority
          cpu (int): CPU time, in HS06s for jobs in this production

        Returns:
          prod: a Production object
        """
        prod = Production()

        # non optional parameters
        prod.LHCbJob.setType(prodType)
        try:
            fTypeIn = [ft.upper() for ft in stepsInProd[0]["fileTypesIn"]]
        except IndexError:
            fTypeIn = []
        prod.LHCbJob.workflow.setName(
            "Request_%d_%s_%s_EventType_%s_%s_%s"
            % (
                self.requestID,
                prodType,
                self.prodGroup,
                self.eventType,
                "".join([x.split(".")[0] for x in fTypeIn]),
                self.appendName,
            )
        )
        prod.setBKParameters(
            configName=self.outConfigName,
            configVersion=self.configVersion,
            groupDescriptionOrStepsList=stepsInProd,
            conditions=self.dataTakingConditions,
        )
        prod.setParameter("eventType", "string", self.eventType, "Event Type of the production")
        prod.setParameter("numberOfEvents", "string", str(events), "Number of events requested")

        prod.setParameter("multicore", "string", multicore, "Flag for enabling gaudi parallel")
        if processors[0] or processors[1]:
            minProcs = processors[0] if processors[0] else None
            maxProcs = processors[1] if processors[1] else None
            prod.LHCbJob.setNumberOfProcessors(minNumberOfProcessors=minProcs, maxNumberOfProcessors=maxProcs)
        prod.prodGroup = self.prodGroup
        prod.priority = priority
        prod.LHCbJob.workflow.setDescrShort("prodDescription")
        prod.LHCbJob.workflow.setDescription("prodDescription")
        prod.LHCbJob.setCPUTime(cpu)
        prod.plugin = plugin

        # optional parameters
        prod.jobFileGroupSize = groupSize
        if inputDataPolicy:
            prod.LHCbJob.setInputDataPolicy(inputDataPolicy)
        prod.setOutputMode(outputMode)
        if outputFileMask:
            outputFileMask = [m.lower() for m in outputFileMask.replace(" ", "").split(",")]
        if outputFileStep:
            if isinstance(outputFileStep, six.string_types):
                outputFileStep = [m.lower() for m in outputFileStep.replace(" ", "").split(",")]
        prod.setFileMask(outputFileMask, outputFileStep)
        if target:
            if target == "Tier2":
                prod.banTier1s()
            elif "BAN" in target:
                sitesToBan = target.split(":")
                if len(sitesToBan) > 1:
                    prod.banSites(sitesToBan[1:])
            elif target != "ALL":
                prod.LHCbJob.setDestination(target)
        prod.LHCbJob.setInputData(inputDataList)
        if ancestorDepth:
            prod.LHCbJob.setAncestorDepth(ancestorDepth)
        if derivedProdID:
            prod.ancestorProduction = derivedProdID
        if transformationFamily:
            prod.transformationFamily = transformationFamily
        if self.fractionToProcess:
            prod.setParameter("FractionToProcess", "string", str(self.fractionToProcess), "Fraction to process")
        if self.minFilesToProcess:
            prod.setParameter("MinFilesToProcess", "string", str(self.minFilesToProcess), "Min N of Files to process")
        if self.processingPass:
            prod.setParameter(
                "processingPass", "string", self.processingPass, "Processing pass of input for the request"
            )

        # Adding optional input BK query
        if bkQuery:
            if bkQuery.lower() == "full":
                prod.inputBKSelection = self._getBKKQuery()
            elif bkQuery.lower() == "frompreviousprod":
                prod.inputBKSelection = self._getBKKQuery("frompreviousprod", fTypeIn, previousProdID)

        self.logger.verbose("Launching with BK selection %s" % prod.inputBKSelection)

        prod = self._addStepsToProd(prod, stepsInProd, removeInputData=removeInputData)

        for ft, oSE in outputSE.items():
            prod.outputSEs.setdefault(ft, oSE)

        prod.LHCbJob.setDIRACPlatform()

        return prod

    #############################################################################

    def _addStepsToProd(self, prod, stepsInProd, stepsSequence="sequential", removeInputData=False):
        """Given a Production object, add requested steps (application and
        finalization)

        Args:
          prod (Production): the Production object to which the steps are added
          stepsInProd (DAG): DAG of steps in a production
          stepsSequence (str or dict): applications steps sequence
          removeInputData (bool): flag that indicates if the input data should be removed (for the finalization step)

        Returns:
          prod with steps added
        """
        # Adding the application steps
        firstStep = stepsInProd.pop(0)
        stepName = prod.addApplicationStep(
            stepDict=firstStep, modulesList=self.modulesList, extraModulesList=self.extraModulesList
        )
        prod.gaudiSteps.append(stepName)

        for step in stepsInProd:
            stepName = prod.addApplicationStep(
                stepDict=step,
                inputData="previousStep",
                modulesList=self.modulesList,
                extraModulesList=self.extraModulesList,
            )
            prod.gaudiSteps.append(stepName)

        # Adding the finalization step
        if removeInputData:
            prod.addFinalizationStep(
                ["UploadOutputData", "RemoveInputData", "UploadLogFile", "UploadMC", "FailoverRequest"]
            )
        else:
            prod.addFinalizationStep()

        return prod

    def _getBKKQuery(self, mode="full", fileType=None, previousProdID=0):
        """simply creates the bkk query dictionary."""

        if fileType is None:
            fileType = []

        if mode.lower() == "full":
            bkQuery = {
                "FileType": ";;;".join(self.bkFileType),
                "EventType": str(self.eventType),
                "ConfigName": self.configName,
                "ConfigVersion": self.configVersion,
            }

            if self.dataTakingConditions:
                bkQuery["DataTakingConditions"] = self.dataTakingConditions

            if self.processingPass:
                bkQuery["ProcessingPass"] = self.processingPass

            if self.dqFlag:
                bkQuery["DataQualityFlag"] = self.dqFlag.replace(",", ";;;").replace(" ", "")

            if self.startRun and self.runsList or self.endRun and self.runsList:
                raise ValueError("Please don't mix runs list with start/end run")

            if self.endRun and self.startRun:
                if self.endRun < self.startRun:
                    gLogger.error(
                        "Your end run '%d' should be more than your start run '%d'!" % (self.endRun, self.startRun)
                    )
                    raise ValueError("Error setting start or end run")

            if self.startRun:
                bkQuery["StartRun"] = self.startRun
            if self.endRun:
                bkQuery["EndRun"] = self.endRun

            if self.runsList:
                bkQuery["RunNumbers"] = self.runsList.replace(",", ";;;").replace(" ", "")

            if self.visibility:
                bkQuery["Visible"] = self.visibility

        elif mode.lower() == "frompreviousprod":
            bkQuery = {"FileType": ";;;".join(fileType).replace(" ", ""), "ProductionID": int(previousProdID)}

            if self.eventType:
                bkQuery["EventType"] = str(self.eventType)

            if self.dqFlag:
                bkQuery["DataQualityFlag"] = self.dqFlag.replace(",", ";;;").replace(" ", "")

        return bkQuery

    ################################################################################
    # properties

    def set_stepsList(self, value):
        listInt = []
        i = 0
        while True:
            try:
                listInt.append(int(value[i]))
                i = i + 1
            except ValueError:
                break
            except IndexError:
                break
        self._stepsList = listInt

    def get_stepsList(self):
        return self._stepsList

    stepsList = property(get_stepsList, set_stepsList)

    def set_startRun(self, value):
        if isinstance(value, six.string_types):
            value = int(value)
        if value < 0:
            raise ValueError("startRun can not be negative")
        self._startRun = value

    def get_startRun(self):
        return self._startRun

    startRun = property(get_startRun, set_startRun)

    def set_endRun(self, value):
        if isinstance(value, six.string_types):
            value = int(value)
        if value < 0:
            raise ValueError("endRun can not be negative")
        self._endRun = value

    def get_endRun(self):
        return self._endRun

    endRun = property(get_endRun, set_endRun)

    def set_requestID(self, value):
        if value == "":
            value = 0
        if isinstance(value, six.string_types):
            value = int(value)
        if value < 0:
            raise ValueError("requestID can not be negative")
        self._requestID = value

    def get_requestID(self):
        return self._requestID

    requestID = property(get_requestID, set_requestID)

    def set_parentRequestID(self, value):
        if value == "":
            value = 0
        if isinstance(value, six.string_types):
            value = int(value)
        if value < 0:
            raise ValueError("parentRequestID can not be negative")
        self._parentRequestID = value

    def get_parentRequestID(self):
        return self._parentRequestID

    parentRequestID = property(get_parentRequestID, set_parentRequestID)

    def set_bkFileType(self, value):
        if isinstance(value, str):
            value = value.replace(" ", "").split(",")
        self._bkFileType = value

    def get_bkFileType(self):
        return self._bkFileType

    bkFileType = property(get_bkFileType, set_bkFileType)


#############################################################################


def _splitIntoProductionSteps(step):
    """Given a list of bookkeeping steps, produce production steps."""
    prodSteps = []

    if len(step["fileTypesIn"]) <= 1:
        prodSteps.append(step)
    else:
        if set(step["fileTypesOut"]) > set(step["fileTypesIn"]):
            raise ValueError(
                "Step outputs %s are not part of the inputs %s...?"
                % (str(step["fileTypesOut"]), str(step["fileTypesIn"]))
            )
        for outputTypes in step["fileTypesOut"]:
            prodStep = copy.deepcopy(step)
            prodStep["fileTypesIn"] = [outputTypes]
            prodStep["fileTypesOut"] = [outputTypes]
            prodStep["prodStepID"] = str(prodStep["StepId"]) + str(prodStep["fileTypesIn"])
            prodSteps.append(prodStep)

    return prodSteps


#############################################################################
