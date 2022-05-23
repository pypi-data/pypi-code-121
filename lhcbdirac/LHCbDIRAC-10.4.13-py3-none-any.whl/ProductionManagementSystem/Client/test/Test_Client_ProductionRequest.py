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
"""Test of the ProductionRequest and Production modules."""
# pylint: disable=line-too-long,invalid-name,protected-access,missing-docstring

import unittest
from mock import Mock, MagicMock

from LHCbDIRAC.BookkeepingSystem.Client.test.mock_BookkeepingClient import (
    BookkeepingClientFake,
    stepMC,
    stepMC2,
    stepStripp,
    mergeStep,
    mergeStepBHADRON,
    step1Dict,
    step2Dict,
    step124620Dict,
    step124621Dict,
    step125080,
    stepHistoMergingDict,
    mergeStepCALIBRA,
    mergeStepPIDMDST,
)
from LHCbDIRAC.ProductionManagementSystem.Client.ProductionRequest import ProductionRequest, _splitIntoProductionSteps
from LHCbDIRAC.ProductionManagementSystem.Client.Production import Production

prodsDict = {
    1: {
        "productionType": "DataStripping",
        "stepsInProd": [123, 456],
        "bkQuery": "Full",
        "removeInputsFlag": False,
        "tracking": 0,
        "outputSE": {"T1": "SE1"},
        "priority": 5,
        "cpu": 1000000,
        "outputFileMask": "",
        "outputFileStep": "",
        "input": [],
        "target": "",
        "groupSize": 1,
        "plugin": "ByRun",
        "inputDataPolicy": "download",
        "derivedProduction": 0,
        "transformationFamily": 0,
        "previousProd": None,
        "stepsInProd-ProdName": ["123['SDST']", "456['BHADRON.DST']"],
        "events": -1,
        "multicore": "False",
        "processors": (4, 4),
        "outputMode": "Any",
        "ancestorDepth": 0,
    },
    2: {
        "productionType": "Merge",
        "stepsInProd": [456],
        "bkQuery": "fromPreviousProd",
        "removeInputsFlag": True,
        "tracking": 1,
        "outputSE": {"T1": "SE1"},
        "priority": 8,
        "cpu": 300000,
        "outputFileMask": "",
        "outputFileStep": "",
        "input": [],
        "target": "",
        "groupSize": 1,
        "plugin": "BySize",
        "inputDataPolicy": "download",
        "derivedProduction": 0,
        "transformationFamily": 0,
        "previousProd": 1,
        "stepsInProd-ProdName": ["456['CALIBRATION.DST']"],
        "events": -1,
        "multicore": "False",
        "processors": (2, 2),
        "outputMode": "Local",
        "ancestorDepth": 0,
    },
    3: {
        "productionType": "Merge",
        "stepsInProd": [456],
        "bkQuery": "fromPreviousProd",
        "removeInputsFlag": True,
        "tracking": 1,
        "outputSE": {"T1": "SE1"},
        "priority": 9,
        "cpu": 10000,
        "outputFileMask": "",
        "outputFileStep": "",
        "input": [],
        "target": "",
        "groupSize": 2,
        "plugin": "BySize",
        "inputDataPolicy": "download",
        "derivedProduction": 0,
        "transformationFamily": 0,
        "previousProd": 1,
        "stepsInProd-ProdName": ["456['PID.MDST']"],
        "events": -1,
        "multicore": "True",
        "processors": (0, 2),
        "outputMode": "Any",
        "ancestorDepth": 0,
    },
    4: {
        "productionType": "Merge",
        "stepsInProd": [789],
        "bkQuery": "fromPreviousProd",
        "removeInputsFlag": True,
        "tracking": 1,
        "outputSE": {"T1": "SE1"},
        "priority": 9,
        "cpu": 1000,
        "outputFileMask": "",
        "outputFileStep": "",
        "input": [],
        "target": "",
        "groupSize": 3,
        "plugin": "BySize",
        "inputDataPolicy": "download",
        "derivedProduction": 0,
        "transformationFamily": 0,
        "previousProd": 1,
        "stepsInProd-ProdName": ["789['DAVINCIHIST', 'BRUNELHIST']"],
        "events": -1,
        "multicore": "True",
        "processors": (0, 0),
        "outputMode": "Any",
        "ancestorDepth": 0,
    },
}


class ClientTestCase(unittest.TestCase):
    """Base class for the Client test cases."""

    def setUp(self):

        self.bkClientMock = Mock()
        self.diracProdIn = Mock()
        self.diracProdIn.launchProduction.return_value = {"OK": True, "Value": 321}

        self.bkClientFake = BookkeepingClientFake()

        self.maxDiff = None


class ProductionRequestSuccess(ClientTestCase):
    def test__mcSpecialCase(self):

        # prepare the test case
        prod = Production()
        prod.setParameter("ProcessingType", "JDL", "Test", "ProductionGroupOrType")
        prod.addApplicationStep(stepDict=stepMC, modulesList=["GaudiApplication"])
        prod.addApplicationStep(stepDict=stepMC2, inputData="previousStep", modulesList=["GaudiApplication"])
        prod.priority = "1"
        prod.addFinalizationStep()
        prod.setFileMask("", "4")
        for par in prod.LHCbJob.workflow.parameters:
            if par.getName() == "Site":
                self.assertEqual(par.value, "ANY")
            if par.getName() == "outputDataFileMask":
                self.assertEqual(par.value, "")

        pr = ProductionRequest(self.bkClientFake, self.diracProdIn)
        pr.tc = MagicMock()
        pr.opsH = MagicMock()
        pr.opsH.getValue.return_value = "testValue"
        prod.LHCbJob._siteSet = {"testValue"}

        pr._modifyAndLaunchMCXML(prod, {"tracking": 0})
        for par in prod.LHCbJob.workflow.parameters:
            if par.getName() == "Site":
                self.assertEqual(par.value, "testValue")
            if par.getName() == "numberOfEvents":
                self.assertEqual(par.value, "testValue")
            if par.getName() == "listoutput":
                self.assertTrue("gausshist" in dict(par.value).values())
            if par.getName() == "outputDataStep":
                self.assertEqual(par.value, "1;4")
            if par.getName() == "outputDataFileMask":
                self.assertEqual(par.value, "GAUSSHIST;DST")

        # # re-prepare the test case
        prod = Production()
        prod.setParameter("ProcessingType", "JDL", "Test", "ProductionGroupOrType")
        prod.addApplicationStep(stepDict=step1Dict, inputData="previousStep", modulesList=["GaudiApplication"])
        prod.addFinalizationStep()
        prod.setFileMask("", ["4"])

        pr = ProductionRequest(self.bkClientFake, self.diracProdIn)
        pr.tc = MagicMock()
        pr.opsH = MagicMock()
        pr.opsH.getValue.return_value = "testValue"
        prod.LHCbJob._siteSet = {"testValue"}

        # # re-run
        pr._mcSpecialCase(prod, {"tracking": 0})
        for par in prod.LHCbJob.workflow.parameters:
            if par.getName() == "Site":
                self.assertEqual(par.value, "ANY")
            if par.getName() == "listoutput":
                self.assertTrue("gausshist" not in dict(par.value).values())
            if par.getName() == "outputDataStep":
                self.assertEqual(par.value, "4")
            if par.getName() == "outputDataFileMask":
                self.assertEqual(par.value, "")
            if par.getName() == "Priority":
                self.assertEqual(par.value, "1")

        # And again re-prepare the test case
        prod = Production()
        prod.setParameter("ProcessingType", "JDL", "Test", "ProductionGroupOrType")
        prod.addApplicationStep(stepDict=step1Dict, inputData="previousStep", modulesList=["GaudiApplication"])
        prod.addFinalizationStep()
        prod.setFileMask("")

        pr = ProductionRequest(self.bkClientFake, self.diracProdIn)
        pr.tc = MagicMock()
        pr.opsH = MagicMock()
        pr.opsH.getValue.return_value = "testValue"
        prod.LHCbJob._siteSet = {"testValue"}

        pr._mcSpecialCase(prod, {"tracking": 0})
        for par in prod.LHCbJob.workflow.parameters:
            if par.getName() == "Site":
                self.assertEqual(par.value, "ANY")
            if par.getName() == "listoutput":
                self.assertTrue("gausshist" not in dict(par.value).values())
            if par.getName() == "outputDataFileMask":
                self.assertEqual(par.value, "")
            if par.getName() == "Priority":
                self.assertEqual(par.value, "1")

    def test_resolveStepsSuccess(self):

        pr = ProductionRequest(self.bkClientFake, self.diracProdIn)
        pr.stepsList = ["123"]
        pr.outputVisFlag = [{"1": "N"}]
        pr.compressionLvl = ["LOW"]
        pr.resolveSteps()
        expected = dict(step1Dict)
        expected["OptionFiles"] = "optsFiles;$APPCONFIGOPTS/Persistency/Compression-ZLIB-1.py"
        self.assertEqual(pr.stepsListDict, [expected])

        pr = ProductionRequest(self.bkClientFake, self.diracProdIn)
        pr.stepsList = ["125080"]  # this one already has a compression level
        pr.outputVisFlag = [{"1": "N"}]
        pr.resolveSteps()
        expected = dict(step125080)
        expectedOptionFiles = "$APPCONFIGOPTS/Gauss/Sim08-Beam4000GeV-mu100-2012-nu2.5.py;"
        expectedOptionFiles += "$DECFILESROOT/options/11102400.py;$LBPYTHIA8ROOT/options/Pythia8.py;"
        expectedOptionFiles += "$APPCONFIGOPTS/Gauss/G4PL_FTFP_BERT_EmNoCuts.py;"
        expected["OptionFiles"] = expectedOptionFiles
        self.assertEqual(pr.stepsListDict, [expected])

        pr = ProductionRequest(self.bkClientFake, self.diracProdIn)
        pr.stepsList = ["125080"]  # this one already has a compression level
        pr.compressionLvl = ["LOW"]
        pr.outputVisFlag = [{"1": "N"}]
        pr.resolveSteps()
        expected = dict(step125080)
        self.assertEqual(pr.stepsListDict, [expected])

        pr = ProductionRequest(self.bkClientFake, self.diracProdIn)
        pr.stepsList = ["125080"]  # this one already has a compression level
        pr.compressionLvl = ["HIGH"]  # this will replace it
        pr.outputVisFlag = [{"1": "N"}]
        pr.resolveSteps()
        expected = dict(step125080)
        expectedOptionFiles = "$APPCONFIGOPTS/Gauss/Sim08-Beam4000GeV-mu100-2012-nu2.5.py;"
        expectedOptionFiles += "$DECFILESROOT/options/11102400.py;"
        expectedOptionFiles += "$LBPYTHIA8ROOT/options/Pythia8.py;"
        expectedOptionFiles += "$APPCONFIGOPTS/Gauss/G4PL_FTFP_BERT_EmNoCuts.py;"
        expected["OptionFiles"] = expectedOptionFiles
        self.assertEqual(pr.stepsListDict, [expected])

        pr = ProductionRequest(self.bkClientFake, self.diracProdIn)
        pr.stepsList = ["123", "456"]
        pr.compressionLvl = ["LOW", "HIGH"]
        pr.outputVisFlag = [{"1": "N"}, {"2": "N"}]
        expected1 = dict(step1Dict)
        expected1["OptionFiles"] = "optsFiles;$APPCONFIGOPTS/Persistency/Compression-ZLIB-1.py"
        expected2 = dict(step2Dict)
        expected2["OptionFiles"] = "optsFiles;$APPCONFIGOPTS/Persistency/Compression-LZMA-4.py"
        pr.resolveSteps()
        self.assertEqual(pr.stepsListDict, [expected1, expected2])

        pr = ProductionRequest(self.bkClientFake, self.diracProdIn)
        pr.stepsList = ["123", "456", "789"]
        pr.compressionLvl = ["LOW", "HIGH", "HIGH"]
        pr.outputVisFlag = [{"1": "N"}, {"2": "N"}, {"3": "Y"}]
        expected1 = dict(step1Dict)
        expected1["OptionFiles"] = "optsFiles;$APPCONFIGOPTS/Persistency/Compression-ZLIB-1.py"
        expected2 = dict(step2Dict)
        expected2["OptionFiles"] = "optsFiles;$APPCONFIGOPTS/Persistency/Compression-LZMA-4.py"
        expected3 = dict(stepHistoMergingDict)
        expected3["OptionFiles"] = "optsFiles;$APPCONFIGOPTS/Persistency/Compression-LZMA-4.py"
        pr.resolveSteps()
        self.assertEqual(pr.stepsListDict, [expected1, expected2, expected3])

        pr = ProductionRequest(self.bkClientFake, self.diracProdIn)
        pr.stepsList = ["124620", "124621"]
        pr.compressionLvl = ["LOW", "HIGH"]
        pr.outputVisFlag = [{"1": "N"}, {"2": "Y"}]
        expected1 = dict(step124620Dict)
        expected1["OptionFiles"] = "$APPCONFIGOPTS/Boole/Default.py;$APPCONFIGOPTS/Boole/DataType-2012.py;"
        expected2 = dict(step124621Dict)
        expected2["OptionFiles"] = "someBrunelOptions"
        pr.resolveSteps()
        self.assertEqual(pr.stepsListDict, [expected1, expected2])

        pr = ProductionRequest(self.bkClientFake, self.diracProdIn)
        pr.stepsList = ["123", "456", "", ""]
        pr.outputVisFlag = [{"1": "N"}, {"2": "N"}]
        pr.compressionLvl = ["LOW", "LOW", "HIGH", "HIGH"]
        pr.resolveSteps()
        self.assertEqual(
            pr.stepsListDict,
            [
                {
                    "StepId": 123,
                    "StepName": "Stripping14-Stripping",
                    "ApplicationName": "DaVinci",
                    "ApplicationVersion": "v2r2",
                    "ExtraOptions": "",
                    "OptionFiles": "optsFiles;$APPCONFIGOPTS/Persistency/Compression-ZLIB-1.py",
                    "Visible": "Yes",
                    "ExtraPackages": "eps",
                    "ProcessingPass": "procPass",
                    "OptionsFormat": "",
                    "SystemConfig": "",
                    "DDDB": "",
                    "CONDDB": "123456",
                    "DQTag": "",
                    "isMulticore": "N",
                    "prodStepID": "123['SDST']",
                    "mcTCK": "",
                    "visibilityFlag": [
                        {"Visible": "N", "FileType": "BHADRON.DST"},
                        {"Visible": "N", "FileType": "CALIBRATION.DST"},
                    ],
                    "fileTypesIn": ["SDST"],
                    "fileTypesOut": ["BHADRON.DST", "CALIBRATION.DST"],
                },
                {
                    "StepId": 456,
                    "StepName": "Merge",
                    "ApplicationName": "LHCb",
                    "ApplicationVersion": "v1r2",
                    "ExtraOptions": "",
                    "OptionFiles": "optsFiles;$APPCONFIGOPTS/Persistency/Compression-ZLIB-1.py",
                    "Visible": "Yes",
                    "ExtraPackages": "eps",
                    "ProcessingPass": "procPass",
                    "OptionsFormat": "",
                    "SystemConfig": "x86_64-slc6-gcc49-opt",
                    "prodStepID": "456['BHADRON.DST', 'CALIBRATION.DST']",
                    "DDDB": "",
                    "CONDDB": "123456",
                    "DQTag": "",
                    "isMulticore": "N",
                    "mcTCK": "",
                    "visibilityFlag": [
                        {"Visible": "N", "FileType": "BHADRON.DST"},
                        {"Visible": "N", "FileType": "CALIBRATION.DST"},
                    ],
                    "fileTypesIn": ["BHADRON.DST", "CALIBRATION.DST"],
                    "fileTypesOut": ["BHADRON.DST", "CALIBRATION.DST"],
                },
            ],
        )

        pr = ProductionRequest(self.bkClientFake, self.diracProdIn)
        pr.stepsList = ["123"]
        pr.outputVisFlag = [{"1": "N"}]
        pr.resolveSteps()
        self.assertEqual(
            pr.stepsListDict,
            [
                {
                    "StepId": 123,
                    "StepName": "Stripping14-Stripping",
                    "ApplicationName": "DaVinci",
                    "ApplicationVersion": "v2r2",
                    "ExtraOptions": "",
                    "OptionFiles": "optsFiles",
                    "Visible": "Yes",
                    "ExtraPackages": "eps",
                    "ProcessingPass": "procPass",
                    "OptionsFormat": "",
                    "SystemConfig": "",
                    "DDDB": "",
                    "CONDDB": "123456",
                    "DQTag": "",
                    "isMulticore": "N",
                    "prodStepID": "123['SDST']",
                    "mcTCK": "",
                    "visibilityFlag": [
                        {"Visible": "N", "FileType": "BHADRON.DST"},
                        {"Visible": "N", "FileType": "CALIBRATION.DST"},
                    ],
                    "fileTypesIn": ["SDST"],
                    "fileTypesOut": ["BHADRON.DST", "CALIBRATION.DST"],
                }
            ],
        )
        pr = ProductionRequest(self.bkClientFake, self.diracProdIn)
        pr.compressionLvl = ["HIGH"]
        pr.stepsList = ["123"]
        pr.outputVisFlag = [{"1": "N"}]
        pr.resolveSteps()
        self.assertEqual(
            pr.stepsListDict,
            [
                {
                    "StepId": 123,
                    "StepName": "Stripping14-Stripping",
                    "ApplicationName": "DaVinci",
                    "ApplicationVersion": "v2r2",
                    "ExtraOptions": "",
                    "ProcessingPass": "procPass",
                    "OptionsFormat": "",
                    "SystemConfig": "",
                    "OptionFiles": "optsFiles;$APPCONFIGOPTS/Persistency/Compression-LZMA-4.py",
                    "Visible": "Yes",
                    "ExtraPackages": "eps",
                    "prodStepID": "123['SDST']",
                    "mcTCK": "",
                    "visibilityFlag": [
                        {"Visible": "N", "FileType": "BHADRON.DST"},
                        {"Visible": "N", "FileType": "CALIBRATION.DST"},
                    ],
                    "DDDB": "",
                    "CONDDB": "123456",
                    "DQTag": "",
                    "isMulticore": "N",
                    "fileTypesIn": ["SDST"],
                    "fileTypesOut": ["BHADRON.DST", "CALIBRATION.DST"],
                }
            ],
        )

        pr = ProductionRequest(self.bkClientFake, self.diracProdIn)
        pr.compressionLvl = ["HIGH"]
        pr.outputVisFlag = [{"1": "Y"}]
        # pr.outputVisFlag = [{'Visibility':'N','FileType':'BHADRON.DST'},{'Visibility':'N','FileType':'CALIBRATION.DST'}]
        pr.stepsList = ["999"]
        pr.resolveSteps()
        self.assertEqual(
            pr.stepsListDict,
            [
                {
                    "StepId": 999,
                    "StepName": "Stripping28",
                    "ApplicationName": "DaVinci",
                    "ApplicationVersion": "v41r3",
                    "ExtraOptions": "",
                    # 'OptionFiles':'$APPCONFIGOPTS/Persistency/Compression-ZLIB-1.py;$APPCONFIGOPTS/Persistency/Compression-LZMA-4.py',
                    # 'OptionFiles':'$APPCONFIGOPTS/Persistency/Compression-LZMA-4.py',
                    "OptionFiles": "",
                    "Visible": "Yes",
                    "Usable": "Yes",
                    "ProcessingPass": "Stripping28",
                    "SystemConfig": "x86_64-slc5-gcc49-opt",
                    "ExtraPackages": "AppConfig.v3r306",
                    "mcTCK": "",
                    "prodStepID": "999['SDST']",
                    "DDDB": "dddb-20150724",
                    "CONDDB": "cond-20161011",
                    "DQTag": "",
                    "isMulticore": "N",
                    "fileTypesIn": ["SDST"],
                    "visibilityFlag": [
                        {"Visible": "Y", "FileType": "BHADRON.DST"},
                        {"Visible": "Y", "FileType": "CALIBRATION.DST"},
                    ],
                    "fileTypesOut": ["BHADRON.DST", "CALIBRATION.DST"],
                }
            ],
        )

        pr = ProductionRequest(self.bkClientFake, self.diracProdIn)
        pr.compressionLvl = ["HIGH"]
        pr.outputVisFlag = [{"1": "Y"}]
        pr.stepsList = ["998"]
        pr.resolveSteps()
        self.assertEqual(
            pr.stepsListDict,
            [
                {
                    "StepId": 998,
                    "StepName": "Stripping28",
                    "ApplicationName": "DaVinci",
                    "ApplicationVersion": "v41r3",
                    "ExtraOptions": "",
                    # 'OptionFiles':'$APPCONFIGOPTS/Persistency/Compression-ZLIB-1.py;$APPCONFIGOPTS/Persistency/Compression-LZMA-4.py',
                    "OptionFiles": "$APPCONFIGOPTS/Persistency/Compression-LZMA-4.py",
                    "Visible": "Yes",
                    "Usable": "Yes",
                    "ProcessingPass": "Stripping28",
                    "SystemConfig": "x86_64-slc6-gcc49-opt",
                    "ExtraPackages": "AppConfig.v3r306",
                    "mcTCK": "",
                    "prodStepID": "998['SDST']",
                    "DDDB": "dddb-20150724",
                    "CONDDB": "cond-20161011",
                    "DQTag": "",
                    "isMulticore": "N",
                    "fileTypesIn": ["SDST"],
                    "visibilityFlag": [
                        {"Visible": "Y", "FileType": "BHADRON.DST"},
                        {"Visible": "Y", "FileType": "CALIBRATION.DST"},
                    ],
                    "fileTypesOut": ["BHADRON.DST", "CALIBRATION.DST"],
                }
            ],
        )

        pr = ProductionRequest(self.bkClientFake, self.diracProdIn)
        pr.stepsList = ["999"]
        pr.outputVisFlag = [{"1": "Y"}]
        pr.compressionLvl = [""] * 4
        pr.resolveSteps()
        self.assertEqual(
            pr.stepsListDict,
            [
                {
                    "StepId": 999,
                    "StepName": "Stripping28",
                    "ApplicationName": "DaVinci",
                    "ApplicationVersion": "v41r3",
                    "ExtraOptions": "",
                    # 'OptionFiles':'$APPCONFIGOPTS/Persistency/Compression-ZLIB-1.py;$APPCONFIGOPTS/Persistency/Compression-LZMA-4.py',
                    "OptionFiles": "",
                    "Visible": "Yes",
                    "Usable": "Yes",
                    "ProcessingPass": "Stripping28",
                    "SystemConfig": "x86_64-slc5-gcc49-opt",
                    "ExtraPackages": "AppConfig.v3r306",
                    "mcTCK": "",
                    "prodStepID": "999['SDST']",
                    "DDDB": "dddb-20150724",
                    "CONDDB": "cond-20161011",
                    "DQTag": "",
                    "isMulticore": "N",
                    "fileTypesIn": ["SDST"],
                    "visibilityFlag": [
                        {"Visible": "Y", "FileType": "BHADRON.DST"},
                        {"Visible": "Y", "FileType": "CALIBRATION.DST"},
                    ],
                    "fileTypesOut": ["BHADRON.DST", "CALIBRATION.DST"],
                }
            ],
        )

        pr = ProductionRequest(self.bkClientFake, self.diracProdIn)
        pr.compressionLvl = ["HIGH"]
        pr.outputVisFlag = [{"1": "Y"}]
        pr.stepsList = ["997"]
        pr.resolveSteps()
        optionFilesStep997 = "$APPCONFIGOPTS/Brunel/DataType-2016.py;"
        optionFilesStep997 += "$APPCONFIGOPTS/Brunel/PbPb-GECs.py;$APPCONFIGOPTS/Persistency/Compression-LZMA-4.py"
        self.assertEqual(
            pr.stepsListDict,
            [
                {
                    "StepId": 997,
                    "StepName": "Stripping28",
                    "ApplicationName": "DaVinci",
                    "ApplicationVersion": "v41r3",
                    "ExtraOptions": "",
                    "OptionFiles": optionFilesStep997,
                    "Visible": "Yes",
                    "Usable": "Yes",
                    "ProcessingPass": "Stripping28",
                    "SystemConfig": "x86_64-slc6-gcc49-opt",
                    "ExtraPackages": "AppConfig.v3r306",
                    "mcTCK": "",
                    "prodStepID": "997['SDST']",
                    "DDDB": "dddb-20150724",
                    "CONDDB": "cond-20161011",
                    "DQTag": "",
                    "isMulticore": "N",
                    "fileTypesIn": ["SDST"],
                    "visibilityFlag": [
                        {"Visible": "Y", "FileType": "BHADRON.DST"},
                        {"Visible": "Y", "FileType": "CALIBRATION.DST"},
                    ],
                    "fileTypesOut": ["BHADRON.DST", "CALIBRATION.DST"],
                }
            ],
        )

        pr = ProductionRequest(self.bkClientFake, self.diracProdIn)
        pr.compressionLvl = ["HIGH"]
        pr.outputVisFlag = [{"1": "Y"}]
        pr.stepsList = ["996"]
        pr.resolveSteps()
        optionFilesStep996 = "$APPCONFIGOPTS/Brunel/DataType-2016.py;"
        optionFilesStep996 += "$APPCONFIGOPTS/Persistency/Compression-LZMA-4.py;$APPCONFIGOPTS/Brunel/PbPb-GECs.py"
        self.assertEqual(
            pr.stepsListDict,
            [
                {
                    "StepId": 996,
                    "StepName": "Stripping28",
                    "ApplicationName": "DaVinci",
                    "ApplicationVersion": "v41r3",
                    "ExtraOptions": "",
                    "OptionFiles": optionFilesStep996,
                    "Visible": "Yes",
                    "Usable": "Yes",
                    "ProcessingPass": "Stripping28",
                    "SystemConfig": "x86_64-slc6-gcc49-opt",
                    "ExtraPackages": "AppConfig.v3r306",
                    "mcTCK": "",
                    "prodStepID": "996['SDST']",
                    "DDDB": "dddb-20150724",
                    "CONDDB": "cond-20161011",
                    "DQTag": "",
                    "isMulticore": "N",
                    "fileTypesIn": ["SDST"],
                    "visibilityFlag": [
                        {"Visible": "Y", "FileType": "BHADRON.DST"},
                        {"Visible": "Y", "FileType": "CALIBRATION.DST"},
                    ],
                    "fileTypesOut": ["BHADRON.DST", "CALIBRATION.DST"],
                }
            ],
        )

        pr = ProductionRequest(self.bkClientFake, self.diracProdIn)
        pr.compressionLvl = [""] * 4
        pr.outputVisFlag = [{"1": "Y"}]
        pr.stepsList = ["1098"]
        pr.resolveSteps()
        self.assertEqual(
            pr.stepsListDict,
            [
                {
                    "StepId": 1098,
                    "StepName": "Stripping28",
                    "ApplicationName": "DaVinci",
                    "ApplicationVersion": "v41r3",
                    "ExtraOptions": "",
                    "OptionFiles": "$APPCONFIGOPTS/Brunel/DataType-2016.py;",
                    "Visible": "Yes",
                    "Usable": "Yes",
                    "ProcessingPass": "Stripping28",
                    "SystemConfig": "x86_64-slc6-gcc49-opt",
                    "ExtraPackages": "AppConfig.v3r306",
                    "mcTCK": "",
                    "prodStepID": "1098['SDST']",
                    "DDDB": "dddb-20150724",
                    "CONDDB": "cond-20161011",
                    "DQTag": "",
                    "isMulticore": "N",
                    "fileTypesIn": ["SDST"],
                    "visibilityFlag": [
                        {"Visible": "Y", "FileType": "BHADRON.DST"},
                        {"Visible": "Y", "FileType": "CALIBRATION.DST"},
                    ],
                    "fileTypesOut": ["BHADRON.DST", "CALIBRATION.DST"],
                }
            ],
        )

        pr = ProductionRequest(self.bkClientFake, self.diracProdIn)
        pr.compressionLvl = ["HIGH"]
        pr.outputVisFlag = [{"1": "Y"}]
        pr.specialOutputVisFlag = [{"1": {"BHADRON.DST": "Y"}}]
        pr.stepsList = ["1098"]
        pr.resolveSteps()
        optionFilesStep1098 = "$APPCONFIGOPTS/Brunel/DataType-2016.py;"
        optionFilesStep1098 += "$APPCONFIGOPTS/Persistency/Compression-LZMA-4.py;"
        optionFilesStep1098 += "$APPCONFIGOPTS/Persistency/Compression-LZMA-4.py"
        self.assertEqual(
            pr.stepsListDict,
            [
                {
                    "StepId": 1098,
                    "StepName": "Stripping28",
                    "ApplicationName": "DaVinci",
                    "ApplicationVersion": "v41r3",
                    "ExtraOptions": "",
                    "OptionFiles": optionFilesStep1098,
                    "Visible": "Yes",
                    "Usable": "Yes",
                    "ProcessingPass": "Stripping28",
                    "SystemConfig": "x86_64-slc6-gcc49-opt",
                    "ExtraPackages": "AppConfig.v3r306",
                    "mcTCK": "",
                    "prodStepID": "1098['SDST']",
                    "DDDB": "dddb-20150724",
                    "CONDDB": "cond-20161011",
                    "DQTag": "",
                    "isMulticore": "N",
                    "fileTypesIn": ["SDST"],
                    "visibilityFlag": [
                        {"Visible": "Y", "FileType": "BHADRON.DST"},
                        {"Visible": "Y", "FileType": "CALIBRATION.DST"},
                    ],
                    "fileTypesOut": ["BHADRON.DST", "CALIBRATION.DST"],
                }
            ],
        )

        pr = ProductionRequest(self.bkClientFake, self.diracProdIn)
        pr.compressionLvl = [""]
        pr.outputVisFlag = [{"1": "Y"}]
        pr.specialOutputVisFlag = [{"1": {"BHADRON.DST": "Y"}}]
        pr.stepsList = ["1099"]
        pr.resolveSteps()
        self.assertEqual(
            pr.stepsListDict,
            [
                {
                    "StepId": 1099,
                    "StepName": "Stripping28",
                    "ApplicationName": "DaVinci",
                    "ApplicationVersion": "v41r3",
                    "ExtraOptions": "",
                    "OptionFiles": "$APPCONFIGOPTS/Brunel/DataType-2016.py;",
                    "Visible": "Yes",
                    "Usable": "Yes",
                    "ProcessingPass": "Stripping28",
                    "SystemConfig": "x86_64-slc6-gcc49-opt",
                    "ExtraPackages": "AppConfig.v3r306",
                    "mcTCK": "",
                    "prodStepID": "1099['SDST']",
                    "DDDB": "dddb-20150724",
                    "CONDDB": "cond-20161011",
                    "DQTag": "",
                    "isMulticore": "N",
                    "fileTypesIn": ["SDST"],
                    "visibilityFlag": [
                        {"Visible": "Y", "FileType": "BHADRON.DST"},
                        {"Visible": "Y", "FileType": "CALIBRATION.DST"},
                    ],
                    "fileTypesOut": ["BHADRON.DST", "CALIBRATION.DST"],
                }
            ],
        )

        pr = ProductionRequest(self.bkClientFake, self.diracProdIn)
        pr.compressionLvl = ["", "HIGH", "LOW"]
        pr.outputVisFlag = [{"1": "N", "2": "N", "3": "N"}]
        pr.specialOutputVisFlag = [{"3": {"BHADRON.DST": "Y"}}]
        pr.stepsList = ["1098", "996", "997"]
        pr.resolveSteps()
        optionFilesStep996 = "$APPCONFIGOPTS/Brunel/DataType-2016.py;"
        optionFilesStep996 += "$APPCONFIGOPTS/Persistency/Compression-LZMA-4.py;"
        optionFilesStep996 += "$APPCONFIGOPTS/Brunel/PbPb-GECs.py"
        optionFilesStep997 = "$APPCONFIGOPTS/Brunel/DataType-2016.py;"
        optionFilesStep997 += "$APPCONFIGOPTS/Brunel/PbPb-GECs.py;"
        optionFilesStep997 += "$APPCONFIGOPTS/Persistency/Compression-ZLIB-1.py"
        self.assertEqual(
            pr.stepsListDict,
            [
                {
                    "StepId": 1098,
                    "StepName": "Stripping28",
                    "ApplicationName": "DaVinci",
                    "ApplicationVersion": "v41r3",
                    "ExtraOptions": "",
                    "OptionFiles": "$APPCONFIGOPTS/Brunel/DataType-2016.py;",
                    "Visible": "Yes",
                    "Usable": "Yes",
                    "ProcessingPass": "Stripping28",
                    "SystemConfig": "x86_64-slc6-gcc49-opt",
                    "ExtraPackages": "AppConfig.v3r306",
                    "mcTCK": "",
                    "prodStepID": "1098['SDST']",
                    "DDDB": "dddb-20150724",
                    "CONDDB": "cond-20161011",
                    "DQTag": "",
                    "isMulticore": "N",
                    "fileTypesIn": ["SDST"],
                    "visibilityFlag": [
                        {"Visible": "N", "FileType": "BHADRON.DST"},
                        {"Visible": "N", "FileType": "CALIBRATION.DST"},
                    ],
                    "fileTypesOut": ["BHADRON.DST", "CALIBRATION.DST"],
                },
                {
                    "StepId": 996,
                    "StepName": "Stripping28",
                    "ApplicationName": "DaVinci",
                    "ApplicationVersion": "v41r3",
                    "ExtraOptions": "",
                    "OptionFiles": optionFilesStep996,
                    "Visible": "Yes",
                    "Usable": "Yes",
                    "ProcessingPass": "Stripping28",
                    "SystemConfig": "x86_64-slc6-gcc49-opt",
                    "ExtraPackages": "AppConfig.v3r306",
                    "mcTCK": "",
                    "prodStepID": "996['SDST']",
                    "DDDB": "dddb-20150724",
                    "CONDDB": "cond-20161011",
                    "DQTag": "",
                    "isMulticore": "N",
                    "fileTypesIn": ["SDST"],
                    "visibilityFlag": [
                        {"Visible": "N", "FileType": "BHADRON.DST"},
                        {"Visible": "N", "FileType": "CALIBRATION.DST"},
                    ],
                    "fileTypesOut": ["BHADRON.DST", "CALIBRATION.DST"],
                },
                {
                    "StepId": 997,
                    "StepName": "Stripping28",
                    "ApplicationName": "DaVinci",
                    "ApplicationVersion": "v41r3",
                    "ExtraOptions": "",
                    "OptionFiles": optionFilesStep997,
                    "Visible": "Yes",
                    "Usable": "Yes",
                    "ProcessingPass": "Stripping28",
                    "SystemConfig": "x86_64-slc6-gcc49-opt",
                    "ExtraPackages": "AppConfig.v3r306",
                    "mcTCK": "",
                    "prodStepID": "997['SDST']",
                    "DDDB": "dddb-20150724",
                    "CONDDB": "cond-20161011",
                    "DQTag": "",
                    "isMulticore": "N",
                    "fileTypesIn": ["SDST"],
                    "visibilityFlag": [
                        {"Visible": "Y", "FileType": "BHADRON.DST"},
                        {"Visible": "N", "FileType": "CALIBRATION.DST"},
                    ],
                    "fileTypesOut": ["BHADRON.DST", "CALIBRATION.DST"],
                },
            ],
        )

        pr = ProductionRequest(self.bkClientFake, self.diracProdIn)
        pr.compressionLvl = ["", "HIGH"]
        pr.outputVisFlag = [{"1": "N", "2": "N", "3": "N"}]
        pr.specialOutputVisFlag = [{"2": {"BHADRON.DST": "Y"}}]
        pr.stepsList = ["1098", "996", "997"]
        pr.resolveSteps()
        optionFilesStep996 = "$APPCONFIGOPTS/Brunel/DataType-2016.py;"
        optionFilesStep996 += "$APPCONFIGOPTS/Persistency/Compression-LZMA-4.py;$APPCONFIGOPTS/Brunel/PbPb-GECs.py"
        optionFilesStep997 = "$APPCONFIGOPTS/Brunel/DataType-2016.py;$APPCONFIGOPTS/Brunel/PbPb-GECs.py"
        self.assertEqual(
            pr.stepsListDict,
            [
                {
                    "StepId": 1098,
                    "StepName": "Stripping28",
                    "ApplicationName": "DaVinci",
                    "ApplicationVersion": "v41r3",
                    "ExtraOptions": "",
                    "OptionFiles": "$APPCONFIGOPTS/Brunel/DataType-2016.py;",
                    "Visible": "Yes",
                    "Usable": "Yes",
                    "ProcessingPass": "Stripping28",
                    "SystemConfig": "x86_64-slc6-gcc49-opt",
                    "ExtraPackages": "AppConfig.v3r306",
                    "mcTCK": "",
                    "prodStepID": "1098['SDST']",
                    "DDDB": "dddb-20150724",
                    "CONDDB": "cond-20161011",
                    "DQTag": "",
                    "isMulticore": "N",
                    "fileTypesIn": ["SDST"],
                    "visibilityFlag": [
                        {"Visible": "N", "FileType": "BHADRON.DST"},
                        {"Visible": "N", "FileType": "CALIBRATION.DST"},
                    ],
                    "fileTypesOut": ["BHADRON.DST", "CALIBRATION.DST"],
                },
                {
                    "StepId": 996,
                    "StepName": "Stripping28",
                    "ApplicationName": "DaVinci",
                    "ApplicationVersion": "v41r3",
                    "ExtraOptions": "",
                    "OptionFiles": optionFilesStep996,
                    "Visible": "Yes",
                    "Usable": "Yes",
                    "ProcessingPass": "Stripping28",
                    "SystemConfig": "x86_64-slc6-gcc49-opt",
                    "ExtraPackages": "AppConfig.v3r306",
                    "mcTCK": "",
                    "prodStepID": "996['SDST']",
                    "DDDB": "dddb-20150724",
                    "CONDDB": "cond-20161011",
                    "DQTag": "",
                    "isMulticore": "N",
                    "fileTypesIn": ["SDST"],
                    "visibilityFlag": [
                        {"Visible": "Y", "FileType": "BHADRON.DST"},
                        {"Visible": "N", "FileType": "CALIBRATION.DST"},
                    ],
                    "fileTypesOut": ["BHADRON.DST", "CALIBRATION.DST"],
                },
                {
                    "StepId": 997,
                    "StepName": "Stripping28",
                    "ApplicationName": "DaVinci",
                    "ApplicationVersion": "v41r3",
                    "ExtraOptions": "",
                    "OptionFiles": optionFilesStep997,
                    "Visible": "Yes",
                    "Usable": "Yes",
                    "ProcessingPass": "Stripping28",
                    "SystemConfig": "x86_64-slc6-gcc49-opt",
                    "ExtraPackages": "AppConfig.v3r306",
                    "mcTCK": "",
                    "prodStepID": "997['SDST']",
                    "DDDB": "dddb-20150724",
                    "CONDDB": "cond-20161011",
                    "DQTag": "",
                    "isMulticore": "N",
                    "fileTypesIn": ["SDST"],
                    "visibilityFlag": [
                        {"Visible": "N", "FileType": "BHADRON.DST"},
                        {"Visible": "N", "FileType": "CALIBRATION.DST"},
                    ],
                    "fileTypesOut": ["BHADRON.DST", "CALIBRATION.DST"],
                },
            ],
        )

    def test__determineOutputSEs(self):
        pr = ProductionRequest(self.bkClientFake, self.diracProdIn)
        pr.stepsList = ["123", "456"]
        pr.compressionLvl = ["LOW", "HIGH"]
        pr.outputVisFlag = [{"1": "N"}, {"2": "N"}]
        pr.resolveSteps()
        pr.outputSEs = ["SE1", "SE2"]
        pr.specialOutputSEs = [{}, {}]
        pr._determineOutputSEs()
        self.assertEqual(
            pr.outputSEsPerFileType,
            [{"CALIBRATION.DST": "SE1", "BHADRON.DST": "SE1"}, {"CALIBRATION.DST": "SE2", "BHADRON.DST": "SE2"}],
        )

        pr = ProductionRequest(self.bkClientFake, self.diracProdIn)
        pr.outputVisFlag = [{"1": "N"}, {"2": "N"}]
        pr.stepsList = ["123", "456"]
        pr.compressionLvl = ["LOW", "HIGH"]
        pr.resolveSteps()
        pr.outputSEs = ["SE1", "SE2"]
        pr.specialOutputSEs = [{"CALIBRATION.DST": "SE3"}, {}]
        pr._determineOutputSEs()
        self.assertEqual(
            pr.outputSEsPerFileType,
            [{"CALIBRATION.DST": "SE3", "BHADRON.DST": "SE1"}, {"CALIBRATION.DST": "SE2", "BHADRON.DST": "SE2"}],
        )

    def test__applyOptionalCorrections(self):

        pr = ProductionRequest(self.bkClientFake, self.diracProdIn)
        pr.prodsTypeList = ["DataStripping", "Merge"]
        pr.plugins = ["ByRun", "BySize"]
        pr.stepsListDict = [stepStripp, mergeStep]
        pr.outputVisFlag = [{"1": "N"}, {"2": "N"}]
        pr.stepsList = [123, 456]
        pr.stepsInProds = [[1], [2]]
        pr.outputSEs = ["Tier1-DST", "Tier1-M-DST"]
        pr.specialOutputSEs = [{}, {}]
        pr.priorities = [1, 4]
        pr.cpus = [10, 100]
        pr.groupSizes = [1, 2]
        pr.bkFileType = "TYPE"
        pr.removeInputsFlags = [False, True]
        pr.outputFileMasks = ["", "dst"]
        pr.outputFileSteps = ["", "2"]
        pr.inputs = [["aa"], []]
        pr.inputDataPolicies = ["dl", "pr"]
        pr.events = [-1, -1]
        pr.bkQueries = ["Full", "fromPreviousProd"]
        pr.targets = ["Target1", "Target2"]
        pr.multicore = ["False", "True"]
        pr.processors = [(2, 4), (0, 0)]
        pr.outputModes = ["Local", "Any"]
        pr.ancestorDepths = [0, 1]
        pr._applyOptionalCorrections()
        prodsTypeListExpected = ["DataStripping", "Merge", "Merge", "Merge"]
        pluginsExpected = ["ByRun", "BySize", "BySize", "BySize"]
        stepsListDictExpected = [stepStripp, mergeStepBHADRON, mergeStepCALIBRA, mergeStepPIDMDST]
        stepsInProdExpected = [[1], [2], [3], [4]]
        outputSEsExpected = ["Tier1-DST", "Tier1-M-DST", "Tier1-M-DST", "Tier1-M-DST"]
        specialOutputSEsExpected = [{}, {}, {}, {}]
        prioritiesExpected = [1, 4, 4, 4]
        cpusExpected = [10, 100, 100, 100]
        bkQueriesExpected = ["Full", "fromPreviousProd", "fromPreviousProd", "fromPreviousProd"]
        groupSizesExpected = [1, 2, 2, 2]
        previousProdsExpected = [None, 1, 1, 1]
        removeInputsFlagExpected = [False, True, True, True]
        outputFileMasksExpected = ["", "dst", "dst", "dst"]
        outputFileStepsExpected = ["", "2", "2", "2"]
        inputsExpected = [["aa"], [], [], []]
        inputDataPoliciesExpected = ["dl", "pr", "pr", "pr"]
        eventsExpected = [-1, -1, -1, -1]
        targetsExpected = ["Target1", "Target2", "Target2", "Target2"]
        multicoreExpected = ["False", "True", "True", "True"]
        processorsExpected = [(2, 4), (0, 0), (0, 0), (0, 0)]
        outputModeExpected = ["Local", "Any", "Any", "Any"]
        ancestorDepthsExpected = [0, 1, 1, 1]
        self.assertEqual(pr.prodsTypeList, prodsTypeListExpected)
        self.assertEqual(pr.plugins, pluginsExpected)
        self.assertEqual(pr.stepsListDict, stepsListDictExpected)
        self.assertEqual(pr.stepsInProds, stepsInProdExpected)
        self.assertEqual(pr.outputSEs, outputSEsExpected)
        self.assertEqual(pr.specialOutputSEs, specialOutputSEsExpected)
        self.assertEqual(pr.priorities, prioritiesExpected)
        self.assertEqual(pr.cpus, cpusExpected)
        self.assertEqual(pr.groupSizes, groupSizesExpected)
        self.assertEqual(pr.bkQueries, bkQueriesExpected)
        self.assertEqual(pr.previousProds, previousProdsExpected)
        self.assertEqual(pr.removeInputsFlags, removeInputsFlagExpected)
        self.assertEqual(pr.outputFileMasks, outputFileMasksExpected)
        self.assertEqual(pr.outputFileSteps, outputFileStepsExpected)
        self.assertEqual(pr.inputs, inputsExpected)
        self.assertEqual(pr.inputDataPolicies, inputDataPoliciesExpected)
        self.assertEqual(pr.events, eventsExpected)
        self.assertEqual(pr.targets, targetsExpected)
        self.assertEqual(pr.multicore, multicoreExpected)
        self.assertEqual(pr.processors, processorsExpected)
        self.assertEqual(pr.outputModes, outputModeExpected)
        self.assertEqual(pr.ancestorDepths, ancestorDepthsExpected)

        pr = ProductionRequest(self.bkClientFake, self.diracProdIn)
        pr.prodsTypeList = ["DataStripping", "Merge"]
        pr.plugins = ["ByRun", "ByRunFileTypeSizeWithFlush"]
        pr.stepsListDict = [stepStripp, mergeStep]
        pr.stepsList = [123, 456]
        pr.stepsInProds = [[1], [2]]
        pr.outputSEs = ["Tier1-DST", "Tier1-M-DST"]
        pr.specialOutputSEs = [{"Type1": "SE1"}, {}]
        pr.priorities = [1, 4]
        pr.cpus = [10, 100]
        pr.groupSizes = [1, 2]
        pr.bkFileType = ["Type1", "Type2"]
        pr.inputs = [[], ["aa"]]
        pr.removeInputsFlags = [False, True]
        pr.outputFileMasks = ["", "dst"]
        pr.outputFileSteps = ["", "2"]
        pr.inputDataPolicies = ["pr", "dl"]
        pr.events = [-1, -1]
        pr.bkQueries = ["Full", "fromPreviousProd"]
        pr.targets = ["Target1", "Target2"]
        pr.multicore = ["False", "True"]
        pr.processors = [2, 0]
        pr.outputModes = ["Local", "Any"]
        pr.ancestorDepths = [0, 0]
        pr._applyOptionalCorrections()
        prodsTypeListExpected = ["DataStripping", "Merge"]
        pluginsExpected = ["ByRun", "ByRunFileTypeSizeWithFlush"]
        stepsListDictExpected = [stepStripp, mergeStep]
        stepsInProdExpected = [[1], [2]]
        outputSEsExpected = ["Tier1-DST", "Tier1-M-DST"]
        specialOutputSEsExpected = [{"Type1": "SE1"}, {}]
        prioritiesExpected = [1, 4]
        cpusExpected = [10, 100]
        groupSizesExpected = [1, 2]
        bkQueriesExpected = ["Full", "fromPreviousProd"]
        previousProdsExpected = [None, 1]
        removeInputsFlagExpected = [False, True]
        outputFileMasksExpected = ["", "dst"]
        outputFileStepsExpected = ["", "2"]
        inputsExpected = [[], ["aa"]]
        inputDataPoliciesExpected = ["pr", "dl"]
        eventsExpected = [-1, -1]
        targetsExpected = ["Target1", "Target2"]
        multicoreExpected = ["False", "True"]
        processorsExpected = [2, 0]
        outputModeExpected = ["Local", "Any"]
        ancestorDepthsExpected = [0, 0]
        self.assertEqual(pr.prodsTypeList, prodsTypeListExpected)
        self.assertEqual(pr.plugins, pluginsExpected)
        self.assertEqual(pr.stepsListDict, stepsListDictExpected)
        self.assertEqual(pr.stepsInProds, stepsInProdExpected)
        self.assertEqual(pr.outputSEs, outputSEsExpected)
        self.assertEqual(pr.specialOutputSEs, specialOutputSEsExpected)
        self.assertEqual(pr.priorities, prioritiesExpected)
        self.assertEqual(pr.cpus, cpusExpected)
        self.assertEqual(pr.groupSizes, groupSizesExpected)
        self.assertEqual(pr.bkQueries, bkQueriesExpected)
        self.assertEqual(pr.previousProds, previousProdsExpected)
        self.assertEqual(pr.removeInputsFlags, removeInputsFlagExpected)
        self.assertEqual(pr.outputFileMasks, outputFileMasksExpected)
        self.assertEqual(pr.outputFileSteps, outputFileStepsExpected)
        self.assertEqual(pr.inputs, inputsExpected)
        self.assertEqual(pr.inputDataPolicies, inputDataPoliciesExpected)
        self.assertEqual(pr.events, eventsExpected)
        self.assertEqual(pr.targets, targetsExpected)
        self.assertEqual(pr.multicore, multicoreExpected)
        self.assertEqual(pr.processors, processorsExpected)
        self.assertEqual(pr.outputModes, outputModeExpected)
        self.assertEqual(pr.ancestorDepths, ancestorDepthsExpected)

        pr = ProductionRequest(self.bkClientFake, self.diracProdIn)
        pr.prodsTypeList = ["Merge", "Merge"]
        pr.plugins = ["BySize", "ByRunFileTypeSizeWithFlush"]
        pr.stepsListDict = [mergeStep, mergeStep]
        pr.stepsList = [456, 456]
        pr.stepsInProds = [[1], [2]]
        pr.outputSEs = ["Tier1-DST", "Tier1-M-DST"]
        pr.specialOutputSEs = [{"Type1": "SE1"}, {}]
        pr.priorities = [1, 4]
        pr.cpus = [10, 100]
        pr.groupSizes = [1, 2]
        pr.removeInputsFlags = [True, True]
        pr.outputFileMasks = ["", "dst"]
        pr.outputFileSteps = ["", "2"]
        pr.inputs = [[], ["aa"]]
        pr.inputDataPolicies = ["dl", "pr"]
        pr.events = [-1, -1]
        pr.bkQueries = ["fromPreviousProd", "fromPreviousProd"]
        pr.targets = ["Target1", "Target2"]
        pr.multicore = ["False", "True"]
        pr.processors = [2, 0]
        pr.outputModes = ["Local", "Any"]
        pr.ancestorDepths = [1, 0]
        pr._applyOptionalCorrections()
        prodsTypeListExpected = ["Merge", "Merge", "Merge", "Merge"]
        pluginsExpected = ["BySize", "BySize", "BySize", "ByRunFileTypeSizeWithFlush"]
        stepsListDictExpected = [mergeStepBHADRON, mergeStepCALIBRA, mergeStepPIDMDST, mergeStep]
        stepsInProdExpected = [[1], [2], [3], [4]]
        outputSEsExpected = ["Tier1-DST", "Tier1-DST", "Tier1-DST", "Tier1-M-DST"]
        specialOutputSEsExpected = [{"Type1": "SE1"}, {"Type1": "SE1"}, {"Type1": "SE1"}, {}]
        prioritiesExpected = [1, 1, 1, 4]
        cpusExpected = [10, 10, 10, 100]
        groupSizesExpected = [1, 1, 1, 2]
        bkQueriesExpected = ["fromPreviousProd", "fromPreviousProd", "fromPreviousProd", "fromPreviousProd"]
        previousProdsExpected = [None, None, None, 1]
        removeInputsFlagExpected = [True, True, True, True]
        outputFileMasksExpected = ["", "", "", "dst"]
        outputFileStepsExpected = ["", "", "", "2"]
        inputsExpected = [[], [], [], ["aa"]]
        inputDataPoliciesExpected = ["dl", "dl", "dl", "pr"]
        eventsExpected = [-1, -1, -1, -1]
        targetsExpected = ["Target1", "Target1", "Target1", "Target2"]
        multicoreExpected = ["False", "False", "False", "True"]
        processorsExpected = [2, 2, 2, 0]
        outputModeExpected = ["Local", "Local", "Local", "Any"]
        ancestorDepthsExpected = [1, 1, 1, 0]
        self.assertEqual(pr.prodsTypeList, prodsTypeListExpected)
        self.assertEqual(pr.plugins, pluginsExpected)
        self.assertEqual(pr.stepsListDict, stepsListDictExpected)
        self.assertEqual(pr.stepsInProds, stepsInProdExpected)
        self.assertEqual(pr.outputSEs, outputSEsExpected)
        self.assertEqual(pr.specialOutputSEs, specialOutputSEsExpected)
        self.assertEqual(pr.priorities, prioritiesExpected)
        self.assertEqual(pr.cpus, cpusExpected)
        self.assertEqual(pr.groupSizes, groupSizesExpected)
        self.assertEqual(pr.bkQueries, bkQueriesExpected)
        self.assertEqual(pr.previousProds, previousProdsExpected)
        self.assertEqual(pr.removeInputsFlags, removeInputsFlagExpected)
        self.assertEqual(pr.outputFileMasks, outputFileMasksExpected)
        self.assertEqual(pr.outputFileSteps, outputFileStepsExpected)
        self.assertEqual(pr.inputs, inputsExpected)
        self.assertEqual(pr.inputDataPolicies, inputDataPoliciesExpected)
        self.assertEqual(pr.events, eventsExpected)
        self.assertEqual(pr.targets, targetsExpected)
        self.assertEqual(pr.multicore, multicoreExpected)
        self.assertEqual(pr.processors, processorsExpected)
        self.assertEqual(pr.outputModes, outputModeExpected)
        self.assertEqual(pr.ancestorDepths, ancestorDepthsExpected)

        pr = ProductionRequest(self.bkClientFake, self.diracProdIn)
        pr.prodsTypeList = ["DataStripping"]
        pr.plugins = ["ByRun"]
        pr.stepsListDict = [stepStripp, mergeStep]
        pr.stepsList = [123]
        pr.stepsInProds = [[1, 2]]
        pr.priorities = [1]
        pr.outputSEs = ["Tier1-DST"]
        pr.cpus = [10]
        pr.groupSizes = [1]
        pr.bkFileType = "TYPE"
        pr.removeInputsFlags = [False]
        pr.outputFileMasks = [""]
        pr.outputFileSteps = ["2"]
        pr.inputs = [[]]
        pr.inputDataPolicies = [""]
        pr.events = [-1]
        pr.bkQueries = ["Full"]
        pr.targets = ["Target1"]
        pr.multicore = ["False"]
        pr.processors = [2]
        pr.outputModes = ["Local"]
        pr.ancestorDepths = [1]
        pr._applyOptionalCorrections()
        prodsTypeListExpected = ["DataStripping"]
        pluginsExpected = ["ByRun"]
        stepsListDictExpected = [stepStripp, mergeStep]
        stepsInProdExpected = [[1, 2]]
        outputSEsExpected = ["Tier1-DST"]
        prioritiesExpected = [1]
        cpusExpected = [10]
        groupSizesExpected = [1]
        bkQueriesExpected = ["Full"]
        previousProdsExpected = [None]
        removeInputsFlagExpected = [False]
        outputFileMasksExpected = [""]
        outputFileStepsExpected = ["2"]
        inputsExpected = [[]]
        inputDataPoliciesExpected = [""]
        eventsExpected = [-1]
        targetsExpected = ["Target1"]
        multicoreExpected = ["False"]
        processorsExpected = [2]
        outputModeExpected = ["Local"]
        ancestorDepthsExpected = [1]
        self.assertEqual(pr.prodsTypeList, prodsTypeListExpected)
        self.assertEqual(pr.plugins, pluginsExpected)
        self.assertEqual(pr.stepsListDict, stepsListDictExpected)
        self.assertEqual(pr.stepsInProds, stepsInProdExpected)
        self.assertEqual(pr.outputSEs, outputSEsExpected)
        self.assertEqual(pr.priorities, prioritiesExpected)
        self.assertEqual(pr.cpus, cpusExpected)
        self.assertEqual(pr.groupSizes, groupSizesExpected)
        self.assertEqual(pr.bkQueries, bkQueriesExpected)
        self.assertEqual(pr.previousProds, previousProdsExpected)
        self.assertEqual(pr.removeInputsFlags, removeInputsFlagExpected)
        self.assertEqual(pr.outputFileMasks, outputFileMasksExpected)
        self.assertEqual(pr.outputFileSteps, outputFileStepsExpected)
        self.assertEqual(pr.inputs, inputsExpected)
        self.assertEqual(pr.inputDataPolicies, inputDataPoliciesExpected)
        self.assertEqual(pr.events, eventsExpected)
        self.assertEqual(pr.targets, targetsExpected)
        self.assertEqual(pr.multicore, multicoreExpected)
        self.assertEqual(pr.processors, processorsExpected)
        self.assertEqual(pr.outputModes, outputModeExpected)
        self.assertEqual(pr.ancestorDepths, ancestorDepthsExpected)

        pr = ProductionRequest(self.bkClientFake, self.diracProdIn)
        pr.prodsTypeList = ["DataStripping", "Merge", "Merge"]
        pr.plugins = ["ByRun", "BySize", "ByRunFileTypeSizeWithFlush"]
        pr.stepsListDict = [stepStripp, mergeStep, mergeStep]
        pr.stepsList = [123, 456, 456]
        pr.stepsInProds = [[1], [2], [3]]
        pr.outputSEs = ["Tier1-DST", "Tier1-M-DST", "Tier1-M-DST"]
        pr.priorities = [1, 4, 5]
        pr.cpus = [10, 100, 1000]
        pr.groupSizes = [1, 2, 3]
        pr.bkFileType = "TYPE"
        pr.removeInputsFlags = [False, True, True]
        pr.outputFileMasks = ["", "dst", ""]
        pr.outputFileSteps = ["", "2", ""]
        pr.inputs = [[], ["aa"], ["bb"]]
        pr.inputDataPolicies = ["", "dl", "pr"]
        pr.bkQueries = ["Full", "fromPreviousProd", "fromPreviousProd"]
        pr.events = [-1, -1, -1]
        pr.targets = ["Target1", "Target2", "Target3"]
        pr.multicore = ["False", "True", "False"]
        pr.processors = [2, 0, 4]
        pr.outputModes = ["Local", "Any", "Any"]
        pr.ancestorDepths = [1, 2, 3]
        pr._applyOptionalCorrections()
        prodsTypeListExpected = ["DataStripping", "Merge", "Merge", "Merge", "Merge"]
        pluginsExpected = ["ByRun", "BySize", "BySize", "BySize", "ByRunFileTypeSizeWithFlush"]
        stepsListDictExpected = [stepStripp, mergeStepBHADRON, mergeStepCALIBRA, mergeStepPIDMDST, mergeStep]
        stepsInProdExpected = [[1], [2], [3], [4], [5]]
        outputSEsExpected = ["Tier1-DST", "Tier1-M-DST", "Tier1-M-DST", "Tier1-M-DST", "Tier1-M-DST"]
        prioritiesExpected = [1, 4, 4, 4, 5]
        groupSizesExpected = [1, 2, 2, 2, 3]
        cpusExpected = [10, 100, 100, 100, 1000]
        bkQueriesExpected = ["Full", "fromPreviousProd", "fromPreviousProd", "fromPreviousProd", "fromPreviousProd"]
        previousProdsExpected = [None, 1, 1, 1, 2]
        removeInputsFlagExpected = [False, True, True, True, True]
        outputFileMasksExpected = ["", "dst", "dst", "dst", ""]
        outputFileStepsExpected = ["", "2", "2", "2", ""]
        inputsExpected = [[], ["aa"], ["aa"], ["aa"], ["bb"]]
        inputDataPoliciesExpected = ["", "dl", "dl", "dl", "pr"]
        eventsExpected = [-1, -1, -1, -1, -1]
        targetsExpected = ["Target1", "Target2", "Target2", "Target2", "Target3"]
        multicoreExpected = ["False", "True", "True", "True", "False"]
        processorsExpected = [2, 0, 0, 0, 4]
        outputModeExpected = ["Local", "Any", "Any", "Any", "Any"]
        ancestorDepthsExpected = [1, 2, 2, 2, 3]
        self.assertEqual(pr.prodsTypeList, prodsTypeListExpected)
        self.assertEqual(pr.plugins, pluginsExpected)
        self.assertEqual(pr.stepsListDict, stepsListDictExpected)
        self.assertEqual(pr.stepsInProds, stepsInProdExpected)
        self.assertEqual(pr.outputSEs, outputSEsExpected)
        self.assertEqual(pr.priorities, prioritiesExpected)
        self.assertEqual(pr.cpus, cpusExpected)
        self.assertEqual(pr.groupSizes, groupSizesExpected)
        self.assertEqual(pr.bkQueries, bkQueriesExpected)
        self.assertEqual(pr.previousProds, previousProdsExpected)
        self.assertEqual(pr.removeInputsFlags, removeInputsFlagExpected)
        self.assertEqual(pr.outputFileMasks, outputFileMasksExpected)
        self.assertEqual(pr.outputFileSteps, outputFileStepsExpected)
        self.assertEqual(pr.inputs, inputsExpected)
        self.assertEqual(pr.inputDataPolicies, inputDataPoliciesExpected)
        self.assertEqual(pr.events, eventsExpected)
        self.assertEqual(pr.targets, targetsExpected)
        self.assertEqual(pr.multicore, multicoreExpected)
        self.assertEqual(pr.processors, processorsExpected)
        self.assertEqual(pr.outputModes, outputModeExpected)
        self.assertEqual(pr.ancestorDepths, ancestorDepthsExpected)

        pr = ProductionRequest(self.bkClientFake, self.diracProdIn)
        pr.prodsTypeList = ["DataStripping", "Merge"]
        pr.plugins = ["ByRun", "BySize"]
        pr.stepsListDict = [stepStripp, mergeStep]
        pr.stepsList = [123, 456]
        pr.stepsInProds = [[3], [4]]
        pr.outputSEs = ["Tier1-DST", "Tier1-M-DST"]
        pr.priorities = [1, 4]
        pr.cpus = [10, 100]
        pr.groupSizes = [1, 2]
        pr.bkFileType = "TYPE"
        pr.removeInputsFlags = [False, True]
        pr.outputFileMasks = ["", "dst"]
        pr.outputFileSteps = ["", "2"]
        pr.inputs = [[], []]
        pr.inputDataPolicies = ["", "dl"]
        pr.events = [-1, -1]
        pr.bkQueries = ["Full", "fromPreviousProd"]
        pr.targets = ["Target1", "Target2"]
        pr.multicore = ["False", "True"]
        pr.processors = [2, 0]
        pr.outputModes = ["Local", "Any"]
        pr.ancestorDepths = [1, 0]
        pr._applyOptionalCorrections()
        prodsTypeListExpected = ["DataStripping", "Merge", "Merge", "Merge"]
        pluginsExpected = ["ByRun", "BySize", "BySize", "BySize"]
        stepsListDictExpected = [stepStripp, mergeStepBHADRON, mergeStepCALIBRA, mergeStepPIDMDST]
        stepsInProdExpected = [[3], [4], [5], [6]]
        outputSEsExpected = ["Tier1-DST", "Tier1-M-DST", "Tier1-M-DST", "Tier1-M-DST"]
        prioritiesExpected = [1, 4, 4, 4]
        cpusExpected = [10, 100, 100, 100]
        groupSizesExpected = [1, 2, 2, 2]
        bkQueriesExpected = ["Full", "fromPreviousProd", "fromPreviousProd", "fromPreviousProd"]
        previousProdsExpected = [None, 1, 1, 1]
        removeInputsFlagExpected = [False, True, True, True]
        outputFileMasksExpected = ["", "dst", "dst", "dst"]
        outputFileStepsExpected = ["", "2", "2", "2"]
        inputsExpected = [[], [], [], []]
        inputDataPoliciesExpected = ["", "dl", "dl", "dl"]
        eventsExpected = [-1, -1, -1, -1]
        targetsExpected = ["Target1", "Target2", "Target2", "Target2"]
        multicoreExpected = ["False", "True", "True", "True"]
        processorsExpected = [2, 0, 0, 0]
        outputModeExpected = ["Local", "Any", "Any", "Any"]
        ancestorDepthsExpected = [1, 0, 0, 0]
        self.assertEqual(pr.prodsTypeList, prodsTypeListExpected)
        self.assertEqual(pr.plugins, pluginsExpected)
        self.assertEqual(pr.stepsListDict, stepsListDictExpected)
        self.assertEqual(pr.stepsInProds, stepsInProdExpected)
        self.assertEqual(pr.outputSEs, outputSEsExpected)
        self.assertEqual(pr.priorities, prioritiesExpected)
        self.assertEqual(pr.cpus, cpusExpected)
        self.assertEqual(pr.groupSizes, groupSizesExpected)
        self.assertEqual(pr.bkQueries, bkQueriesExpected)
        self.assertEqual(pr.previousProds, previousProdsExpected)
        self.assertEqual(pr.removeInputsFlags, removeInputsFlagExpected)
        self.assertEqual(pr.outputFileMasks, outputFileMasksExpected)
        self.assertEqual(pr.outputFileSteps, outputFileStepsExpected)
        self.assertEqual(pr.inputs, inputsExpected)
        self.assertEqual(pr.inputDataPolicies, inputDataPoliciesExpected)
        self.assertEqual(pr.events, eventsExpected)
        self.assertEqual(pr.targets, targetsExpected)
        self.assertEqual(pr.multicore, multicoreExpected)
        self.assertEqual(pr.processors, processorsExpected)
        self.assertEqual(pr.outputModes, outputModeExpected)
        self.assertEqual(pr.ancestorDepths, ancestorDepthsExpected)

        pr = ProductionRequest(self.bkClientFake, self.diracProdIn)
        pr.prodsTypeList = ["DataStripping"]
        pr.plugins = ["ByRun"]
        pr.stepsListDict = [stepStripp, mergeStep]
        pr.stepsList = [123, 456]
        pr.stepsInProds = [[3, 4]]
        pr.priorities = [1]
        pr.outputSEs = ["Tier1-DST"]
        pr.cpus = [10]
        pr.groupSizes = [1]
        pr.removeInputsFlags = [False]
        pr.outputFileMasks = ["dst"]
        pr.outputFileSteps = ["2"]
        pr.bkFileType = "TYPE"
        pr.inputs = [[]]
        pr.inputDataPolicies = ["dl"]
        pr.events = [-1]
        pr.bkQueries = ["Full"]
        pr.targets = ["Target1"]
        pr.multicore = ["False"]
        pr.processors = [2]
        pr.outputModes = ["Local"]
        pr.ancestorDepths = [1]
        pr._applyOptionalCorrections()
        prodsTypeListExpected = ["DataStripping"]
        pluginsExpected = ["ByRun"]
        stepsListDictExpected = [stepStripp, mergeStep]
        stepsInProdExpected = [[3, 4]]
        outputSEsExpected = ["Tier1-DST"]
        prioritiesExpected = [1]
        cpusExpected = [10]
        groupSizesExpected = [1]
        bkQueriesExpected = ["Full"]
        previousProdsExpected = [None]
        removeInputsFlagExpected = [False]
        outputFileMasksExpected = ["dst"]
        outputFileStepsExpected = ["2"]
        inputsExpected = [[]]
        inputDataPoliciesExpected = ["dl"]
        eventsExpected = [-1]
        targetsExpected = ["Target1"]
        multicoreExpected = ["False"]
        processorsExpected = [2]
        outputModeExpected = ["Local"]
        ancestorDepthsExpected = [1]
        self.assertEqual(pr.prodsTypeList, prodsTypeListExpected)
        self.assertEqual(pr.plugins, pluginsExpected)
        self.assertEqual(pr.stepsListDict, stepsListDictExpected)
        self.assertEqual(pr.stepsInProds, stepsInProdExpected)
        self.assertEqual(pr.outputSEs, outputSEsExpected)
        self.assertEqual(pr.priorities, prioritiesExpected)
        self.assertEqual(pr.cpus, cpusExpected)
        self.assertEqual(pr.groupSizes, groupSizesExpected)
        self.assertEqual(pr.bkQueries, bkQueriesExpected)
        self.assertEqual(pr.previousProds, previousProdsExpected)
        self.assertEqual(pr.removeInputsFlags, removeInputsFlagExpected)
        self.assertEqual(pr.outputFileMasks, outputFileMasksExpected)
        self.assertEqual(pr.outputFileSteps, outputFileStepsExpected)
        self.assertEqual(pr.inputs, inputsExpected)
        self.assertEqual(pr.inputDataPolicies, inputDataPoliciesExpected)
        self.assertEqual(pr.events, eventsExpected)
        self.assertEqual(pr.targets, targetsExpected)
        self.assertEqual(pr.multicore, multicoreExpected)
        self.assertEqual(pr.processors, processorsExpected)
        self.assertEqual(pr.outputModes, outputModeExpected)
        self.assertEqual(pr.ancestorDepths, ancestorDepthsExpected)

        pr = ProductionRequest(self.bkClientFake, self.diracProdIn)
        pr.prodsTypeList = ["Merge", "Merge"]
        pr.plugins = ["BySize", "ByRunFileTypeSizeWithFlush"]
        pr.stepsListDict = [mergeStep, mergeStep]
        pr.stepsList = [456, 456]
        pr.stepsInProds = [[3], [4]]
        pr.outputSEs = ["Tier1-DST", "Tier1-M-DST"]
        pr.priorities = [1, 4]
        pr.cpus = [10, 100]
        pr.groupSizes = [1, 2]
        pr.removeInputsFlags = [True, True]
        pr.outputFileMasks = ["", "dst"]
        pr.outputFileSteps = ["", "2"]
        pr.inputs = [["aa"], ["bb"]]
        pr.inputDataPolicies = ["dl", "pr"]
        pr.events = [-1, -1]
        pr.bkQueries = ["Full", "fromPreviousProd"]
        pr.targets = ["Target1", "Target2"]
        pr.multicore = ["False", "True"]
        pr.processors = [2, 0]
        pr.outputModes = ["Local", "Any"]
        pr.ancestorDepths = [1, 0]
        pr._applyOptionalCorrections()
        prodsTypeListExpected = ["Merge", "Merge", "Merge", "Merge"]
        pluginsExpected = ["BySize", "BySize", "BySize", "ByRunFileTypeSizeWithFlush"]
        stepsListDictExpected = [mergeStepBHADRON, mergeStepCALIBRA, mergeStepPIDMDST, mergeStep]
        stepsInProdExpected = [[3], [4], [5], [6]]
        outputSEsExpected = ["Tier1-DST", "Tier1-DST", "Tier1-DST", "Tier1-M-DST"]
        prioritiesExpected = [1, 1, 1, 4]
        cpusExpected = [10, 10, 10, 100]
        groupSizesExpected = [1, 1, 1, 2]
        bkQueriesExpected = ["Full", "Full", "Full", "fromPreviousProd"]
        previousProdsExpected = [None, None, None, 1]
        removeInputsFlagExpected = [True, True, True, True]
        outputFileMasksExpected = ["", "", "", "dst"]
        outputFileStepsExpected = ["", "", "", "2"]
        inputsExpected = [["aa"], ["aa"], ["aa"], ["bb"]]
        inputDataPoliciesExpected = ["dl", "dl", "dl", "pr"]
        eventsExpected = [-1, -1, -1, -1]
        targetsExpected = ["Target1", "Target1", "Target1", "Target2"]
        multicoreExpected = ["False", "False", "False", "True"]
        processorsExpected = [2, 2, 2, 0]
        outputModeExpected = ["Local", "Local", "Local", "Any"]
        ancestorDepthsExpected = [1, 1, 1, 0]
        self.assertEqual(pr.prodsTypeList, prodsTypeListExpected)
        self.assertEqual(pr.plugins, pluginsExpected)
        self.assertEqual(pr.stepsListDict, stepsListDictExpected)
        self.assertEqual(pr.stepsInProds, stepsInProdExpected)
        self.assertEqual(pr.outputSEs, outputSEsExpected)
        self.assertEqual(pr.priorities, prioritiesExpected)
        self.assertEqual(pr.cpus, cpusExpected)
        self.assertEqual(pr.groupSizes, groupSizesExpected)
        self.assertEqual(pr.bkQueries, bkQueriesExpected)
        self.assertEqual(pr.previousProds, previousProdsExpected)
        self.assertEqual(pr.removeInputsFlags, removeInputsFlagExpected)
        self.assertEqual(pr.outputFileMasks, outputFileMasksExpected)
        self.assertEqual(pr.outputFileSteps, outputFileStepsExpected)
        self.assertEqual(pr.inputs, inputsExpected)
        self.assertEqual(pr.inputDataPolicies, inputDataPoliciesExpected)
        self.assertEqual(pr.events, eventsExpected)
        self.assertEqual(pr.targets, targetsExpected)
        self.assertEqual(pr.multicore, multicoreExpected)
        self.assertEqual(pr.processors, processorsExpected)
        self.assertEqual(pr.outputModes, outputModeExpected)
        self.assertEqual(pr.ancestorDepths, ancestorDepthsExpected)

        pr = ProductionRequest(self.bkClientFake, self.diracProdIn)
        pr.prodsTypeList = ["MCSimulation", "Merge"]
        pr.plugins = ["", "ByRunFileTypeSizeWithFlush"]
        pr.stepsListDict = [stepMC, mergeStep]
        pr.stepsList = [123, 456]
        pr.stepsInProds = [[1], [2]]
        pr.outputSEs = ["Tier1-DST", "Tier1-M-DST"]
        pr.priorities = [1, 4]
        pr.cpus = [10, 100]
        pr.groupSizes = [1, 2]
        pr.removeInputsFlags = [False, True]
        pr.outputFileMasks = ["", "dst"]
        pr.outputFileSteps = ["", "2"]
        pr.inputs = [[], []]
        pr.inputDataPolicies = ["", "dl"]
        pr.events = [100, -1]
        pr.bkQueries = ["", "fromPreviousProd"]
        pr.targets = ["Target1", "Target2"]
        pr.multicore = ["False", "True"]
        pr.processors = [2, 0]
        pr.outputModes = ["Local", "Any"]
        pr.ancestorDepths = [1, 0]
        pr._applyOptionalCorrections()
        prodsTypeListExpected = ["MCSimulation", "Merge"]
        pluginsExpected = ["", "ByRunFileTypeSizeWithFlush"]
        stepsListDictExpected = [stepMC, mergeStep]
        stepsInProdExpected = [[1], [2]]
        outputSEsExpected = ["Tier1-DST", "Tier1-M-DST"]
        prioritiesExpected = [1, 4]
        cpusExpected = [10, 100]
        groupSizesExpected = [1, 2]
        bkQueriesExpected = ["", "fromPreviousProd"]
        previousProdsExpected = [None, 1]
        removeInputsFlagExpected = [False, True]
        outputFileMasksExpected = ["", "dst"]
        outputFileStepsExpected = ["", "2"]
        inputsExpected = [[], []]
        inputDataPoliciesExpected = ["", "dl"]
        eventsExpected = [100, -1]
        targetsExpected = ["Target1", "Target2"]
        multicoreExpected = ["False", "True"]
        processorsExpected = [2, 0]
        outputModeExpected = ["Local", "Any"]
        ancestorDepthsExpected = [1, 0]
        self.assertEqual(pr.prodsTypeList, prodsTypeListExpected)
        self.assertEqual(pr.plugins, pluginsExpected)
        self.assertEqual(pr.stepsListDict, stepsListDictExpected)
        self.assertEqual(pr.stepsInProds, stepsInProdExpected)
        self.assertEqual(pr.outputSEs, outputSEsExpected)
        self.assertEqual(pr.priorities, prioritiesExpected)
        self.assertEqual(pr.cpus, cpusExpected)
        self.assertEqual(pr.groupSizes, groupSizesExpected)
        self.assertEqual(pr.bkQueries, bkQueriesExpected)
        self.assertEqual(pr.previousProds, previousProdsExpected)
        self.assertEqual(pr.removeInputsFlags, removeInputsFlagExpected)
        self.assertEqual(pr.outputFileMasks, outputFileMasksExpected)
        self.assertEqual(pr.outputFileSteps, outputFileStepsExpected)
        self.assertEqual(pr.inputs, inputsExpected)
        self.assertEqual(pr.inputDataPolicies, inputDataPoliciesExpected)
        self.assertEqual(pr.events, eventsExpected)
        self.assertEqual(pr.targets, targetsExpected)
        self.assertEqual(pr.multicore, multicoreExpected)
        self.assertEqual(pr.processors, processorsExpected)
        self.assertEqual(pr.outputModes, outputModeExpected)
        self.assertEqual(pr.ancestorDepths, ancestorDepthsExpected)

        pr = ProductionRequest(self.bkClientFake, self.diracProdIn)
        pr.prodsTypeList = ["MCSimulation", "Merge", "Merge"]
        pr.plugins = ["", "ByRunFileTypeSizeWithFlush", "RootMerging"]
        pr.stepsListDict = [stepMC, mergeStep, stepHistoMergingDict]
        pr.stepsList = [123, 456, 789]
        pr.stepsInProds = [[1], [2], [3]]
        pr.outputSEs = ["Tier1-DST", "Tier1-M-DST", "Tier1-M-DST"]
        pr.priorities = [1, 4, 5]
        pr.cpus = [10, 100, 100]
        pr.groupSizes = [1, 2, 3]
        pr.removeInputsFlags = [False, True, True]
        pr.outputFileMasks = ["", "dst", "root"]
        pr.outputFileSteps = ["", "2", "3"]
        pr.inputs = [[], [], []]
        pr.inputDataPolicies = ["", "dl", "dl"]
        pr.events = [100, -1, -1]
        pr.bkQueries = ["", "fromPreviousProd", "fromPreviousProd"]
        pr.targets = ["Target1", "Target2", "T3"]
        pr.multicore = ["False", "True", "True"]
        pr.processors = [2, 0, 0]
        pr.outputModes = ["Local", "Any", "Any"]
        pr.ancestorDepths = [1, 0, 0]
        pr._applyOptionalCorrections()
        prodsTypeListExpected = ["MCSimulation", "Merge", "Merge"]
        pluginsExpected = ["", "ByRunFileTypeSizeWithFlush", "RootMerging"]
        stepsListDictExpected = [stepMC, mergeStep, stepHistoMergingDict]
        stepsInProdExpected = [[1], [2], [3]]
        outputSEsExpected = ["Tier1-DST", "Tier1-M-DST", "Tier1-M-DST"]
        prioritiesExpected = [1, 4, 5]
        cpusExpected = [10, 100, 100]
        groupSizesExpected = [1, 2, 3]
        bkQueriesExpected = ["", "fromPreviousProd", "fromPreviousProd"]
        previousProdsExpected = [None, 1, 2]
        removeInputsFlagExpected = [False, True, True]
        outputFileMasksExpected = ["", "dst", "root"]
        outputFileStepsExpected = ["", "2", "3"]
        inputsExpected = [[], [], []]
        inputDataPoliciesExpected = ["", "dl", "dl"]
        eventsExpected = [100, -1, -1]
        targetsExpected = ["Target1", "Target2", "T3"]
        multicoreExpected = ["False", "True", "True"]
        processorsExpected = [2, 0, 0]
        outputModeExpected = ["Local", "Any", "Any"]
        ancestorDepthsExpected = [1, 0, 0]
        self.assertEqual(pr.prodsTypeList, prodsTypeListExpected)
        self.assertEqual(pr.plugins, pluginsExpected)
        self.assertEqual(pr.stepsListDict, stepsListDictExpected)
        self.assertEqual(pr.stepsInProds, stepsInProdExpected)
        self.assertEqual(pr.outputSEs, outputSEsExpected)
        self.assertEqual(pr.priorities, prioritiesExpected)
        self.assertEqual(pr.cpus, cpusExpected)
        self.assertEqual(pr.groupSizes, groupSizesExpected)
        self.assertEqual(pr.bkQueries, bkQueriesExpected)
        self.assertEqual(pr.previousProds, previousProdsExpected)
        self.assertEqual(pr.removeInputsFlags, removeInputsFlagExpected)
        self.assertEqual(pr.outputFileMasks, outputFileMasksExpected)
        self.assertEqual(pr.outputFileSteps, outputFileStepsExpected)
        self.assertEqual(pr.inputs, inputsExpected)
        self.assertEqual(pr.inputDataPolicies, inputDataPoliciesExpected)
        self.assertEqual(pr.events, eventsExpected)
        self.assertEqual(pr.targets, targetsExpected)
        self.assertEqual(pr.multicore, multicoreExpected)
        self.assertEqual(pr.processors, processorsExpected)
        self.assertEqual(pr.outputModes, outputModeExpected)
        self.assertEqual(pr.ancestorDepths, ancestorDepthsExpected)

    def test_getProdsDescriptionDict(self):
        pr = ProductionRequest(self.bkClientFake, self.diracProdIn)
        pr.stepsList = [123, 456, 456, 456, 789]
        pr.prodsTypeList = ["DataStripping", "Merge", "Merge", "Merge"]
        pr.removeInputsFlags = [False, True, True, True]
        pr.inputs = [[], [], [], []]
        pr.targets = ["", "", "", ""]
        pr.groupSizes = [1, 1, 2, 3]
        pr.inputDataPolicies = ["download", "download", "download", "download"]
        pr.outputFileMasks = ["", "", "", ""]
        pr.outputFileSteps = ["", "", "", ""]
        pr.stepsInProds = [[1, 2], [3], [4], [5]]
        pr.bkQueries = ["Full", "fromPreviousProd", "fromPreviousProd", "fromPreviousProd"]
        #     pr.outputSEs = ['Tier1-Buffer', 'Tier1-DST', 'Tier1-DST']
        #     pr.specialOutputSEs = [{}, {}, {}]
        pr.outputSEsPerFileType = [{"T1": "SE1"}, {"T1": "SE1"}, {"T1": "SE1"}, {"T1": "SE1"}]
        pr.priorities = [5, 8, 9, 9]
        pr.cpus = [1000000, 300000, 10000, 1000]
        pr.plugins = ["ByRun", "BySize", "BySize", "BySize"]
        pr.previousProds = [None, 1, 1, 1]
        pr.events = [-1, -1, -1, -1]
        pr.multicore = ["False", "False", "True", "True"]
        pr.processors = [(4, 4), (2, 2), (0, 2), (0, 0)]
        pr.outputModes = ["Any", "Local", "Any", "Any"]
        pr.ancestorDepths = [0, 0, 0, 0]

        pr.stepsListDict = [
            {
                "StepId": 123,
                "StepName": "Stripping14-Stripping",
                "ApplicationName": "DaVinci",
                "ApplicationVersion": "v2r2",
                "OptionFiles": "optsFiles",
                "Visible": "Yes",
                "ExtraPackages": "eps",
                "ProcessingPass": "procPass",
                "OptionsFormat": "",
                "DDDB": "",
                "CONDDB": "123456",
                "DQTag": "",
                "isMulticore": "False",
                "fileTypesIn": ["SDST"],
                "fileTypesOut": ["BHADRON.DST", "CALIBRATION.DST"],
            },
            {
                "StepId": 456,
                "StepName": "Merge",
                "ApplicationName": "LHCb",
                "ApplicationVersion": "v1r2",
                "OptionFiles": "optsFiles",
                "Visible": "Yes",
                "ExtraPackages": "eps",
                "ProcessingPass": "procPass",
                "OptionsFormat": "",
                "DDDB": "",
                "CONDDB": "123456",
                "DQTag": "",
                "isMulticore": "False",
                "prodStepID": "456['BHADRON.DST']",
                "fileTypesIn": ["BHADRON.DST"],
                "fileTypesOut": ["BHADRON.DST"],
            },
            {
                "StepId": 456,
                "StepName": "Merge",
                "ApplicationName": "LHCb",
                "ApplicationVersion": "v1r2",
                "OptionFiles": "optsFiles",
                "Visible": "Yes",
                "ExtraPackages": "eps",
                "ProcessingPass": "procPass",
                "OptionsFormat": "",
                "DDDB": "",
                "CONDDB": "123456",
                "DQTag": "",
                "isMulticore": "False",
                "prodStepID": "456['CALIBRATION.DST']",
                "fileTypesIn": ["CALIBRATION.DST"],
                "fileTypesOut": ["CALIBRATION.DST"],
            },
            {
                "StepId": 456,
                "StepName": "Merge",
                "ApplicationName": "LHCb",
                "ApplicationVersion": "v1r2",
                "OptionFiles": "optsFiles",
                "Visible": "Yes",
                "ExtraPackages": "eps",
                "ProcessingPass": "procPass",
                "OptionsFormat": "",
                "DDDB": "",
                "CONDDB": "123456",
                "DQTag": "",
                "isMulticore": "False",
                "prodStepID": "456['PID.MDST']",
                "fileTypesIn": ["PID.MDST"],
                "fileTypesOut": ["PID.MDST"],
            },
            {
                "StepId": 789,
                "StepName": "Merge",
                "ApplicationName": "Noether",
                "ApplicationVersion": "v1r2",
                "OptionFiles": "optsFiles",
                "Visible": "Yes",
                "ExtraPackages": "eps",
                "ProcessingPass": "procPass",
                "OptionsFormat": "",
                "DDDB": "",
                "CONDDB": "123456",
                "DQTag": "",
                "isMulticore": "False",
                "prodStepID": "789['DAVINCIHIST', 'BRUNELHIST']",
                "fileTypesIn": ["DAVINCIHIST", "BRUNELHIST"],
                "fileTypesOut": ["ROOT"],
            },
        ]
        res = pr._getProdsDescriptionDict()

        self.maxDiff = None
        self.assertEqual(res, prodsDict)

    def test__addStepsToProd(self):

        stepsInProd = [
            {
                "StepId": 123,
                "StepName": "Stripping14-Stripping",
                "ApplicationName": "DaVinci",
                "ApplicationVersion": "v2r2",
                "ExtraOptions": "",
                "OptionFiles": "optsFiles",
                "Visible": "Yes",
                "ExtraPackages": "eps",
                "ProcessingPass": "procPass",
                "OptionsFormat": "",
                "SystemConfig": "",
                "DDDB": "",
                "CONDDB": "123456",
                "DQTag": "",
                "isMulticore": "N",
                "prodStepID": "123['SDST']",
                "mcTCK": "",
                "visibilityFlag": [
                    {"Visibility": "N", "FileType": "BHADRON.DST"},
                    {"Visibility": "N", "FileType": "CALIBRATION.DST"},
                ],
                "fileTypesIn": ["SDST"],
                "fileTypesOut": ["BHADRON.DST", "CALIBRATION.DST"],
            },
            {
                "StepId": 456,
                "StepName": "Merge",
                "ApplicationName": "LHCb",
                "ApplicationVersion": "v1r2",
                "ExtraOptions": "",
                "OptionFiles": "optsFiles",
                "Visible": "Yes",
                "ExtraPackages": "eps",
                "ProcessingPass": "procPass",
                "OptionsFormat": "",
                "SystemConfig": "x86_64+avx2-centos7-gcc7-opt",
                "prodStepID": "456['BHADRON.DST', 'CALIBRATION.DST']",
                "DDDB": "",
                "CONDDB": "123456",
                "DQTag": "",
                "isMulticore": "N",
                "mcTCK": "",
                "visibilityFlag": [
                    {"Visibility": "Y", "FileType": "BHADRON.DST"},
                    {"Visibility": "Y", "FileType": "CALIBRATION.DST"},
                ],
                "fileTypesIn": ["BHADRON.DST", "CALIBRATION.DST"],
                "fileTypesOut": ["BHADRON.DST", "CALIBRATION.DST"],
            },
        ]

        pr = ProductionRequest(self.bkClientFake, self.diracProdIn)
        prod = Production()
        prod = pr._addStepsToProd(prod, stepsInProd, True)
        self.assertEqual(prod.gaudiSteps, ["DaVinci_1", "LHCb_2"])

    # def test__getStepsInProdDAG( self ):

    #   pr = ProductionRequest( self.bkClientFake, self.diracProdIn )
    #   # stepsListDict = {}
    #   # for prodDict in prodsDict.values():
    #   #   stepsInProdDAG = pr._getStepsInProdDAG(prodDict, stepsListDict)
    #   #   self.assertEqual(stepsInProdDAG.graph, {})

    #   stepsListDict = [step1Dict, mergeStepBHADRON]
    #   stepsInProdDAG = pr._getStepsInProdDAG(prodsDict[1], stepsListDict)

    #   self.assertEqual(
    #       stepsInProdDAG.graph,
    #       {frozenset([('DDDB', ''),
    #                   ('ExtraPackages', 'eps'),
    #                   ('OptionsFormat', ''),
    #                   ('visibilityFlag', frozenset([
    #                       {'Visible':'N', 'FileType': 'BHADRON.DST'},
    #                       {'Visible':'N', 'FileType': 'CALIBRATION.DST'},
    #                   ])),
    #                   ('fileTypesOut', frozenset(['CALIBRATION.DST', 'BHADRON.DST'])),
    #                   ('DQTag', ''),
    #                   ('CONDDB', '123456'),
    #                   ('mcTCK', ''),
    #                   ('ApplicationName', 'DaVinci'),
    #                   ('ApplicationVersion', 'v2r2'),
    #                   ('Visible', 'Yes'),
    #                   ('ProcessingPass', 'procPass'),
    #                   ('fileTypesIn', frozenset(['SDST'])),
    #                   ('isMulticore', 'N'),
    #                   ('SystemConfig', ''),
    #                   ('prodStepID', "123['SDST']"),
    #                   ('StepName', 'Stripping14-Stripping'),
    #                   ('StepId', 123),
    #                   ('OptionFiles', 'optsFiles'),
    #                   ('ExtraOptions', '')]): set([frozenset([
    #                       ('DDDB', 'head-20110302'),
    #                       ('ExtraPackages', 'AppConfig.v3r104'),
    #                       ('fileTypesOut', frozenset(['BHADRON.DST'])),
    #                       ('CONDDB', 'head-20110407'),
    #                       ('mcTCK', ''),
    #                       ('visibilityFlag', frozenset([''])),
    #                       ('ApplicationName', 'DaVinci'),
    #                       ('ApplicationVersion', 'v28r3p1'),
    #                       ('ProcessingPass', 'Merging'),
    #                       ('fileTypesIn', frozenset(['BHADRON.DST'])),
    #                       ('prodStepID', "456['BHADRON.DST']"),
    #                       ('StepName', 'Stripping14-Merging'),
    #                       ('StepId', 456),
    #                       ('SystemConfig', ''),
    #                       ('Usable', 'Yes'),
    #                       ('Visible', 'N'),
    #                       ('OptionFiles', '$APPCONFIGOPTS/Merging/DV-Stripping14-Merging.py')
    #                   ])]),
    #         frozenset([('DDDB', 'head-20110302'),
    #                   ('ExtraPackages', 'AppConfig.v3r104'),
    #                   ('fileTypesOut', frozenset(['BHADRON.DST'])),
    #                   ('CONDDB', 'head-20110407'),
    #                   ('mcTCK', ''),
    #                   ('visibilityFlag', frozenset([''])),
    #                   ('ApplicationName', 'DaVinci'),
    #                   ('ApplicationVersion', 'v28r3p1'),
    #                   ('ProcessingPass', 'Merging'),
    #                   ('fileTypesIn', frozenset(['BHADRON.DST'])),
    #                   ('prodStepID', "456['BHADRON.DST']"),
    #                   ('StepName', 'Stripping14-Merging'),
    #                   ('StepId', 456),
    #                   ('SystemConfig', ''),
    #                   ('Usable', 'Yes'),
    #                   ('Visible', 'N'),
    #                   ('OptionFiles', '$APPCONFIGOPTS/Merging/DV-Stripping14-Merging.py')]): set([]),
    #       }
    #     )

    def test__getBKKQuery(self):

        pr = ProductionRequest(self.bkClientFake, self.diracProdIn)
        pr.dataTakingConditions = "dataTC"
        pr.processingPass = "procePass"
        pr.dqFlag = "OK,AA, BB"
        pr.startRun = "123"
        pr.endRun = "456"
        res = pr._getBKKQuery()

        resExpected = {
            "DataTakingConditions": "dataTC",
            "ProcessingPass": "procePass",
            "FileType": "",
            "EventType": "",
            "ConfigName": "test",
            "ConfigVersion": "certification",
            "DataQualityFlag": "OK;;;AA;;;BB",
            "StartRun": 123,
            "EndRun": 456,
        }
        self.assertEqual(res, resExpected)

        pr = ProductionRequest(self.bkClientFake, self.diracProdIn)
        pr.dataTakingConditions = "dataTC"
        pr.processingPass = "procePass"
        pr.dqFlag = "OK,AA, BB"
        pr.bkFileType = ["type1", "type2"]
        pr.startRun = "123"
        pr.endRun = "456"
        res = pr._getBKKQuery()
        resExpected = {
            "DataTakingConditions": "dataTC",
            "ProcessingPass": "procePass",
            "FileType": "type1;;;type2",
            "EventType": "",
            "ConfigName": "test",
            "ConfigVersion": "certification",
            "DataQualityFlag": "OK;;;AA;;;BB",
            "StartRun": 123,
            "EndRun": 456,
        }
        self.assertEqual(res, resExpected)

        pr = ProductionRequest(self.bkClientFake, self.diracProdIn)
        pr.dataTakingConditions = "dataTC"
        pr.processingPass = "procePass"
        pr.dqFlag = "OK,AA, BB"
        pr.bkFileType = ["type1"]
        pr.startRun = "123"
        pr.endRun = "456"
        res = pr._getBKKQuery()
        resExpected = {
            "DataTakingConditions": "dataTC",
            "ProcessingPass": "procePass",
            "FileType": "type1",
            "EventType": "",
            "ConfigName": "test",
            "ConfigVersion": "certification",
            "DataQualityFlag": "OK;;;AA;;;BB",
            "StartRun": 123,
            "EndRun": 456,
        }
        self.assertEqual(res, resExpected)

        pr = ProductionRequest(self.bkClientFake, self.diracProdIn)
        pr.dataTakingConditions = "dataTC"
        pr.processingPass = "procePass"
        pr.dqFlag = "OK,AA, BB"
        pr.bkFileType = "type1"
        pr.startRun = "123"
        pr.endRun = "456"
        res = pr._getBKKQuery()
        resExpected = {
            "DataTakingConditions": "dataTC",
            "ProcessingPass": "procePass",
            "FileType": "type1",
            "EventType": "",
            "ConfigName": "test",
            "ConfigVersion": "certification",
            "DataQualityFlag": "OK;;;AA;;;BB",
            "StartRun": 123,
            "EndRun": 456,
        }
        self.assertEqual(res, resExpected)

        pr = ProductionRequest(self.bkClientFake, self.diracProdIn)
        pr.dataTakingConditions = "dataTC"
        pr.processingPass = "procePass"
        pr.dqFlag = "OK,AA, BB"
        pr.bkFileType = "type1, type2"
        pr.startRun = "123"
        pr.endRun = "456"
        res = pr._getBKKQuery()
        resExpected = {
            "DataTakingConditions": "dataTC",
            "ProcessingPass": "procePass",
            "FileType": "type1;;;type2",
            "EventType": "",
            "ConfigName": "test",
            "ConfigVersion": "certification",
            "DataQualityFlag": "OK;;;AA;;;BB",
            "StartRun": 123,
            "EndRun": 456,
        }
        self.assertEqual(res, resExpected)

        pr = ProductionRequest(self.bkClientFake, self.diracProdIn)
        pr.dqFlag = "OK,AA, BB"
        res = pr._getBKKQuery("fromPreviousProd", ["type"], 123)
        resExpected = {"ProductionID": 123, "FileType": "type", "DataQualityFlag": "OK;;;AA;;;BB"}
        self.assertEqual(res, resExpected)

        pr = ProductionRequest(self.bkClientFake, self.diracProdIn)
        pr.dqFlag = "OK,AA, BB"
        res = pr._getBKKQuery("fromPreviousProd", ["type"], 123)
        resExpected = {"ProductionID": 123, "FileType": "type", "DataQualityFlag": "OK;;;AA;;;BB"}
        self.assertEqual(res, resExpected)

        pr = ProductionRequest(self.bkClientFake, self.diracProdIn)
        pr.dqFlag = "OK,AA, BB"
        res = pr._getBKKQuery("fromPreviousProd", ["type1", "type2"], 123)
        resExpected = {"ProductionID": 123, "FileType": "type1;;;type2", "DataQualityFlag": "OK;;;AA;;;BB"}
        self.assertEqual(res, resExpected)

    def test__splitIntoProductionSteps(self):

        r_p = _splitIntoProductionSteps(stepStripp)
        r_exp = [
            {
                "ApplicationName": "DaVinci",
                "Usable": "Yes",
                "StepId": 123,
                "ApplicationVersion": "v28r3p1",
                "ExtraPackages": "AppConfig.v3r104",
                "StepName": "Stripping14-Merging",
                "SystemConfig": "",
                "ProcessingPass": "Merging",
                "Visible": "N",
                "DDDB": "head-20110302",
                "mcTCK": "",
                "OptionFiles": "$APPCONFIGOPTS/Merging/DV-Stripping14-Merging.py",
                "CONDDB": "head-20110407",
                "visibilityFlag": [],
                "fileTypesIn": ["SDST"],
                "fileTypesOut": ["BHADRON.DST", "CALIBRATION.DST", "CHARM.MDST", "CHARMCOMPLETEEVENT.DST"],
            }
        ]

        self.assertEqual(r_p, r_exp)

        r_p = _splitIntoProductionSteps(mergeStep)
        r_exp = [
            {
                "ApplicationName": "DaVinci",
                "Usable": "Yes",
                "StepId": 456,
                "ApplicationVersion": "v28r3p1",
                "ExtraPackages": "AppConfig.v3r104",
                "StepName": "Stripping14-Merging",
                "SystemConfig": "",
                "prodStepID": "456['BHADRON.DST']",
                "mcTCK": "",
                "ProcessingPass": "Merging",
                "Visible": "N",
                "DDDB": "head-20110302",
                "OptionFiles": "$APPCONFIGOPTS/Merging/DV-Stripping14-Merging.py",
                "CONDDB": "head-20110407",
                "visibilityFlag": [],
                "fileTypesIn": ["BHADRON.DST"],
                "fileTypesOut": ["BHADRON.DST"],
            },
            {
                "ApplicationName": "DaVinci",
                "Usable": "Yes",
                "StepId": 456,
                "ApplicationVersion": "v28r3p1",
                "ExtraPackages": "AppConfig.v3r104",
                "StepName": "Stripping14-Merging",
                "SystemConfig": "",
                "prodStepID": "456['CALIBRATION.DST']",
                "mcTCK": "",
                "ProcessingPass": "Merging",
                "Visible": "N",
                "DDDB": "head-20110302",
                "OptionFiles": "$APPCONFIGOPTS/Merging/DV-Stripping14-Merging.py",
                "CONDDB": "head-20110407",
                "visibilityFlag": [],
                "fileTypesIn": ["CALIBRATION.DST"],
                "fileTypesOut": ["CALIBRATION.DST"],
            },
            {
                "ApplicationName": "DaVinci",
                "Usable": "Yes",
                "StepId": 456,
                "ApplicationVersion": "v28r3p1",
                "ExtraPackages": "AppConfig.v3r104",
                "StepName": "Stripping14-Merging",
                "SystemConfig": "",
                "prodStepID": "456['PID.MDST']",
                "mcTCK": "",
                "ProcessingPass": "Merging",
                "Visible": "N",
                "DDDB": "head-20110302",
                "OptionFiles": "$APPCONFIGOPTS/Merging/DV-Stripping14-Merging.py",
                "CONDDB": "head-20110407",
                "visibilityFlag": [],
                "fileTypesIn": ["PID.MDST"],
                "fileTypesOut": ["PID.MDST"],
            },
        ]

        self.assertEqual(r_p, r_exp)


class ProductionRequestFailure(ClientTestCase):
    def test_resolveStepsFailure(self):
        pr = ProductionRequest(self.bkClientMock, self.diracProdIn)
        pr.stepsList = ["123"]
        self.bkClientMock.getAvailableSteps.return_value = {"OK": False, "Message": "error"}
        self.assertRaises(ValueError, pr.resolveSteps)

        self.bkClientMock.getStepInputFiles.return_value = {"OK": False, "Message": "error"}
        self.assertRaises(ValueError, pr.resolveSteps)


class ProductionRequestFullChain(ClientTestCase):
    def test_full(self):

        pr = ProductionRequest(self.bkClientFake, self.diracProdIn)
        pr.logger.setLevel("VERBOSE")

        stepsList = ["123"]
        stepsList.append("456")
        stepsList.append("")
        stepsList.append("")
        stepsList.append("")
        pr.stepsList = stepsList
        pr.compressionLvl = ["LOW"] * 4
        pr.outputVisFlag = [{"1": "N"}, {"2": "N"}]
        pr.resolveSteps()

        pr.appendName = "1"
        pr.configName = "MC"
        pr.configVersion = "MC11a"

        pr.events = ["100", "-1"]

        pr.eventsToProduce = 10000

        pr.eventType = "11124001"
        pr.parentRequestID = "34"
        pr.requestID = "35"

        pr.prodGroup = "Sim05/Trig0x40760037Flagged/Reco12a/Stripping17Flagged"
        pr.dataTakingConditions = "Beam3500GeV-2011-MagDown-Nu2-EmNoCuts"

        pr.prodsTypeList = ["Stripping", "Merge"]
        pr.outputSEs = ["Tier1_MC-DST", "Tier1_MC-DST"]
        pr.specialOutputSEs = [{}, {}]
        pr.stepsInProds = [range(1, len(pr.stepsList)), [len(pr.stepsList)]]
        pr.removeInputsFlags = [False, True]
        pr.priorities = [1, 6]
        pr.cpus = [1000, 100]
        pr.outputModes = ["Local", "Any"]
        pr.outputFileMasks = ["FOO", ""]
        pr.outputFileSteps = ["2", ""]
        pr.targets = ["Tier2", ""]
        pr.groupSizes = [1, 5]
        pr.plugins = ["", "BySize"]
        pr.inputDataPolicies = ["", "protocol"]
        pr.inputs = [[], []]

        res = pr.buildAndLaunchRequest()

        self.assertEqual(res, {"OK": True, "Value": [321, 321, 321]})


# ###########################################################################
# Test Suite run
# ###########################################################################


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ClientTestCase)
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(ProductionRequestSuccess))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(ProductionRequestFailure))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(ProductionRequestFullChain))
    testResult = unittest.TextTestRunner(verbosity=2).run(suite)

# EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#
