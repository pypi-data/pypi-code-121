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
"""just some common components for tests."""
from mock import MagicMock

from DIRAC.RequestManagementSystem.Client.Request import Request
from DIRAC.RequestManagementSystem.Client.Operation import Operation
from DIRAC.RequestManagementSystem.Client.File import File

version = "someVers"
prod_id = "123"
prod_job_id = "00000456"
wms_job_id = 12345
workflowStatus = {"OK": True}
stepStatus = {"OK": True}
step_number = "321"
step_id = "%s_%s_%s" % (prod_id, prod_job_id, step_number)

ar_mock = MagicMock()
ar_mock.commit.return_value = {"OK": True, "Value": ""}

jr_mock = MagicMock()
jr_mock.setApplicationStatus.return_value = {"OK": True, "Value": ""}
jr_mock.generateForwardDISET.return_value = {"OK": True, "Value": Operation()}
jr_mock.setJobParameter.return_value = {"OK": True, "Value": "pippo"}

fr_mock = MagicMock()
fr_mock.getFiles.return_value = {}
fr_mock.setFileStatus.return_value = {"OK": True, "Value": ""}
fr_mock.commit.return_value = {"OK": True, "Value": ""}
fr_mock.generateForwardDISET.return_value = {"OK": True, "Value": Operation()}

rc_mock = Request()
rc_mock.RequestName = "aRequestName"
rc_mock.OwnerDN = "pippo"
rc_mock.OwnerGroup = "pippoGRP"
rOp = Operation()
rOp.Type = "PutAndRegister"
rOp.TargetSE = "anSE"
f = File()
f.LFN = "/foo/bar.py"
f.PFN = "/foo/bar.py"
rOp.addFile(f)
rc_mock.addOperation(rOp)


wf_commons = [
    {
        "PRODUCTION_ID": prod_id,
        "JOB_ID": prod_job_id,
        "eventType": "123456789",
        "jobType": "merge",
        "configName": "aConfigName",
        "configVersion": "aConfigVersion",
        "outputDataFileMask": "",
        "BookkeepingLFNs": "aa",
        "ProductionOutputData": "ProductionOutputData",
        "numberOfEvents": "100",
        "JobReport": jr_mock,
        "Request": rc_mock,
        "AccountingReport": ar_mock,
        "FileReport": fr_mock,
        "SystemConfig": "sys_config",
        "runNumber": "Unknown",
        "gaudiSteps": ["someApp_1"],
        "outputSEs": {"DAVINCIHIST": "CERN-HIST", "TXT": "SE1"},
    },
    {
        "PRODUCTION_ID": prod_id,
        "JOB_ID": prod_job_id,
        "configName": "aConfigName",
        "configVersion": "aConfigVersion",
        "outputDataFileMask": "",
        "jobType": "merge",
        "BookkeepingLFNs": "aa",
        "ProductionOutputData": "ProductionOutputData",
        "numberOfEvents": "100",
        "JobReport": jr_mock,
        "Request": rc_mock,
        "AccountingReport": ar_mock,
        "FileReport": fr_mock,
        "SystemConfig": "sys_config",
        "LogFilePath": "someDir",
        "runNumber": "Unknown",
        "gaudiSteps": ["someApp_1"],
        "outputSEs": {"DAVINCIHIST": "CERN-HIST", "TXT": "SE1"},
    },
    {
        "PRODUCTION_ID": prod_id,
        "JOB_ID": prod_job_id,
        "configName": "aConfigName",
        "configVersion": "aConfigVersion",
        "outputDataFileMask": "",
        "jobType": "merge",
        "BookkeepingLFNs": "aa",
        "ProductionOutputData": "ProductionOutputData",
        "numberOfEvents": "100",
        "JobReport": jr_mock,
        "Request": rc_mock,
        "AccountingReport": ar_mock,
        "FileReport": fr_mock,
        "SystemConfig": "sys_config",
        "LogFilePath": "someDir",
        "LogTargetPath": "someOtherDir",
        "runNumber": "Unknown",
        "gaudiSteps": ["someApp_1"],
        "outputSEs": {"DAVINCIHIST": "CERN-HIST", "TXT": "SE1"},
    },
    {
        "PRODUCTION_ID": prod_id,
        "JOB_ID": prod_job_id,
        "configName": "aConfigName",
        "configVersion": "aConfigVersion",
        "outputDataFileMask": "",
        "jobType": "merge",
        "BookkeepingLFNs": "aa",
        "ProductionOutputData": "ProductionOutputData",
        "numberOfEvents": "100",
        "JobReport": jr_mock,
        "Request": rc_mock,
        "AccountingReport": ar_mock,
        "FileReport": fr_mock,
        "SystemConfig": "sys_config",
        "LogFilePath": "someDir",
        "LogTargetPath": "someOtherDir",
        "runNumber": "Unknown",
        "gaudiSteps": ["someApp_1"],
        "outputSEs": {"DAVINCIHIST": "CERN-HIST", "TXT": "SE1"},
    },
    {
        "PRODUCTION_ID": prod_id,
        "JOB_ID": prod_job_id,
        "configName": "aConfigName",
        "configVersion": "aConfigVersion",
        "outputDataFileMask": "",
        "jobType": "reco",
        "BookkeepingLFNs": "aa",
        "ProductionOutputData": "ProductionOutputData",
        "JobReport": jr_mock,
        "Request": rc_mock,
        "AccountingReport": ar_mock,
        "FileReport": fr_mock,
        "SystemConfig": "sys_config",
        "runNumber": "Unknown",
        "gaudiSteps": ["someApp_1"],
        "outputSEs": {"DAVINCIHIST": "CERN-HIST", "TXT": "SE1"},
    },
    {
        "PRODUCTION_ID": prod_id,
        "JOB_ID": prod_job_id,
        "configName": "aConfigName",
        "configVersion": "aConfigVersion",
        "outputDataFileMask": "",
        "jobType": "reco",
        "BookkeepingLFNs": "aa",
        "ProductionOutputData": "ProductionOutputData",
        "JobReport": jr_mock,
        "Request": rc_mock,
        "AccountingReport": ar_mock,
        "FileReport": fr_mock,
        "SystemConfig": "sys_config",
        "LogFilePath": "someDir",
        "runNumber": "Unknown",
        "gaudiSteps": ["someApp_1"],
        "outputSEs": {"DAVINCIHIST": "CERN-HIST", "TXT": "SE1"},
    },
    {
        "PRODUCTION_ID": prod_id,
        "JOB_ID": prod_job_id,
        "configName": "aConfigName",
        "configVersion": "aConfigVersion",
        "outputDataFileMask": "",
        "jobType": "reco",
        "BookkeepingLFNs": "aa",
        "ProductionOutputData": "ProductionOutputData",
        "JobReport": jr_mock,
        "Request": rc_mock,
        "AccountingReport": ar_mock,
        "FileReport": fr_mock,
        "SystemConfig": "sys_config",
        "LogFilePath": "someDir",
        "LogTargetPath": "someOtherDir",
        "runNumber": "Unknown",
        "gaudiSteps": ["someApp_1"],
        "outputSEs": {"DAVINCIHIST": "CERN-HIST", "TXT": "SE1"},
    },
    {
        "PRODUCTION_ID": prod_id,
        "JOB_ID": prod_job_id,
        "configName": "aConfigName",
        "configVersion": "aConfigVersion",
        "outputDataFileMask": "",
        "jobType": "reco",
        "BookkeepingLFNs": "aa",
        "ProductionOutputData": "ProductionOutputData",
        "JobReport": jr_mock,
        "Request": rc_mock,
        "AccountingReport": ar_mock,
        "FileReport": fr_mock,
        "SystemConfig": "sys_config",
        "LogFilePath": "someDir",
        "LogTargetPath": "someOtherDir",
        "runNumber": "Unknown",
        "gaudiSteps": ["someApp_1"],
        "outputSEs": {"DAVINCIHIST": "CERN-HIST", "TXT": "SE1"},
    },
    {
        "PRODUCTION_ID": prod_id,
        "JOB_ID": prod_job_id,
        "configName": "aConfigName",
        "configVersion": "aConfigVersion",
        "outputDataFileMask": "",
        "jobType": "reco",
        "BookkeepingLFNs": "aa",
        "ProductionOutputData": "ProductionOutputData",
        "JobReport": jr_mock,
        "Request": rc_mock,
        "AccountingReport": ar_mock,
        "FileReport": fr_mock,
        "SystemConfig": "sys_config",
        "LogFilePath": "someDir",
        "LogTargetPath": "someOtherDir",
        "runNumber": "Unknown",
        "InputData": "",
        "gaudiSteps": ["someApp_1"],
        "outputSEs": {"DAVINCIHIST": "CERN-HIST", "TXT": "SE1"},
    },
    {
        "PRODUCTION_ID": prod_id,
        "JOB_ID": prod_job_id,
        "configName": "aConfigName",
        "configVersion": "aConfigVersion",
        "outputDataFileMask": "",
        "jobType": "reco",
        "BookkeepingLFNs": "aa",
        "ProductionOutputData": "ProductionOutputData",
        "JobReport": jr_mock,
        "Request": rc_mock,
        "AccountingReport": ar_mock,
        "FileReport": fr_mock,
        "SystemConfig": "sys_config",
        "LogFilePath": "someDir",
        "LogTargetPath": "someOtherDir",
        "runNumber": "Unknown",
        "InputData": "foo;bar",
        "gaudiSteps": ["someApp_1"],
        "outputSEs": {"DAVINCIHIST": "CERN-HIST", "TXT": "SE1"},
    },
    {
        "PRODUCTION_ID": prod_id,
        "JOB_ID": prod_job_id,
        "configName": "aConfigName",
        "configVersion": "aConfigVersion",
        "outputDataFileMask": "",
        "jobType": "reco",
        "BookkeepingLFNs": "aa",
        "ProductionOutputData": "ProductionOutputData",
        "JobReport": jr_mock,
        "Request": rc_mock,
        "AccountingReport": ar_mock,
        "FileReport": fr_mock,
        "SystemConfig": "sys_config",
        "LogFilePath": "someDir",
        "LogTargetPath": "someOtherDir",
        "runNumber": "Unknown",
        "InputData": "foo;bar",
        "ParametricInputData": "",
        "gaudiSteps": ["someApp_1"],
        "outputSEs": {"DAVINCIHIST": "CERN-HIST", "TXT": "SE1"},
    },
    {
        "PRODUCTION_ID": prod_id,
        "JOB_ID": prod_job_id,
        "configName": "aConfigName",
        "configVersion": "aConfigVersion",
        "outputDataFileMask": "",
        "jobType": "reco",
        "BookkeepingLFNs": "aa",
        "ProductionOutputData": "ProductionOutputData",
        "JobReport": jr_mock,
        "Request": rc_mock,
        "AccountingReport": ar_mock,
        "FileReport": fr_mock,
        "SystemConfig": "sys_config",
        "LogFilePath": "someDir",
        "LogTargetPath": "someOtherDir",
        "runNumber": "Unknown",
        "InputData": "foo;bar",
        "ParametricInputData": "pid1;pid2;pid3",
        "gaudiSteps": ["someApp_1"],
        "outputSEs": {"DAVINCIHIST": "CERN-HIST", "TXT": "SE1"},
    },
]

step_commons = [
    {
        "applicationName": "someApp",
        "applicationVersion": "v1r0",
        "eventType": "123456789",
        "SystemConfig": "sys_config",
        "applicationLog": "appLog",
        "extraPackages": "",
        "XMLSummary": "XMLSummaryFile",
        "numberOfEvents": "100",
        "BKStepID": "123",
        "StepProcPass": "Sim123",
        "outputFilePrefix": "pref_",
        "STEP_INSTANCE_NAME": "someApp_1",
        "inputData": "/for/bar/",
        "listoutput": [{"outputDataName": prod_id + "_" + prod_job_id + "_", "outputDataType": "bbb"}],
    },
    {
        "applicationName": "someApp",
        "applicationVersion": "v1r0",
        "eventType": "123456789",
        "SystemConfig": "sys_config",
        "applicationLog": "appLog",
        "extraPackages": "",
        "XMLSummary": "XMLSummaryFile",
        "numberOfEvents": "100",
        "BKStepID": "123",
        "StepProcPass": "Sim123",
        "outputFilePrefix": "pref_",
        "optionsLine": "",
        "inputData": "/for/bar/",
        "STEP_INSTANCE_NAME": "someApp_1",
        "listoutput": [{"outputDataName": prod_id + "_" + prod_job_id + "_", "outputDataType": "bbb"}],
    },
    {
        "applicationName": "someApp",
        "applicationVersion": "v1r0",
        "eventType": "123456789",
        "SystemConfig": "sys_config",
        "applicationLog": "appLog",
        "extraPackages": "",
        "XMLSummary": "XMLSummaryFile",
        "numberOfEvents": "100",
        "BKStepID": "123",
        "StepProcPass": "Sim123",
        "outputFilePrefix": "pref_",
        "extraOptionsLine": "blaBla",
        "inputData": "/for/bar/",
        "STEP_INSTANCE_NAME": "someApp_1",
        "listoutput": [{"outputDataName": prod_id + "_" + prod_job_id + "_", "outputDataType": "bbb"}],
    },
]
