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
"""Unit tests for LHCbDIRAC utilities."""
# pylint: disable=protected-access,missing-docstring,invalid-name
import unittest
import itertools
import os
import datetime

from mock import MagicMock

from DIRAC import gLogger

from LHCbDIRAC.BookkeepingSystem.Client.test.mock_BookkeepingClient import bkc_mock

from LHCbDIRAC.Core.Utilities.ProductionData import (
    _makeProductionLFN,
    constructProductionLFNs,
    _getLFNRoot,
    _applyMask,
    getLogPath,
    constructUserLFNs,
)
from LHCbDIRAC.Core.Utilities.InputDataResolution import InputDataResolution
from LHCbDIRAC.Core.Utilities.GangaDataFile import GangaDataFile
from LHCbDIRAC.Core.Utilities.NagiosConnector import NagiosConnector

gConfigMock = MagicMock()
gConfigMock.getValue.return_value = "aValue"


class UtilitiesTestCase(unittest.TestCase):
    """Base class for the Utilities test cases."""

    def setUp(self):
        self.IDR = InputDataResolution({}, bkc_mock)
        gLogger.setLevel("DEBUG")

    def tearDown(self):
        for fileProd in ["data.py", "gaudi_extra_options.py"]:
            try:
                os.remove(fileProd)
            except OSError:
                continue


#################################################


class GangaDataFileSuccess(UtilitiesTestCase):
    def test_generateGangaDataFile(self):

        gdf = GangaDataFile()

        res = gdf.generateDataFile(["foo", "bar"], persistency="ROOT")
        # Remove first line as it contains the date and time
        res = "\n".join(res.split("\n")[1:])
        root = (
            "\n"
            + "from Gaudi.Configuration import * \n"
            + "from GaudiConf import IOHelper\nIOHelper('ROOT').inputFiles([\n"
            + "'LFN:foo',\n'LFN:bar',\n], clear=True)\n"
            + "\nFileCatalog().Catalogs += [ 'xmlcatalog_file:pool_xml_catalog.xml' ]\n"
        )
        self.assertEqual(res, root)

        res = gdf.generateDataFile(["foo", "bar"])
        # Remove first line as it contains the date and time
        res = "\n".join(res.split("\n")[1:])
        root = (
            "\n"
            + "from Gaudi.Configuration import * \n"
            + "from GaudiConf import IOHelper\nIOHelper().inputFiles([\n"
            + "'LFN:foo',\n'LFN:bar',\n], clear=True)\n"
            + "\nFileCatalog().Catalogs += [ 'xmlcatalog_file:pool_xml_catalog.xml' ]\n"
        )
        self.assertEqual(res, root)

        gdf = GangaDataFile(xmlcatalog_file="")

        res = gdf.generateDataFile(["foo", "bar"], persistency="MDF")
        # Remove first line as it contains the date and time
        res = "\n".join(res.split("\n")[1:])
        root = (
            "\n"
            + "from Gaudi.Configuration import * \n"
            + "from GaudiConf import IOHelper\nIOHelper('MDF').inputFiles([\n"
            + "'LFN:foo',\n'LFN:bar',\n], clear=True)\n"
        )
        self.assertEqual(res, root)

        res = gdf.generateDataFile("foo", persistency="ROOT")
        # Remove first line as it contains the date and time
        res = "\n".join(res.split("\n")[1:])
        root = (
            "\n"
            + "from Gaudi.Configuration import * \n"
            + "from GaudiConf import IOHelper\nIOHelper('ROOT').inputFiles([\n"
            + "'LFN:foo',\n], clear=True)\n"
        )
        self.assertEqual(res, root)


#################################################


class GangaDataFileFailure(UtilitiesTestCase):
    def test_generateDataFile(self):

        gdf = GangaDataFile()
        self.assertRaises(TypeError, gdf.generateDataFile, (""))
        self.assertRaises(ValueError, gdf.generateDataFile, ([]))


#################################################


class ProductionDataSuccess(UtilitiesTestCase):

    #################################################

    def test_constructProductionLFNs(self):

        # + test with InputData

        paramDict = {
            "PRODUCTION_ID": "12345",
            "JOB_ID": "54321",
            "configVersion": "test",
            "configName": "certification",
            "JobType": "MCSimulation",
            "outputList": [
                {"outputDataType": "sim", "outputDataSE": "Tier1-RDST", "outputDataName": "00012345_00054321_1.sim"},
                {"outputDataType": "digi", "outputDataSE": "Tier1-RDST", "outputDataName": "00012345_00054321_2.digi"},
                {
                    "outputDataType": "dst",
                    "outputDataSE": "Tier1_MC_M-DST",
                    "outputDataName": "00012345_00054321_4.dst",
                },
                {
                    "outputDataType": "ALLSTREAMS.DST",
                    "outputBKType": "ALLSTREAMS.DST",
                    "outputDataSE": "Tier1_MC_M-DST",
                    "outputDataName": "00012345_00054321_5.AllStreams.dst",
                },
            ],
        }

        AllStreamsDST = "/lhcb/certification/test/ALLSTREAMS.DST/00012345/0005/00012345_00054321_5.AllStreams.dst"
        reslist = [
            {
                "LogTargetPath": ["/lhcb/certification/test/LOG/00012345/0005/00012345_00054321.tar"],
                "LogFilePath": ["/lhcb/certification/test/LOG/00012345/0005/00054321"],
                "DebugLFNs": [
                    "/lhcb/debug/test/SIM/00012345/0005/00012345_00054321_1.sim",
                    "/lhcb/debug/test/DIGI/00012345/0005/00012345_00054321_2.digi",
                    "/lhcb/debug/test/DST/00012345/0005/00012345_00054321_4.dst",
                    "/lhcb/debug/test/ALLSTREAMS.DST/00012345/0005/00012345_00054321_5.AllStreams.dst",
                    "/lhcb/debug/test/CORE/00012345/0005/00054321_core",
                ],
                "BookkeepingLFNs": [
                    "/lhcb/certification/test/SIM/00012345/0005/00012345_00054321_1.sim",
                    "/lhcb/certification/test/DIGI/00012345/0005/00012345_00054321_2.digi",
                    "/lhcb/certification/test/DST/00012345/0005/00012345_00054321_4.dst",
                    AllStreamsDST,
                ],
                "ProductionOutputData": [
                    "/lhcb/certification/test/SIM/00012345/0005/00012345_00054321_1.sim",
                    "/lhcb/certification/test/DIGI/00012345/0005/00012345_00054321_2.digi",
                    "/lhcb/certification/test/DST/00012345/0005/00012345_00054321_4.dst",
                    AllStreamsDST,
                ],
            },
            {
                "LogTargetPath": ["/lhcb/certification/test/LOG/00012345/0005/00012345_00054321.tar"],
                "LogFilePath": ["/lhcb/certification/test/LOG/00012345/0005/00054321"],
                "DebugLFNs": [
                    "/lhcb/debug/test/SIM/00012345/0005/00012345_00054321_1.sim",
                    "/lhcb/debug/test/DIGI/00012345/0005/00012345_00054321_2.digi",
                    "/lhcb/debug/test/DST/00012345/0005/00012345_00054321_4.dst",
                    "/lhcb/debug/test/ALLSTREAMS.DST/00012345/0005/00012345_00054321_5.AllStreams.dst",
                    "/lhcb/debug/test/CORE/00012345/0005/00054321_core",
                ],
                "BookkeepingLFNs": [
                    "/lhcb/certification/test/SIM/00012345/0005/00012345_00054321_1.sim",
                    "/lhcb/certification/test/DIGI/00012345/0005/00012345_00054321_2.digi",
                    "/lhcb/certification/test/DST/00012345/0005/00012345_00054321_4.dst",
                    AllStreamsDST,
                ],
                "ProductionOutputData": ["/lhcb/certification/test/DST/00012345/0005/00012345_00054321_4.dst"],
            },
            {
                "LogTargetPath": ["/lhcb/certification/test/LOG/00012345/0005/00012345_00054321.tar"],
                "LogFilePath": ["/lhcb/certification/test/LOG/00012345/0005/00054321"],
                "DebugLFNs": [
                    "/lhcb/debug/test/SIM/00012345/0005/00012345_00054321_1.sim",
                    "/lhcb/debug/test/DIGI/00012345/0005/00012345_00054321_2.digi",
                    "/lhcb/debug/test/DST/00012345/0005/00012345_00054321_4.dst",
                    "/lhcb/debug/test/ALLSTREAMS.DST/00012345/0005/00012345_00054321_5.AllStreams.dst",
                    "/lhcb/debug/test/CORE/00012345/0005/00054321_core",
                ],
                "BookkeepingLFNs": [
                    "/lhcb/certification/test/SIM/00012345/0005/00012345_00054321_1.sim",
                    "/lhcb/certification/test/DIGI/00012345/0005/00012345_00054321_2.digi",
                    "/lhcb/certification/test/DST/00012345/0005/00012345_00054321_4.dst",
                    AllStreamsDST,
                ],
                "ProductionOutputData": ["/lhcb/certification/test/DST/00012345/0005/00012345_00054321_4.dst"],
            },
            {
                "LogTargetPath": ["/lhcb/certification/test/LOG/00012345/0005/00012345_00054321.tar"],
                "LogFilePath": ["/lhcb/certification/test/LOG/00012345/0005/00054321"],
                "DebugLFNs": [
                    "/lhcb/debug/test/SIM/00012345/0005/00012345_00054321_1.sim",
                    "/lhcb/debug/test/DIGI/00012345/0005/00012345_00054321_2.digi",
                    "/lhcb/debug/test/DST/00012345/0005/00012345_00054321_4.dst",
                    "/lhcb/debug/test/ALLSTREAMS.DST/00012345/0005/00012345_00054321_5.AllStreams.dst",
                    "/lhcb/debug/test/CORE/00012345/0005/00054321_core",
                ],
                "BookkeepingLFNs": [
                    "/lhcb/certification/test/SIM/00012345/0005/00012345_00054321_1.sim",
                    "/lhcb/certification/test/DIGI/00012345/0005/00012345_00054321_2.digi",
                    "/lhcb/certification/test/DST/00012345/0005/00012345_00054321_4.dst",
                    AllStreamsDST,
                ],
                "ProductionOutputData": [
                    "/lhcb/certification/test/DIGI/00012345/0005/00012345_00054321_2.digi",
                    "/lhcb/certification/test/DST/00012345/0005/00012345_00054321_4.dst",
                ],
            },
            {
                "LogTargetPath": ["/lhcb/certification/test/LOG/00012345/0005/00012345_00054321.tar"],
                "LogFilePath": ["/lhcb/certification/test/LOG/00012345/0005/00054321"],
                "DebugLFNs": [
                    "/lhcb/debug/test/SIM/00012345/0005/00012345_00054321_1.sim",
                    "/lhcb/debug/test/DIGI/00012345/0005/00012345_00054321_2.digi",
                    "/lhcb/debug/test/DST/00012345/0005/00012345_00054321_4.dst",
                    "/lhcb/debug/test/ALLSTREAMS.DST/00012345/0005/00012345_00054321_5.AllStreams.dst",
                    "/lhcb/debug/test/CORE/00012345/0005/00054321_core",
                ],
                "BookkeepingLFNs": [
                    "/lhcb/certification/test/SIM/00012345/0005/00012345_00054321_1.sim",
                    "/lhcb/certification/test/DIGI/00012345/0005/00012345_00054321_2.digi",
                    "/lhcb/certification/test/DST/00012345/0005/00012345_00054321_4.dst",
                    AllStreamsDST,
                ],
                "ProductionOutputData": [AllStreamsDST],
            },
            {
                "LogTargetPath": ["/lhcb/certification/test/LOG/00012345/0005/00012345_00054321.tar"],
                "LogFilePath": ["/lhcb/certification/test/LOG/00012345/0005/00054321"],
                "DebugLFNs": [
                    "/lhcb/debug/test/SIM/00012345/0005/00012345_00054321_1.sim",
                    "/lhcb/debug/test/DIGI/00012345/0005/00012345_00054321_2.digi",
                    "/lhcb/debug/test/DST/00012345/0005/00012345_00054321_4.dst",
                    "/lhcb/debug/test/ALLSTREAMS.DST/00012345/0005/00012345_00054321_5.AllStreams.dst",
                    "/lhcb/debug/test/CORE/00012345/0005/00054321_core",
                ],
                "BookkeepingLFNs": [
                    "/lhcb/certification/test/SIM/00012345/0005/00012345_00054321_1.sim",
                    "/lhcb/certification/test/DIGI/00012345/0005/00012345_00054321_2.digi",
                    "/lhcb/certification/test/DST/00012345/0005/00012345_00054321_4.dst",
                    AllStreamsDST,
                ],
                "ProductionOutputData": [
                    "/lhcb/certification/test/DST/00012345/0005/00012345_00054321_4.dst",
                    AllStreamsDST,
                ],
            },
        ]

        outputDataFileMasks = ("", "dst", "DST", ["digi", "dst"], "ALLSTREAMS.DST", ["dst", "allstreams.dst"])

        for outputDataFileMask, resL in zip(outputDataFileMasks, reslist):
            paramDict["outputDataFileMask"] = outputDataFileMask

            res = constructProductionLFNs(paramDict, bkc_mock)

            self.assertTrue(res["OK"])
            self.assertEqual(res["Value"], resL)

            resWithBkk = constructProductionLFNs(paramDict, bkc_mock, quick=False)

            self.assertTrue(resWithBkk["OK"])
            self.assertEqual(resWithBkk["Value"], resL)

    #################################################

    def test__makeProductionLFN(self):

        JOB_ID = "00054321"
        LFN_ROOT = "/lhcb/MC/MC10"
        filetuple = (("00012345_00054321_1.sim", "sim"), ("00012345_00054321_1.sim", "SIM"))
        prodstring = "00012345"

        for ft in filetuple:
            res = _makeProductionLFN(JOB_ID, LFN_ROOT, ft, prodstring)
            self.assertEqual(res, "/lhcb/MC/MC10/SIM/00012345/0005/00012345_00054321_1.sim")

    #################################################

    def test__applymask(self):

        dtl = [
            ("00012345_00054321_1.sim", "sim"),
            ("00012345_00054321_4.dst", "dst"),
            ("00012345_00054321_2.digi", "digi"),
            ("Brunel_00012345_00012345_1_Hist.root", "hist"),
            ("00012345_00054321_5.AllStreams.dst", "ALLSTREAMS.DST"),
        ]

        wfMask = ("", "dst", "ALLSTREAMS.DST", ["dst", "digi"], ["DIGI", "allstreams.dst"], "hist", ["dst", "hist"])

        dtlM = (
            [
                ("00012345_00054321_1.sim", "sim"),
                ("00012345_00054321_4.dst", "dst"),
                ("00012345_00054321_2.digi", "digi"),
                ("Brunel_00012345_00012345_1_Hist.root", "hist"),
                ("00012345_00054321_5.AllStreams.dst", "ALLSTREAMS.DST"),
            ],
            [("00012345_00054321_4.dst", "dst")],
            [("00012345_00054321_5.AllStreams.dst", "ALLSTREAMS.DST")],
            [("00012345_00054321_4.dst", "dst"), ("00012345_00054321_2.digi", "digi")],
            [("00012345_00054321_2.digi", "digi"), ("00012345_00054321_5.AllStreams.dst", "ALLSTREAMS.DST")],
            [("Brunel_00012345_00012345_1_Hist.root", "hist")],
            [("00012345_00054321_4.dst", "dst"), ("Brunel_00012345_00012345_1_Hist.root", "hist")],
        )

        for mask, res in zip(wfMask, dtlM):
            r = _applyMask(mask, dtl)

            self.assertEqual(r, res)

    def test_getLogPath(self):

        wkf_commons = {
            "PRODUCTION_ID": 12345,
            "JOB_ID": 0o0001,
            "configName": "LHCb",
            "configVersion": "Collision11",
            "JobType": "MCSimulation",
        }

        resWithBkk = getLogPath(wkf_commons, bkc_mock, quick=False)

        self.assertEqual(
            resWithBkk,
            {
                "OK": True,
                "Value": {
                    "LogTargetPath": ["/lhcb/LHCb/Collision11/LOG/00012345/0000/00012345_00000001.tar"],
                    "LogFilePath": ["/lhcb/LHCb/Collision11/LOG/00012345/0000/00000001"],
                },
            },
        )

        res = getLogPath(wkf_commons, bkc_mock)

        self.assertEqual(
            res,
            {
                "OK": True,
                "Value": {
                    "LogTargetPath": ["/lhcb/LHCb/Collision11/LOG/00012345/0000/00012345_00000001.tar"],
                    "LogFilePath": ["/lhcb/LHCb/Collision11/LOG/00012345/0000/00000001"],
                },
            },
        )

    def test__getLFNRoot(self):
        res = _getLFNRoot("/lhcb/data/CCRC08/00009909/DST/0000/00009909_00003456_2.dst", "MC12", bkClient=bkc_mock)
        self.assertEqual(res, "/lhcb/data/CCRC08/00009909/DST/0000/00009909_00003456_2.dst")

        res = _getLFNRoot(
            "/lhcb/data/CCRC08/00009909/DST/0000/00009909_00003456_2.dst", "MC12", bkClient=bkc_mock, quick=True
        )
        self.assertEqual(res, "/lhcb/data/CCRC08/00009909")

    def test_constructUserLFNs(self):
        timeTup = datetime.date.today().timetuple()
        yearMonth = "%s_%s" % (timeTup[0], str(timeTup[1]).zfill(2))

        res = constructUserLFNs(123, "fstagni", ["pippo.txt", "pluto.txt"])
        self.assertEqual(
            sorted(res),
            sorted(
                [
                    "/lhcb/user/f/fstagni/" + yearMonth + "/0/123/pluto.txt",
                    "/lhcb/user/f/fstagni/" + yearMonth + "/0/123/pippo.txt",
                ]
            ),
        )

        res = constructUserLFNs(123, "fstagni", ["pippo.txt", "pluto.txt"], "my/Output/Path")
        self.assertEqual(
            sorted(res),
            sorted(
                [
                    "/lhcb/user/f/fstagni/my/Output/Path/" + yearMonth + "/0/123/pluto.txt",
                    "/lhcb/user/f/fstagni/my/Output/Path/" + yearMonth + "/0/123/pippo.txt",
                ]
            ),
        )

        res = constructUserLFNs(123, "fstagni", ["pippo.txt", "pluto.txt"], prependString="pre/pend")
        self.assertEqual(
            sorted(res),
            sorted(
                [
                    "/lhcb/user/f/fstagni/" + yearMonth + "/123_pre/pend_pippo.txt",
                    "/lhcb/user/f/fstagni/" + yearMonth + "/123_pre/pend_pluto.txt",
                ]
            ),
        )

        res = constructUserLFNs(123, "fstagni", ["pippo.txt", "pluto.txt"], "my/Output/Path", "pre/pend")
        self.assertEqual(
            sorted(res),
            sorted(
                [
                    "/lhcb/user/f/fstagni/my/Output/Path/" + yearMonth + "/123_pre/pend_pippo.txt",
                    "/lhcb/user/f/fstagni/my/Output/Path/" + yearMonth + "/123_pre/pend_pluto.txt",
                ]
            ),
        )


class InputDataResolutionSuccess(UtilitiesTestCase):
    def test__addPfnType(self):

        res = self.IDR._addPfnType({"lfn1": {"mdata": "mdata1"}, "lfn2": {"mdata": "mdata2"}})
        self.assertEqual(
            res,
            {
                "OK": True,
                "Value": {
                    "lfn1": {"pfntype": "ROOT", "mdata": "mdata1"},
                    "lfn2": {"pfntype": "MDF", "mdata": "mdata2"},
                },
            },
        )

        bkc_mock.getFileTypeVersion.return_value = {"OK": True, "Value": {}}

        res = self.IDR._addPfnType({"lfn1": {"mdata": "mdata1"}, "lfn2": {"mdata": "mdata2"}})
        self.assertEqual(
            res,
            {
                "OK": True,
                "Value": {
                    "lfn1": {"pfntype": "ROOT", "mdata": "mdata1"},
                    "lfn2": {"pfntype": "ROOT", "mdata": "mdata2"},
                },
            },
        )

        bkc_mock.getFileTypeVersion.return_value = {"OK": True, "Value": {"lfn1": "ROOT"}}

        res = self.IDR._addPfnType(
            {"lfn1": {"mdata": "mdata1"}, "lfn2": {"mdata": "mdata2"}, "lfn3": {"mdata": "mdata3"}}
        )
        self.assertEqual(
            res,
            {
                "OK": True,
                "Value": {
                    "lfn1": {"pfntype": "ROOT", "mdata": "mdata1"},
                    "lfn2": {"pfntype": "ROOT", "mdata": "mdata2"},
                    "lfn3": {"pfntype": "ROOT", "mdata": "mdata3"},
                },
            },
        )


class NagiosConnectorSuccess(UtilitiesTestCase):
    def test_readConfig(self):

        nagConn = NagiosConnector()
        nagConn.readConfig()
        self.assertTrue(nagConn.config["MsgPort"])


#  def test_failedConnection( self ):
#
#    nagConn = NagiosConnector()
#    nagConn.readConfig()
#    nagConn.config['NagiosName'] = 'lhcb-Dirac.Unittest'
#    nagConn.useDebugMessage()
#    self.assertEqual( nagConn.initializeConnection(),
#                       S_OK( 'Connection to Broker established' ),
#                       'Connection not correctly initialized' )
#    self.assertEqual( nagConn.sendMessage(),
#                       S_OK('Message sent to Broker.'),
#                       'Sending unsuccessful!' )


#############################################################################
# Test Suite run
#############################################################################

if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(UtilitiesTestCase)
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(ProductionDataSuccess))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(InputDataResolutionSuccess))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(NagiosConnectorSuccess))
    testResult = unittest.TextTestRunner(verbosity=2).run(suite)
