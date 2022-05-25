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
"""  The MC Simulation Template creates workflows for the following simulation
     use-cases:
      WORKFLOW1: Simulation+Selection+Merge
      WORKFLOW2: Simulation+Selection+MCMerge
      WORKFLOW3: Simulation+Selection
      WORKFLOW4: Simulation+MCMerge
      WORKFLOW5: Simulation

    Exotic things you might want to do:
    * run a local test:
      - of the MC: just set the localTestFlag to True
      - of the merging/stripping: set pr.prodsToLaunch to, e.g., [2], and adjust the pr.inputs at the end of the script
    * run only part of the request on the Grid:
      - for the MC: just set pr.prodsToLaunch = [1]
      - for the merge and/or stripping: set pr.prodsToLaunch, then set pr.previousProdID
"""
from six.moves import range

import ast

from DIRAC.Core.Base.Script import Script

Script.parseCommandLine()

from DIRAC import gConfig, gLogger, exit as DIRACexit
from LHCbDIRAC.ProductionManagementSystem.Client.ProductionRequest import ProductionRequest

#
# Link compression level to the output file visibility. If any file types is visible, the corresponding
# step takes the maximum compression level
# Input : dicts including the visibility of output files per step
# Output: modified list of compression levels
#


def modifyCompression(dict1, dict2, default):

    compression = []

    combinedVis = dict1.copy()
    combinedVis.update(dict2)
    for stepN in sorted(combinedVis):
        if combinedVis[stepN] == "Y":
            compression.append("HIGH")
        else:
            compression.append(default)

    return compression


#
# Simple "check" in case the visibility includes only one element
# Input : dict of visibility
# Output: modified dict of visibility
#


def fillVisList(vdict, num):

    # Assuming that, if there's only one element in the list of output visibility flags, every step will catch that flag
    if len(vdict) == 1:
        val = vdict[list(vdict)[0]]
        vdict = dict([(str(i), val) for i in range(int(list(vdict)[0]), int(list(vdict)[0]) + num)])
    # Another assumption: if the number of steps is bigger than that of vis flags,
    # then extend the list with the last flag available
    # to fill the "holes"
    # if len(vlist) < len(slist):
    #  vlist.extend( vlist[-1] * (len(slist) - len(vlist)) )

    return vdict


gLogger = gLogger.getSubLogger("MCSimulation_run.py")
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
stepsList.append("{{p10Step}}")
stepsList.append("{{p11Step}}")
stepsList.append("{{p12Step}}")
stepsList.append("{{p13Step}}")
stepsList.append("{{p14Step}}")
stepsList.append("{{p15Step}}")
stepsList.append("{{p16Step}}")
stepsList.append("{{p17Step}}")
stepsList.append("{{p18Step}}")
stepsList.append("{{p19Step}}")
stepsList.append("{{p20Step}}")
pr.stepsList = stepsList

###########################################
# Configurable and fixed parameters
###########################################

pr.appendName = "{{WorkflowAppendName#GENERAL: Workflow string to append to production name#1}}"

w = "{{w#----->WORKFLOW: choose one below#}}"
w1 = "{{w1#-WORKFLOW1: Simulation#False}}"
w2 = "{{w2#-WORKFLOW2: Simulation(Gauss) + AllOthers#False}}"
w3 = "{{w3#-WORKFLOW3: Simulation(Gauss) + AllOthers + Merge#False}}"

localTestFlag = "{{localTestFlag#GENERAL: Set True for local test#False}}"
validationFlag = "{{validationFlag#GENERAL: Set True for validation prod - will create histograms#False}}"

pr.configName = "{{BKConfigName#GENERAL: BK configuration name e.g. MC #MC}}"
extraOptions = "{{extraOptions#GENERAL: extra options as python dict stepID:options#}}"

targets = "{{Target#PROD-1:MC: Target for MC (e.g. Tier2, ALL, LCG.CERN.cern or BAN:site1:site2#ALL}}"
eventsPerJob = "{{eventsPerJob#PROD-1:MC: Number of events per job#-1}}"
MCPriority = "{{MCPriority#PROD-1:MC: Production priority#0}}"
MCmulticoreFlag = "{{MCMulticoreFLag#PROD-1:MC multicore flag#True}}"
MCNumberOfProcessors = "{{MCNumberOfProcessors#PROD-1:MC jobs min/max n of processors#0,0}}"
MCSimulationType = "{{MCSimulationType#PROD-1:MC: type of MCSimulation#MCSimulation}}"
pr.mcTesting = ast.literal_eval("{{MCTesting#PROD-1:MC: testing enabled#True}}")
simulationCompressionLvl = "{{simulationCompressionLvl#PROD-1: Compression level#LOW}}"

simulationOutputVisFlag = ast.literal_eval(
    '{{simulationOutputVisFlag#PROD-1: Simulation visib flag dictionary (one flag per step {"step":"Y|N"})#{} }}'
)
try:
    simVisFlagSpecial = "{{simulationOutputVisFlagSpecial"
    simVisFlagSpecial += "#PROD-1: Special Visibility flag of output files"
    simVisFlagSpecial += ' (a dictionary {"step n":{("FType":flag)}} )#}}'
    simulationOutputVisFlagSpecial = ast.literal_eval(simVisFlagSpecial)
except SyntaxError:
    simulationOutputVisFlagSpecial = {}

selectionPlugin = "{{selectionPlugin#PROD-2:Selection: plugin e.g. Standard, BySize#BySize}}"
selectionGroupSize = "{{selectionGroupSize#PROD-2:Selection: input files total size (we'll download)#5}}"
selectionPriority = "{{selectionPriority#PROD-2:Selection: Job Priority e.g. 8 by default#8}}"
selectionCPU = "{{selectionCPU#PROD-2:Selection: Max CPU time in secs#100000}}"
removeInputSelection = "{{removeInputSelection#PROD-2:Selection: remove inputs#True}}"
selmulticoreFlag = "{{selMulticoreFLag#PROD-2:Selection: multicore flag#True}}"
selNumberOfProcessors = "{{selNumberOfProcessors#PROD-2:Selection jobs min/max n of processors#0,0}}"
selectionCompressionLvl = "{{selectionCompressionLvl#PROD-2:Selection: Compression level#LOW}}"
selectionOutputVisFlag = ast.literal_eval(
    '{{selectionOutputVisFlag#PROD-2: Selection visibility flag dictionary ({"step n": "Y|N"})#{} }}'
)
try:
    selVisFlagSpecial = "{{selectionOutputVisFlagSpecial"
    selVisFlagSpecial += '#PROD-2: Special Visibility flag of output files (a dictionary {"step n":{"FType":flag}} )#}}'
    selectionOutputVisFlagSpecial = ast.literal_eval(selVisFlagSpecial)
except SyntaxError:
    selectionOutputVisFlagSpecial = {}

mergingPlugin = "{{MergingPlugin#PROD-3:Merging: plugin e.g. Standard, BySize#BySize}}"
mergingGroupSize = "{{MergingGroupSize#PROD-3:Merging: Group Size e.g. BySize = GB file size#5}}"
mergingPriority = "{{MergingPriority#PROD-3:Merging: Job Priority e.g. 8 by default#8}}"
mergingCPU = "{{mergingCPU#PROD-3:Merging: Max CPU time in secs#100000}}"
removeInputMerge = "{{removeInputMerge#PROD-3:Merging: remove inputs#True}}"
mergemulticoreFlag = "{{mergeMulticoreFLag#PROD-3:Merging: multicore flag#True}}"
mergeNumberOfProcessors = "{{mergeNumberOfProcessors#PROD-3:Merging jobs min/max n of processors#0,0}}"
mergeCompressionLvl = "{{mergeCompressionLvl#PROD-3:Merging: Compression level#HIGH}}"
mergeOutputVisFlag = ast.literal_eval(
    '{{mergeOutputVisFlag#PROD-3: Merge visibility flag dictionary ({"step":"Y|N"})#{} }}'
)
try:
    mergeVisFlagSpecial = "{{mergeOutputVisFlagSpecial"
    mergeVisFlagSpecial += "#PROD-3: Special Visibility flag of output files"
    mergeVisFlagSpecial += '(a dictionary {"step n":{"FType":flag}} )#}}'
    mergeOutputVisFlagSpecial = ast.literal_eval(mergeVisFlagSpecial)
except SyntaxError:
    mergeOutputVisFlagSpecial = {}

pr.configVersion = "{{mcConfigVersion}}"
pr.eventType = "{{eventType}}"
# Often MC requests are defined with many subrequests but we want to retain
# the parent ID for viewing on the production monitoring page. If a parent
# request is defined then this is used.
pr.parentRequestID = "{{_parent}}"
pr.requestID = "{{ID}}"

if extraOptions:
    pr.extraOptions = ast.literal_eval(extraOptions)
pr.prodGroup = "{{pDsc}}"
pr.dataTakingConditions = "{{simDesc}}"

MCPriority = int(MCPriority)
selectionPriority = int(selectionPriority)
mergingPriority = int(mergingPriority)

removeInputMerge = ast.literal_eval(removeInputMerge)
removeInputSelection = ast.literal_eval(removeInputSelection)

MCNumberOfProcessors = tuple(int(x) for x in MCNumberOfProcessors.replace(" ", "").split(","))
selNumberOfProcessors = tuple(int(x) for x in selNumberOfProcessors.replace(" ", "").split(","))
mergeNumberOfProcessors = tuple(int(x) for x in mergeNumberOfProcessors.replace(" ", "").split(","))

###########################################
# LHCb conventions implied by the above
###########################################

localTestFlag = ast.literal_eval(localTestFlag)
validationFlag = ast.literal_eval(validationFlag)

if localTestFlag:
    pr.testFlag = True
    pr.publishFlag = False
    pr.prodsToLaunch = [1]

pr.outConfigName = pr.configName

w1 = ast.literal_eval(w1)
w2 = ast.literal_eval(w2)
w3 = ast.literal_eval(w3)

if not w1 and not w2 and not w3:
    gLogger.error("Vladimir, I told you to select at least one workflow!")
    DIRACexit(2)

elif w1:
    pr.prodsTypeList = [MCSimulationType]
    pr.outputSEs = ["Tier1_MC-DST"]

    pr.stepsInProds = [list(range(1, len(pr.stepsList) + 1))]
    pr.removeInputsFlags = [False]
    pr.priorities = [MCPriority]
    pr.cpus = [100000]
    pr.outputFileSteps = [str(len(pr.stepsList))]
    pr.targets = [targets]
    pr.events = [eventsPerJob]
    pr.groupSizes = [1]
    pr.plugins = [""]
    pr.inputDataPolicies = [""]
    pr.bkQueries = [""]
    pr.multicore = [MCmulticoreFlag]
    pr.processors = [MCNumberOfProcessors]

    simulationOutputVisFlag = fillVisList(simulationOutputVisFlag, len(pr.stepsInProds[0]))
    pr.compressionLvl = modifyCompression(
        simulationOutputVisFlag, simulationOutputVisFlagSpecial, simulationCompressionLvl
    )

    pr.outputVisFlag = [simulationOutputVisFlag]
    pr.specialOutputVisFlag = [simulationOutputVisFlagSpecial]

    # pr.resolveSteps()

elif w2:
    pr.prodsTypeList = [MCSimulationType, "MCReconstruction"]
    pr.outputSEs = ["Tier1-Buffer", "Tier1_MC-DST"]

    pr.stepsInProds = [
        [
            1,
        ],
        list(range(2, len(pr.stepsList) + 1)),
    ]
    pr.outputFileSteps = [str(len(pr.stepsInProds[0])), str(len(pr.stepsInProds[1]))]

    pr.removeInputsFlags = [False, removeInputSelection]
    pr.priorities = [MCPriority, selectionPriority]
    pr.cpus = [100000, selectionCPU]
    pr.targets = [targets, ""]
    pr.events = [eventsPerJob, -1]
    pr.groupSizes = [1, selectionGroupSize]
    pr.plugins = ["", selectionPlugin]
    pr.inputDataPolicies = ["", "download"]
    pr.bkQueries = ["", "fromPreviousProd"]
    pr.multicore = [MCmulticoreFlag, selmulticoreFlag]
    pr.processors = [MCNumberOfProcessors, selNumberOfProcessors]

    pr.compressionLvl = [simulationCompressionLvl] * len(pr.stepsInProds[0]) + [selectionCompressionLvl] * len(
        pr.stepsInProds[1]
    )

    simulationOutputVisFlag = fillVisList(simulationOutputVisFlag, len(pr.stepsInProds[0]))
    selectionOutputVisFlag = fillVisList(selectionOutputVisFlag, len(pr.stepsInProds[1]))

    pr.compressionLvl = modifyCompression(
        simulationOutputVisFlag, simulationOutputVisFlagSpecial, simulationCompressionLvl
    )
    pr.compressionLvl += modifyCompression(
        selectionOutputVisFlag, selectionOutputVisFlagSpecial, selectionCompressionLvl
    )

    pr.outputVisFlag = [simulationOutputVisFlag, selectionOutputVisFlag]
    pr.specialOutputVisFlag = [simulationOutputVisFlagSpecial, selectionOutputVisFlagSpecial]

    # pr.resolveSteps()

elif w3:
    pr.prodsTypeList = [MCSimulationType, "MCReconstruction", "MCMerge"]
    pr.outputSEs = ["Tier1-Buffer", "Tier1-Buffer", "Tier1_MC-DST"]

    pr.stepsInProds = [
        [
            1,
        ],
        list(range(2, len(pr.stepsList))),
        [len(pr.stepsList)],
    ]
    pr.outputFileSteps = ["1", str(len(pr.stepsInProds[1])), "1"]

    pr.removeInputsFlags = [False, removeInputSelection, removeInputMerge]
    pr.priorities = [MCPriority, selectionPriority, mergingPriority]
    pr.cpus = [100000, selectionCPU, mergingCPU]
    pr.targets = [targets, "", ""]
    pr.events = [eventsPerJob, -1, -1]
    pr.groupSizes = [1, selectionGroupSize, mergingGroupSize]
    pr.plugins = ["", selectionPlugin, mergingPlugin]
    pr.inputDataPolicies = ["", "download", "download"]
    pr.bkQueries = ["", "fromPreviousProd", "fromPreviousProd"]
    pr.multicore = [MCmulticoreFlag, selmulticoreFlag, mergemulticoreFlag]
    pr.processors = [MCNumberOfProcessors, selNumberOfProcessors, mergeNumberOfProcessors]

    simulationOutputVisFlag = fillVisList(simulationOutputVisFlag, len(pr.stepsInProds[0]))
    selectionOutputVisFlag = fillVisList(selectionOutputVisFlag, len(pr.stepsInProds[1]))
    mergeOutputVisFlag = fillVisList(mergeOutputVisFlag, len(pr.stepsInProds[2]))

    pr.compressionLvl = modifyCompression(
        simulationOutputVisFlag, simulationOutputVisFlagSpecial, simulationCompressionLvl
    )
    pr.compressionLvl += modifyCompression(
        selectionOutputVisFlag, selectionOutputVisFlagSpecial, selectionCompressionLvl
    )
    pr.compressionLvl += modifyCompression(mergeOutputVisFlag, mergeOutputVisFlagSpecial, mergeCompressionLvl)

    pr.outputVisFlag = [simulationOutputVisFlag, selectionOutputVisFlag, mergeOutputVisFlag]
    pr.specialOutputVisFlag = [simulationOutputVisFlagSpecial, selectionOutputVisFlagSpecial, mergeOutputVisFlagSpecial]

# In case we want just to test, we publish in the certification/test part of the BKK
if currentSetup == "LHCb-Certification" or pr.testFlag:
    pr.outConfigName = "certification"
    pr.configVersion = "test"

if pr.testFlag:
    pr.extend = "10"
    mergingGroupSize = "1"
    MCCpu = "50000"
    pr.previousProdID = 0  # set this for, e.g., launching only merging

# Validation implies few things, like saving all the outputs, and adding a GAUSSHIST
if validationFlag:
    pr.resolveSteps()
    pr.outConfigName = "validation"
    # Adding GAUSSHIST to the list of outputs to be produced (by the first step, which is Gauss)
    if "GAUSSHIST" not in pr.stepsListDict[0]["fileTypesOut"]:
        pr.stepsListDict[0]["fileTypesOut"].append("GAUSSHIST")
    pr.outputFileSteps = [""] * len(pr.prodsTypeList)


res = pr.buildAndLaunchRequest()
if not res["OK"]:
    gLogger.error("Errors with submission: %s" % res["Message"])
    DIRACexit(2)
else:
    gLogger.always("Submitted %s" % str(res["Value"]))
