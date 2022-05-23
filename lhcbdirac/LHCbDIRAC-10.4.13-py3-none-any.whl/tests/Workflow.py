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
import os

import DIRAC
from DIRAC.tests.Utilities.utils import find_all

from LHCbDIRAC.Interfaces.API.LHCbJob import LHCbJob


def createJob(local=True, workspace=os.path.dirname(DIRAC.__file__)):
    gaudirunJob = LHCbJob()
    gaudirunJob.setName("gaudirun-Gauss-test-wrong-config-will-fail")

    workspace = os.environ.get("WORKSPACE", workspace)
    inputSandbox = [
        find_all("prodConf_Gauss_00012345_00067890_1.py", workspace, "/tests/System/GridTestSubmission")[0],
        find_all("wrongConfig.cfg", workspace, "/tests/System/GridTestSubmission")[0],
    ]
    if not local:
        pilot_cfg = find_all("pilot.cfg", workspace + "/PilotInstallDIR")
        if not pilot_cfg:
            pilot_cfg = find_all("pilot.cfg", workspace)[0]
        inputSandbox += [pilot_cfg]
    gaudirunJob.setInputSandbox(inputSandbox)

    gaudirunJob.setOutputSandbox("00012345_00067890_1.sim")

    optGauss = "$APPCONFIGOPTS/Gauss/Sim08-Beam3500GeV-md100-2011-nu2.py;"
    optDec = "$DECFILESROOT/options/34112104.py;"
    optPythia = "$LBPYTHIAROOT/options/Pythia.py;"
    optOpts = "$APPCONFIGOPTS/Gauss/G4PL_FTFP_BERT_EmNoCuts.py;"
    optCompr = "$APPCONFIGOPTS/Persistency/Compression-ZLIB-1.py;"
    optPConf = "prodConf_Gauss_00012345_00067890_1.py"
    options = optGauss + optDec + optPythia + optOpts + optCompr + optPConf

    gaudirunJob.setApplication(
        "Gauss",
        "v45r5",
        options,
        extraPackages="AppConfig.v3r171;Gen/DecFiles.v27r14p1;ProdConf.v1r9",
        systemConfig="x86_64-slc5-gcc43-opt",
        modulesNameList=[
            "CreateDataFile",
            "GaudiApplication",
            "FileUsage",
            "UploadOutputData",
            "UploadLogFile",
            "FailoverRequest",
            "UserJobFinalization",
        ],
        parametersList=[
            ("applicationName", "string", "", "Application Name"),
            ("applicationVersion", "string", "", "Application Version"),
            ("applicationLog", "string", "", "Name of the output file of the application"),
            ("optionsFile", "string", "", "Options File"),
            ("extraOptionsLine", "string", "", "This is appended to standard options"),
            ("inputDataType", "string", "", "Input Data Type"),
            ("inputData", "string", "", "Input Data"),
            ("numberOfEvents", "string", "", "Events treated"),
            ("multiCore", "string", "", "If the step can run multicore"),
            ("StopSigNumber", "string", "", "signal number (interpreted by Gaudi)"),
            ("StopSigRegex", "string", "", "RegEx of what to stop"),
            ("extraPackages", "string", "", "ExtraPackages"),
            ("listoutput", "list", [], "StepOutputList"),
            ("SystemConfig", "string", "", "binary tag"),
        ],
    )

    gaudirunJob._addParameter(gaudirunJob.workflow, "PRODUCTION_ID", "string", "00012345", "ProductionID")
    gaudirunJob._addParameter(gaudirunJob.workflow, "JOB_ID", "string", "00067890", "JobID")
    gaudirunJob._addParameter(gaudirunJob.workflow, "configName", "string", "testCfg", "ConfigName")
    gaudirunJob._addParameter(gaudirunJob.workflow, "configVersion", "string", "testVer", "ConfigVersion")
    outputList = [
        {
            "stepName": "GaussStep1",
            "outputDataType": "sim",
            "outputBKType": "SIM",
            "outputDataSE": "Tier1_MC-DST",
            "outputDataName": "00012345_00067890_1.sim",
        }
    ]
    gaudirunJob._addParameter(gaudirunJob.workflow, "outputList", "list", outputList, "outputList")
    gaudirunJob._addParameter(gaudirunJob.workflow, "outputDataFileMask", "string", "", "outputFM")
    gaudirunJob._addParameter(gaudirunJob.workflow, "outputMode", "string", "Local", "OM")
    gaudirunJob._addParameter(gaudirunJob.workflow, "LogLevel", "string", "DEBUG", "LL")
    outputFilesDict = [
        {"outputDataName": "00012345_00067890_1.sim", "outputDataSE": "Tier1_MC-DST", "outputDataType": "SIM"}
    ]
    gaudirunJob._addParameter(
        gaudirunJob.workflow.step_instances[0], "listoutput", "list", outputFilesDict, "listoutput"
    )

    gaudirunJob.setLogLevel("DEBUG")
    gaudirunJob.setDIRACPlatform()
    if local:
        gaudirunJob.setConfigArgs("pilot.cfg wrongConfig.cfg")
    else:
        gaudirunJob.setConfigArgs("wrongConfig.cfg")

    gaudirunJob.setCPUTime(172800)

    return gaudirunJob
