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
"""Moving toward a templates-less system.

The RecoStripping Template creates workflows for the following use-cases:
  WORKFLOW1: Reconstruction
  WORKFLOW2: Stripping+Merge
  WORKFLOW3: RecoStripping+Merge (Reco and Stripping within the same job)
  WORKFLOW4: Reconstruction+Stripping+Merge
  WORKFLOW5: Stripping+Merge+Indexing

Exotic things you might want to do:
* run a local test:
  pre: remember to check if your input file is online, if not use lcg-bringonline <PFN>
* run only part of the request on the Grid:
"""
from six.moves import range

import ast

from DIRAC.Core.Base.Script import Script

Script.parseCommandLine()

from DIRAC import gConfig, gLogger, exit as DIRACexit
from LHCbDIRAC.ProductionManagementSystem.Client.ProductionRequest import ProductionRequest

gLogger = gLogger.getSubLogger("RecoStripping_run.py")
currentSetup = gConfig.getValue("DIRAC/Setup")

pr = ProductionRequest()

stepsList = ["{{p1Step}}"]
stepsList.append("{{p2Step}}")
stepsList.append("{{p3Step}}")
stepsList.append("{{p4Step}}")
stepsList.append("{{p5Step}}")
stepsList.append("{{p6Step}}")
stepsList.append("{{p7Step}}")
stepsList.append("{{p8Step}}")
stepsList.append("{{p9Step}}")
pr.stepsList = stepsList

###########################################
# Configurable and fixed parameters
###########################################

pr.appendName = "{{WorkflowAppendName#GENERAL: Workflow string to append to production name#1}}"

w = "{{w#----->WORKFLOW: choose one below#}}"
w1 = "{{w1#-WORKFLOW1: Reconstruction#False}}"
w2 = "{{w2#-WORKFLOW2: Stripping+Merge#False}}"
w3 = "{{w3#-WORKFLOW3: RecoStripping+Merge#False}}"
w4 = "{{w4#-WORKFLOW4: Reconstruction+Stripping+Merge#False}}"
w5 = "{{w5#-WORKFLOW5: Stripping+Merge+Indexing #False}}"

localTestFlag = "{{localTestFlag#GENERAL: Set True for local test#False}}"
validationFlag = "{{validationFlag#GENERAL: Set True for validation prod#False}}"

# workflow params for all productions
pr.startRun = "{{startRun#GENERAL: run start, to set the start run#0}}"
pr.endRun = "{{endRun#GENERAL: run end, to set the end of the range#0}}"
pr.derivedProduction = "{{AncestorProd#GENERAL: ancestor prod to be derived#0}}"

# reco params
recoPriority = int("{{RecoPriority#PROD-1:RECO(Stripp): priority#2}}")
recoCPU = "{{RecoMaxCPUTime#PROD-1:RECO(Stripp): Max CPU time in secs#1500000}}"
recoPlugin = "{{RecoPluginType#PROD-1:RECO(Stripp): production plugin name#RAWProcessing}}"
recoFilesPerJob = "{{RecoFilesPerJob#PROD-1:RECO(Stripp): Group size or number of files per job#1}}"
recoDataSE = "{{RecoDataSE#PROD-1:RECO(Stripp): Output Data Storage Element#Tier1-Buffer}}"
try:
    recoDataSESpecial = ast.literal_eval(
        "{{RecoDataSESpecial#PROD-1:RECO(Stripp): Special SE (a dictionary Type:SE)#}}"
    )
except SyntaxError:
    recoDataSESpecial = {}
recoAncestorDepth = int("{{recoAncestorDepth#PROD-1: Ancestor Depth#0}}")
recoCompressionLvl = "{{recoCompressionLvl#PROD-1: compression level#LOW}}"
recoOutputVisFlag = "{{recoOutputVisFlag#PROD-1: Visibility flag of output files #Y}}"
try:
    recoOutputVisFlagSpecial = ast.literal_eval(
        "{{recoOutputVisFlagSpecial#PROD-1: Special Visibility flag of output files (dict FType:Y|N )#}}"
    )
except SyntaxError:
    recoOutputVisFlagSpecial = {}

# stripp params
strippPriority = int("{{priority#PROD-2:Stripping: priority#2}}")
strippCPU = "{{StrippMaxCPUTime#PROD-2:Stripping: Max CPU time in secs#1000000}}"
strippPlugin = "{{StrippPluginType#PROD-2:Stripping: plugin name#ByRunWithFlush}}"
strippFilesPerJob = "{{StrippFilesPerJob#PROD-2:Stripping: Group size or number of files per job#2}}"
strippDataSE = "{{StrippStreamSE#PROD-2:Stripping: output data SE (un-merged streams)#Tier1-Buffer}}"
try:
    strippDataSESpecial = ast.literal_eval(
        "{{StrippDataSESpecial#PROD-2:Stripping: Special SE (a dictionary Type:SE)#}}"
    )
except SyntaxError:
    strippDataSESpecial = {}
strippAncestorDepth = int("{{strippAncestorDepth#PROD-2: Ancestor Depth#0}}")
strippCompressionLvl = "{{strippCompressionLvl#PROD-2: compression level#LOW}}"
strippOutputVisFlag = "{{strippOutputVisFlag#PROD-2: Visibility flag of output files#N}}"
try:
    strippOutputVisFlagSpecial = ast.literal_eval(
        "{{strippOutputVisFlagSpecial#PROD-2: Special Visibility flag of output files (dict FType:Y|N)#}}"
    )
except SyntaxError:
    strippOutputVisFlagSpecial = {}

# merging params
mergingPriority = int("{{MergePriority#PROD-3:Merging: priority#8}}")
mergingCPU = "{{MergeMaxCPUTime#PROD-3:Merging: Max CPU time in secs#300000}}"
mergingPlugin = "{{MergePlugin#PROD-3:Merging: plugin#ByRunFileTypeSizeWithFlush}}"
mergingGroupSize = "{{MergeFileSize#PROD-3:Merging: Size (in GB) of the merged files#5}}"
mergingDataSE = "{{MergeStreamSE#PROD-3:Merging: output data SE (merged streams)#Tier1-DST}}"
try:
    mergingDataSESpecial = ast.literal_eval(
        "{{MergingDataSESpecial#PROD-3:Merging: Special SE (a dictionary Type:SE)#}}"
    )
except SyntaxError:
    mergingDataSESpecial = {}
mergingRemoveInputsFlag = "{{MergeRemoveFlag#PROD-3:Merging: remove input data flag True/False#True}}"
mergeCompressionLvl = "{{mergeCompressionLvl#PROD-3: compression level#HIGH}}"
mergeOutputVisFlag = "{{mergeOutputVisFlag#PROD-3: Visibility flag of output files#Y}}"
try:
    mergeOutputVisFlagSpecial = ast.literal_eval(
        "{{mergeOutputVisFlagSpecial#PROD-3: Special Visibility flag of output files (dict FType:Y|N)#}}"
    )
except SyntaxError:
    mergeOutputVisFlagSpecial = {}

# indexing params
indexingPriority = int("{{IndexingPriority#PROD-4:indexing: priority#5}}")
indexingCPU = "{{IndexingMaxCPUTime#PROD-4:indexing: Max CPU time in secs#50000}}"
indexingPlugin = "{{IndexingPlugin#PROD-4:indexing: plugin#ByRunFileTypeSizeWithFlush}}"
indexingGroupSize = "{{IndexingFileSize#PROD-4:indexing: Size (in GB) of the Indexed files#50}}"
indexingDataSE = "{{IndexingStreamSE#PROD-4:indexing: output data SE (Indexed streams)#IndexerSE}}"

pr.requestID = "{{ID}}"
pr.prodGroup = "{{inProPass}}" + "/" + "{{pDsc}}"
# used in case of a test e.g. certification etc.
pr.configName = "{{configName}}"
pr.configVersion = "{{configVersion}}"
# Other parameters from the request page
pr.dqFlag = "{{inDataQualityFlag}}"  # UNCHECKED
pr.dataTakingConditions = "{{simDesc}}"
pr.processingPass = "{{inProPass}}"
pr.bkFileType = "{{inFileType}}"
pr.eventType = "{{eventType}}"
pr.visibility = "Yes"
recoType = "DataReconstruction"
targetSite = "ALL"
recoMulticoreFlag = strippMulticoreFlag = mergeMulticoreFlag = "True"
recoIDPolicy = strippIDPolicy = mergingIDPolicy = indexingIDPolicy = "download"


w1 = ast.literal_eval(w1)
w2 = ast.literal_eval(w2)
w3 = ast.literal_eval(w3)
w4 = ast.literal_eval(w4)
w5 = ast.literal_eval(w5)

localTestFlag = ast.literal_eval(localTestFlag)
validationFlag = ast.literal_eval(validationFlag)

mergeRemoveInputsFlag = ast.literal_eval(mergingRemoveInputsFlag)

if not w1 and not w2 and not w3 and not w4:
    gLogger.error("I told you to select at least one workflow!")
    DIRACexit(2)

if localTestFlag:
    pr.testFlag = True
    pr.publishFlag = False
    pr.prodsToLaunch = [1]

recoInputDataList = []
strippInputDataList = []
if not pr.publishFlag:
    # this is 1380Gev MagUp
    # recoTestData = 'LFN:/lhcb/data/2011/RAW/FULL/LHCb/COLLISION11/88162/088162_0000000020.raw'
    # this is collision11
    recoTestData = "LFN:/lhcb/data/2011/RAW/FULL/LHCb/COLLISION11/89333/089333_0000000003.raw"
    recoInputDataList.append(recoTestData)
    recoIDPolicy = "protocol"

    strippTestData = "LFN:/lhcb/data/2010/SDST/00008375/0001/00008375_00016947_1.sdst"
    strippInputDataList.append(strippTestData)
    #  strippTestDataRAW = 'LFN:/lhcb/data/2010/RAW/FULL/LHCb/COLLISION10/75338/075338_0000000069.raw'
    #  strippInputDataList.append( strippTestDataRAW )
    strippIDPolicy = "protocol"
    evtsPerJob = "2000"


pr.outConfigName = pr.configName

# In case we want just to test, we publish in the certification/test part of the BKK
if currentSetup == "LHCb-Certification" or pr.testFlag:
    pr.outConfigName = "certification"
    if "lhcb" not in pr.configName.lower():  # in case of reconstruction
        pr.configVersion = "test"

if pr.testFlag:
    pr.dataTakingConditions = "Beam3500GeV-VeloClosed-MagUp"
    if w1 or w3:
        pr.events = ["25"]
        pr.processingPass = "Real Data"
        pr.bkFileType = "RAW"
    else:
        pr.events = ["2000"]
        pr.processingPass = "Real Data/Reco12"
        pr.bkFileType = "SDST"
    mergingGroupSize = "1"
    recoCPU = strippCPU = "200000"
    pr.startRun = "93718"
    pr.endRun = "93720"
    pr.eventType = "90000000"
    pr.dqFlag = "ALL"

if validationFlag:
    pr.outConfigName = "validation"

if w1:
    pr.prodsTypeList = [recoType]
    pr.outputSEs = [recoDataSE]
    pr.specialOutputSEs = [recoDataSESpecial]
    pr.stepsInProds = [list(range(1, len(pr.stepsList) + 1))]
    pr.removeInputsFlags = [False]
    pr.priorities = [recoPriority]
    pr.cpus = [recoCPU]
    pr.groupSizes = [recoFilesPerJob]
    pr.plugins = [recoPlugin]
    pr.inputs = [recoInputDataList]
    pr.inputDataPolicies = [recoIDPolicy]
    pr.bkQueries = ["Full"]
    pr.targets = [targetSite]
    pr.multicore = [recoMulticoreFlag]
    pr.outputModes = ["Run"]
    pr.ancestorDepths = [recoAncestorDepth]
    pr.compressionLvl = [recoCompressionLvl] * len(pr.stepsInProds[0])
    pr.outputVisFlag = [{str(i + 1): recoOutputVisFlag} for i in range(len(pr.stepsInProds[0]))]
    pr.specialOutputVisFlag = [{"1": recoOutputVisFlagSpecial}]

elif w2:
    pr.prodsTypeList = ["DataStripping", "Merge"]
    pr.outputSEs = [strippDataSE, mergingDataSE]
    pr.specialOutputSEs = [strippDataSESpecial, mergingDataSESpecial]
    pr.stepsInProds = [list(range(1, len(pr.stepsList))), [len(pr.stepsList)]]
    pr.removeInputsFlags = [False, mergeRemoveInputsFlag]
    pr.priorities = [strippPriority, mergingPriority]
    pr.cpus = [strippCPU, mergingCPU]
    pr.groupSizes = [strippFilesPerJob, mergingGroupSize]
    pr.plugins = [strippPlugin, mergingPlugin]
    pr.inputs = [strippInputDataList, []]
    pr.inputDataPolicies = [strippIDPolicy, mergingIDPolicy]
    pr.bkQueries = ["Full", "fromPreviousProd"]
    pr.targets = [targetSite, targetSite]
    pr.multicore = [strippMulticoreFlag, mergeMulticoreFlag]
    pr.outputModes = ["Run", "Run"]
    pr.ancestorDepths = [strippAncestorDepth, 0]
    pr.compressionLvl = [strippCompressionLvl] * len(pr.stepsInProds[0]) + [mergeCompressionLvl] * len(
        pr.stepsInProds[1]
    )
    pr.outputVisFlag = [{"1": strippOutputVisFlag}, {"2": mergeOutputVisFlag}]
    pr.specialOutputVisFlag = [{"1": strippOutputVisFlagSpecial}, {"2": mergeOutputVisFlagSpecial}]

elif w3:
    pr.prodsTypeList = [recoType, "Merge"]
    pr.outputSEs = [recoDataSE, mergingDataSE]
    pr.specialOutputSEs = [recoDataSESpecial, mergingDataSESpecial]
    pr.stepsInProds = [list(range(1, len(pr.stepsList))), [len(pr.stepsList)]]
    pr.removeInputsFlags = [False, mergeRemoveInputsFlag]
    pr.priorities = [recoPriority, mergingPriority]
    pr.cpus = [recoCPU, mergingCPU]
    pr.groupSizes = [recoFilesPerJob, mergingGroupSize]
    pr.plugins = [recoPlugin, mergingPlugin]
    pr.inputs = [recoInputDataList, []]
    pr.inputDataPolicies = [recoIDPolicy, mergingIDPolicy]
    pr.bkQueries = ["Full", "fromPreviousProd"]
    pr.targets = [targetSite, targetSite]
    pr.multicore = [recoMulticoreFlag, mergeMulticoreFlag]
    pr.outputModes = ["Run", "Run"]
    pr.ancestorDepths = [recoAncestorDepth, 0]
    pr.compressionLvl = [recoCompressionLvl] * len(pr.stepsInProds[0]) + [mergeCompressionLvl] * len(pr.stepsInProds[1])
    pr.outputVisFlag = [{"1": recoOutputVisFlag}, {"2": mergeOutputVisFlag}]
    pr.specialOutputVisFlag = [{"1": recoOutputVisFlagSpecial}, {"2": mergeOutputVisFlagSpecial}]

elif w4:
    pr.prodsTypeList = [recoType, "DataStripping", "Merge"]
    pr.outputSEs = [recoDataSE, strippDataSE, mergingDataSE]
    pr.specialOutputSEs = [recoDataSESpecial, strippDataSESpecial, mergingDataSESpecial]
    pr.stepsInProds = [
        list(range(1, len(pr.stepsList) - 1)),
        list(range(len(pr.stepsList) - 1, len(pr.stepsList))),
        [len(pr.stepsList)],
    ]
    pr.removeInputsFlags = [False, False, mergeRemoveInputsFlag]
    pr.priorities = [recoPriority, strippPriority, mergingPriority]
    pr.cpus = [recoCPU, strippCPU, mergingCPU]
    pr.groupSizes = [recoFilesPerJob, strippFilesPerJob, mergingGroupSize]
    pr.plugins = [recoPlugin, strippPlugin, mergingPlugin]
    pr.inputs = [recoInputDataList, [], []]
    pr.inputDataPolicies = [recoIDPolicy, strippIDPolicy, mergingIDPolicy]
    pr.bkQueries = ["Full", "fromPreviousProd", "fromPreviousProd"]
    pr.targets = [targetSite, targetSite, targetSite]
    pr.multicore = [recoMulticoreFlag, strippMulticoreFlag, mergeMulticoreFlag]
    pr.outputModes = ["Run", "Run", "Run"]
    pr.ancestorDepths = [recoAncestorDepth, strippAncestorDepth, 0]
    pr.compressionLvl = (
        [recoCompressionLvl] * len(pr.stepsInProds[0])
        + [strippCompressionLvl] * len(pr.stepsInProds[1])
        + [mergeCompressionLvl] * len(pr.stepsInProds[2])
    )
    pr.outputVisFlag = [{"1": recoOutputVisFlag}, {"2": strippOutputVisFlag}, {"3": mergeOutputVisFlag}]
    pr.specialOutputVisFlag = [
        {"1": recoOutputVisFlagSpecial},
        {"2": strippOutputVisFlagSpecial},
        {"3": mergeOutputVisFlagSpecial},
    ]

elif w5:
    pr.prodsTypeList = ["DataStripping", "Merge", "WGProduction"]
    pr.outputSEs = [strippDataSE, mergingDataSE, indexingDataSE]
    pr.specialOutputSEs = [strippDataSESpecial, mergingDataSESpecial, {}]
    pr.stepsInProds = [
        list(range(1, len(pr.stepsList) - 1)),
        list(range(len(pr.stepsList) - 1, len(pr.stepsList))),
        [len(pr.stepsList)],
    ]
    pr.removeInputsFlags = [False, mergeRemoveInputsFlag, False]
    pr.priorities = [strippPriority, mergingPriority, indexingPriority]
    pr.cpus = [strippCPU, mergingCPU, indexingCPU]
    pr.groupSizes = [strippFilesPerJob, mergingGroupSize, indexingGroupSize]
    pr.plugins = [strippPlugin, mergingPlugin, indexingPlugin]
    pr.inputs = [strippInputDataList, [], []]
    pr.inputDataPolicies = [strippIDPolicy, mergingIDPolicy, indexingIDPolicy]
    pr.bkQueries = ["Full", "fromPreviousProd", "fromPreviousProd"]
    pr.targets = [targetSite, targetSite, targetSite]
    pr.multicore = [strippMulticoreFlag, mergeMulticoreFlag, False]
    pr.outputModes = ["Run", "Run", "Any"]
    pr.ancestorDepths = [strippAncestorDepth, 0, 0]
    pr.compressionLvl = (
        [strippCompressionLvl] * len(pr.stepsInProds[0])
        + [mergeCompressionLvl] * len(pr.stepsInProds[1])
        + [""] * len(pr.stepsInProds[2])
    )
    pr.outputVisFlag = [{"1": strippOutputVisFlag}, {"2": mergeOutputVisFlag}]
    pr.specialOutputVisFlag = [{"1": strippOutputVisFlagSpecial}, {"2": mergeOutputVisFlagSpecial}]


pr.buildAndLaunchRequest()
