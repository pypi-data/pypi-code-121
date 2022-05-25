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
"""Unit test of ConsistencyChecks."""
# pylint: disable=invalid-name,missing-docstring,protected-access

import unittest
from mock import Mock

from LHCbDIRAC.BookkeepingSystem.Client.test.mock_BookkeepingClient import bkc_mock
from LHCbDIRAC.DataManagementSystem.Client.ConsistencyChecks import ConsistencyChecks


class UtilitiesTestCase(unittest.TestCase):
    def setUp(self):

        self.dmMock = Mock()
        self.dmMock.getReplicas.return_value = {
            "OK": True,
            "Value": {"Successful": {"bb.raw": "metadataPippo"}, "Failed": {}},
        }

        self.cc = ConsistencyChecks(transClient=Mock(), dm=self.dmMock, bkClient=bkc_mock)
        self.fileTypes = [
            ["SEMILEPTONIC.DST", "LOG", "RAW"],
            ["SEMILEPTONIC.DST", "LOG", "RAW"],
            ["SEMILEPTONIC.DST"],
            ["SEMILEPTONIC.DST"],
        ]
        self.cc.fileTypesExcluded = ["LOG"]
        self.cc.prod = 0
        self.maxDiff = None

    def tearDown(self):
        pass


class ConsistencyChecksSuccess(UtilitiesTestCase):
    def test__selectByFileType(self):

        lfnDicts = [
            {
                "aa.raw": {
                    "bb.raw": {"FileType": "RAW", "RunNumber": 97019},
                    "bb.log": {"FileType": "LOG"},
                    "/bb/pippo/aa.dst": {"FileType": "DST"},
                    "/lhcb/1_2_1.Semileptonic.dst": {"FileType": "SEMILEPTONIC.DST"},
                },
                "cc.raw": {
                    "dd.raw": {"FileType": "RAW", "RunNumber": 97019},
                    "bb.log": {"FileType": "LOG"},
                    "/bb/pippo/aa.dst": {"FileType": "LOG"},
                    "/lhcb/1_1.semileptonic.dst": {"FileType": "SEMILEPTONIC.DST"},
                },
            },
            {"aa.raw": {"/bb/pippo/aa.dst": {"FileType": "LOG"}, "bb.log": {"FileType": "LOG"}}},
            {
                "aa.raw": {
                    "bb.raw": {"FileType": "RAW", "RunNumber": 97019},
                    "bb.log": {"FileType": "LOG"},
                    "/bb/pippo/aa.dst": {"FileType": "DST"},
                    "/lhcb/1_2_1.Semileptonic.dst": {"FileType": "SEMILEPTONIC.DST"},
                },
                "cc.raw": {
                    "dd.raw": {"FileType": "RAW", "RunNumber": 97019},
                    "bb.log": {"FileType": "LOG"},
                    "/bb/pippo/aa.dst": {"FileType": "LOG"},
                    "/lhcb/1_1.semileptonic.dst": {"FileType": "SEMILEPTONIC.DST"},
                },
            },
            {"aa.raw": {"/bb/pippo/aa.dst": {"FileType": "LOG"}, "bb.log": {"FileType": "LOG"}}},
        ]

        lfnDictsExpected = [
            {
                "aa.raw": {
                    "/lhcb/1_2_1.Semileptonic.dst": {"FileType": "SEMILEPTONIC.DST"},
                    "bb.log": {"FileType": "LOG"},
                    "bb.raw": {"RunNumber": 97019, "FileType": "RAW"},
                },
                "cc.raw": {
                    "dd.raw": {"RunNumber": 97019, "FileType": "RAW"},
                    "bb.log": {"FileType": "LOG"},
                    "/bb/pippo/aa.dst": {"FileType": "LOG"},
                    "/lhcb/1_1.semileptonic.dst": {"FileType": "SEMILEPTONIC.DST"},
                },
            },
            {"aa.raw": {"/bb/pippo/aa.dst": {"FileType": "LOG"}, "bb.log": {"FileType": "LOG"}}},
            {
                "aa.raw": {"/lhcb/1_2_1.Semileptonic.dst": {"FileType": "SEMILEPTONIC.DST"}},
                "cc.raw": {"/lhcb/1_1.semileptonic.dst": {"FileType": "SEMILEPTONIC.DST"}},
            },
            {},
        ]

        # testing various cases
        for fileType, lfnDict, lfnDictExpected in zip(self.fileTypes, lfnDicts, lfnDictsExpected):
            self.cc.fileType = fileType

            res = self.cc._selectByFileType(lfnDict)

            self.assertEqual(res, lfnDictExpected)

            res = self.cc._selectByFileType(lfnDict)
            self.assertEqual(res, lfnDictExpected)

    def test__getFileTypesCount(self):
        lfnDict = {"aa.raw": {"bb.log": {"FileType": "LOG"}, "/bb/pippo/aa.dst": {"FileType": "DST"}}}
        res = self.cc._getFileTypesCount(lfnDict)
        resExpected = {"aa.raw": {"DST": 1, "LOG": 1}}
        self.assertEqual(res, resExpected)

        lfnDict = {
            "aa.raw": {
                "bb.log": {"FileType": "LOG"},
                "/bb/pippo/aa.dst": {"FileType": "DST"},
                "/bb/pippo/cc.dst": {"FileType": "DST"},
            }
        }
        res = self.cc._getFileTypesCount(lfnDict)
        resExpected = {"aa.raw": {"DST": 2, "LOG": 1}}
        self.assertEqual(res, resExpected)

    def test_getDescendants(self):
        self.cc.fileType = ["SEMILEPTONIC.DST", "LOG", "RAW"]
        res = self.cc.getDescendants(["aa.raw"])
        (
            filesWithDescendants,
            filesWithoutDescendants,
            filesWitMultipleDescendants,
            descendants,
            inFCNotInBK,
            inBKNotInFC,
            removedFiles,
            inFailover,
        ) = res
        self.assertEqual(
            {k: set(v) for k, v in filesWithDescendants.items()},
            {"aa.raw": {"bb.log", "bb.raw"}},
        )
        self.assertEqual(filesWithoutDescendants, {})
        self.assertEqual(filesWitMultipleDescendants, {})
        self.assertEqual(descendants, ["bb.raw"])
        self.assertEqual(inFCNotInBK, [])
        self.assertEqual(inBKNotInFC, [])
        self.assertEqual(removedFiles, [])
        self.assertEqual(inFailover, [])


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(UtilitiesTestCase)
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(ConsistencyChecksSuccess))
    testResult = unittest.TextTestRunner(verbosity=2).run(suite)
