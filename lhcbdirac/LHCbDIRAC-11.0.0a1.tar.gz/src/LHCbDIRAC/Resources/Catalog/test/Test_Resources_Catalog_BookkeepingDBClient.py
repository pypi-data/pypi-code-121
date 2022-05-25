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
"""Test_Resources_Catalog_BookkeepingDBClient."""
# pylint: disable=protected-access, missing-docstring, invalid-name, line-too-long

import unittest
import mock

import six

from DIRAC import gLogger
import LHCbDIRAC.Resources.Catalog.BookkeepingDBClient as moduleTested

################################################################################


class BookkeepingDBClientt_TestCase(unittest.TestCase):
    def setUp(self):
        """Setup."""
        gLogger.setLevel("DEBUG")

        # # Mock external libraries / modules not interesting for the unit test
        # mock_pathFinder = mock.Mock()
        # mock_pathFinder.getServiceURL.return_value = 'cookiesURL'
        # self.mock_pathFinder = mock_pathFinder

        # Add mocks to moduleTested
        # moduleTested.PathFinder = self.mock_pathFinder

        mock_RPC = mock.Mock()
        mock_RPC.addFiles.return_value = {"OK": True, "Value": {"Successful": ["A"], "Failed": ["B"]}}
        mock_RPC.removeFiles.return_value = {"OK": True, "Value": {"Successful": ["A"], "Failed": ["B"]}}
        mock_RPC.exists.return_value = {"OK": True, "Value": {"A": 1, "B": 2}}
        mock_RPC.getFileMetadata.return_value = {
            "OK": True,
            "Value": {"Successful": {"A": {"FileSize": 1}, "B": {"FileSize": 2}}},
        }
        # mock_RPC.removeMigratingFiles.return_value    = {'OK': True}
        # mock_RPC.removeMigratingReplicas.return_value = {'OK': True}

        mock_BookkeepingClient = mock.Mock()
        mock_BookkeepingClient.return_value = mock_RPC
        self.mock_BookkeepingClient = mock_BookkeepingClient

        moduleTested.BookkeepingClient = self.mock_BookkeepingClient

        self.moduleTested = moduleTested
        self.testClass = self.moduleTested.BookkeepingDBClient

    def tearDown(self):
        """TearDown."""
        del self.testClass
        del self.moduleTested
        del self.mock_BookkeepingClient


################################################################################


class BookkeepingDBClient_Success(BookkeepingDBClientt_TestCase):
    def test_instantiate(self):
        """tests that we can instantiate one object of the tested class."""

        catalog = self.testClass()
        self.assertEqual("BookkeepingDBClient", catalog.__class__.__name__)

    def test_init(self):
        """tests that the init method does what it should do."""

        catalog = self.testClass()

        self.assertEqual(1000, catalog.splitSize)
        self.assertEqual("BookkeepingDB", catalog.name)

        catalog = self.testClass()
        self.assertEqual(1000, catalog.splitSize)
        self.assertEqual("BookkeepingDB", catalog.name)

    def test__setHasReplicaFlag(self):
        """test the output of __setHasReplicaFlag."""

        catalog = self.testClass()

        res = catalog._BookkeepingDBClient__setHasReplicaFlag([])
        self.assertEqual(True, res["OK"])
        self.assertEqual({"Successful": {}, "Failed": {}}, res["Value"])

        res = catalog._BookkeepingDBClient__setHasReplicaFlag(["A"])
        self.assertEqual(True, res["OK"])
        self.assertEqual({"Successful": {"A": True}, "Failed": {"B": "File does not exist"}}, res["Value"])

        res = catalog._BookkeepingDBClient__setHasReplicaFlag(["A", "B"])
        self.assertEqual(True, res["OK"])
        self.assertEqual({"Successful": {"A": True}, "Failed": {"B": "File does not exist"}}, res["Value"])

        res = catalog._BookkeepingDBClient__setHasReplicaFlag(["C"])
        self.assertEqual(True, res["OK"])
        self.assertEqual({"Successful": {"A": True}, "Failed": {"B": "File does not exist"}}, res["Value"])

        mock_RPC = mock.Mock()
        mock_RPC.addFiles.return_value = {"OK": False, "Message": "Bo!"}

        self.moduleTested.BookkeepingClient.return_value = mock_RPC

        catalog = self.testClass()

        res = catalog._BookkeepingDBClient__setHasReplicaFlag([])
        self.assertEqual(True, res["OK"])
        self.assertEqual({"Successful": {}, "Failed": {}}, res["Value"])

        res = catalog._BookkeepingDBClient__setHasReplicaFlag(["A"])
        self.assertEqual(True, res["OK"])
        self.assertEqual({"Successful": {}, "Failed": {"A": "Bo!"}}, res["Value"])

        res = catalog._BookkeepingDBClient__setHasReplicaFlag(["A", "B"])
        self.assertEqual(True, res["OK"])
        self.assertEqual({"Successful": {}, "Failed": {"A": "Bo!", "B": "Bo!"}}, res["Value"])

        res = catalog._BookkeepingDBClient__setHasReplicaFlag(["C"])
        self.assertEqual(True, res["OK"])
        self.assertEqual({"Successful": {}, "Failed": {"C": "Bo!"}}, res["Value"])

        mock_RPC = mock.Mock()
        # side_effect does not work very well, cooked a workaround
        _myValues = [{"OK": False, "Message": "Bo!"}, {"OK": True, "Value": {"A": 1, "B": 2}}]

        def _side_effect(_pfn):
            return _myValues.pop()

        mock_RPC.addFiles.side_effect = _side_effect
        # mock_RPC.addFiles.side_effect = [{'OK': True, 'Value': {'A': 1 , 'B': 2}},
        #                                  {'OK': False, 'Message': 'Bo!'}]

        self.moduleTested.BookkeepingClient.return_value = mock_RPC

        catalog = self.testClass()
        catalog.splitSize = 2

        res = catalog._BookkeepingDBClient__setHasReplicaFlag([])
        self.assertEqual(True, res["OK"])
        self.assertEqual({"Successful": {}, "Failed": {}}, res["Value"])

        _myValues = [{"OK": False, "Message": "Bo!"}, {"OK": True, "Value": {"Successful": ["A"], "Failed": []}}]

        res = catalog._BookkeepingDBClient__setHasReplicaFlag(["A", "C", "B"])
        self.assertEqual(True, res["OK"])
        self.assertEqual({"Successful": {"A": True}, "Failed": {"B": "Bo!"}}, res["Value"])

        # Restore the module
        self.moduleTested.BookkeepingClient.return_value = self.mock_BookkeepingClient
        six.moves.reload_module(self.moduleTested)

    def test__unsetHasReplicaFlag(self):
        """test the output of __unsetHasReplicaFlag."""

        catalog = self.testClass()

        res = catalog._BookkeepingDBClient__unsetHasReplicaFlag([])
        self.assertEqual(True, res["OK"])
        self.assertEqual({"Successful": {}, "Failed": {}}, res["Value"])

        res = catalog._BookkeepingDBClient__unsetHasReplicaFlag(["A"])
        self.assertEqual(True, res["OK"])
        self.assertEqual({"Successful": {"A": True}, "Failed": {"B": "File does not exist"}}, res["Value"])

        res = catalog._BookkeepingDBClient__unsetHasReplicaFlag(["A", "B"])
        self.assertEqual(True, res["OK"])
        self.assertEqual({"Successful": {"A": True}, "Failed": {"B": "File does not exist"}}, res["Value"])

        res = catalog._BookkeepingDBClient__unsetHasReplicaFlag(["C"])
        self.assertEqual(True, res["OK"])
        self.assertEqual({"Successful": {"A": True}, "Failed": {"B": "File does not exist"}}, res["Value"])

        mock_RPC = mock.Mock()
        mock_RPC.removeFiles.return_value = {"OK": False, "Message": "Bo!"}

        self.moduleTested.BookkeepingClient.return_value = mock_RPC

        catalog = self.testClass()

        res = catalog._BookkeepingDBClient__unsetHasReplicaFlag([])
        self.assertEqual(True, res["OK"])
        self.assertEqual({"Successful": {}, "Failed": {}}, res["Value"])

        res = catalog._BookkeepingDBClient__unsetHasReplicaFlag(["A"])
        self.assertEqual(True, res["OK"])
        self.assertEqual({"Successful": {}, "Failed": {"A": "Bo!"}}, res["Value"])

        res = catalog._BookkeepingDBClient__unsetHasReplicaFlag(["A", "B"])
        self.assertEqual(True, res["OK"])
        self.assertEqual({"Successful": {}, "Failed": {"A": "Bo!", "B": "Bo!"}}, res["Value"])

        res = catalog._BookkeepingDBClient__unsetHasReplicaFlag(["C"])
        self.assertEqual(True, res["OK"])
        self.assertEqual({"Successful": {}, "Failed": {"C": "Bo!"}}, res["Value"])

        mock_RPC = mock.Mock()
        # side_effect does not work very well, cooked a workaround
        _myValues = [{"OK": False, "Message": "Bo!"}, {"OK": True, "Value": {"Successful": [], "Failed": ["A", "B"]}}]

        def _side_effect(_pfn):
            return _myValues.pop()

        mock_RPC.removeFiles.side_effect = _side_effect
        # mock_RPC.removeFiles.side_effect = [{'OK': True, 'Value': {'A': 1 , 'B': 2}},
        #                                     {'OK': False, 'Message': 'Bo!'}]

        self.moduleTested.BookkeepingClient.return_value = mock_RPC

        catalog = self.testClass()
        catalog.splitSize = 2

        res = catalog._BookkeepingDBClient__unsetHasReplicaFlag([])
        self.assertEqual(True, res["OK"])
        self.assertEqual({"Successful": {}, "Failed": {}}, res["Value"])

        res = catalog._BookkeepingDBClient__unsetHasReplicaFlag(["A", "C", "B"])
        self.assertEqual(True, res["OK"])
        self.assertEqual({"Successful": {}, "Failed": {"A": "File does not exist", "B": "Bo!"}}, res["Value"])

        # Restore the module
        self.moduleTested.BookkeepingClient.return_value = self.mock_BookkeepingClient
        six.moves.reload_module(self.moduleTested)

    def test__exists(self):
        """tests the output of __exists."""

        catalog = self.testClass()

        res = catalog._BookkeepingDBClient__exists([])
        self.assertEqual(True, res["OK"])
        self.assertEqual({"Successful": {}, "Failed": {}}, res["Value"])

        res = catalog._BookkeepingDBClient__exists(["A", "B"])
        self.assertEqual(True, res["OK"])
        self.assertEqual({"Successful": {"A": 1, "B": 2}, "Failed": {}}, res["Value"])

        res = catalog._BookkeepingDBClient__exists(["C"])
        self.assertEqual(True, res["OK"])
        self.assertEqual({"Successful": {"A": 1, "B": 2}, "Failed": {}}, res["Value"])

        mock_RPC = mock.Mock()
        mock_RPC.exists.return_value = {"OK": False, "Message": "Bo!"}

        self.moduleTested.BookkeepingClient.return_value = mock_RPC

        catalog = self.testClass()

        res = catalog._BookkeepingDBClient__exists([])
        self.assertEqual(True, res["OK"])
        self.assertEqual({"Successful": {}, "Failed": {}}, res["Value"])

        res = catalog._BookkeepingDBClient__exists(["A"])
        self.assertEqual(True, res["OK"])
        self.assertEqual({"Successful": {}, "Failed": {"A": "Bo!"}}, res["Value"])

        res = catalog._BookkeepingDBClient__exists(["A", "B"])
        self.assertEqual(True, res["OK"])
        self.assertEqual({"Successful": {}, "Failed": {"A": "Bo!", "B": "Bo!"}}, res["Value"])

        res = catalog._BookkeepingDBClient__exists(["C"])
        self.assertEqual(True, res["OK"])
        self.assertEqual({"Successful": {}, "Failed": {"C": "Bo!"}}, res["Value"])

        mock_RPC = mock.Mock()

        # side_effect does not work very well, cooked a workaround
        _myValues = [{"OK": False, "Message": "Bo!"}, {"OK": True, "Value": {"A": 1, "B": 2}}]

        def _side_effect(_pfn):
            return _myValues.pop()

        mock_RPC.exists.side_effect = _side_effect
        # mock_RPC.exists.side_effect = [{'OK': True, 'Value': {'A': 1 , 'B': 2}},
        #                                {'OK': False, 'Message': 'Bo!'}]

        self.moduleTested.BookkeepingClient.return_value = mock_RPC

        catalog = self.testClass()
        catalog.splitSize = 2

        res = catalog._BookkeepingDBClient__exists([])
        self.assertEqual(True, res["OK"])
        self.assertEqual({"Successful": {}, "Failed": {}}, res["Value"])

        _myValues = [{"OK": False, "Message": "Bo!"}, {"OK": True, "Value": {"A": 1, "B": 2}}]

        res = catalog._BookkeepingDBClient__exists(["A", "C", "B"])
        self.assertEqual(True, res["OK"])
        self.assertEqual({"Successful": {"A": 1, "B": 2}, "Failed": {"B": "Bo!"}}, res["Value"])

        # Restore the module
        self.moduleTested.BookkeepingClient.return_value = self.mock_BookkeepingClient
        six.moves.reload_module(self.moduleTested)

    def test__getFileMetadata(self):
        """tests the output of __getFileMetadata."""

        catalog = self.testClass()

        res = catalog._BookkeepingDBClient__getFileMetadata(["A", "B"])
        self.assertEqual(True, res["OK"])
        self.assertEqual({"Successful": {"A": {"FileSize": 1}, "B": {"FileSize": 2}}, "Failed": {}}, res["Value"])

        res = catalog._BookkeepingDBClient__getFileMetadata(["A", "B"])
        self.assertEqual(True, res["OK"])
        self.assertEqual({"Successful": {"A": {"FileSize": 1}, "B": {"FileSize": 2}}, "Failed": {}}, res["Value"])

        res = catalog._BookkeepingDBClient__getFileMetadata(["C"])
        self.assertEqual(True, res["OK"])
        self.assertEqual(
            {"Successful": {"A": {"FileSize": 1}, "B": {"FileSize": 2}}, "Failed": {"C": "File does not exist"}},
            res["Value"],
        )

        mock_RPC = mock.Mock()
        mock_RPC.getFileMetadata.return_value = {"OK": True, "Value": {"Successful": {"A": "1", "B": "2"}}}

        self.moduleTested.BookkeepingClient.return_value = mock_RPC

        catalog = self.testClass()

        res = catalog._BookkeepingDBClient__getFileMetadata(["A", "B"])
        self.assertEqual(True, res["OK"])
        self.assertEqual({"Successful": {}, "Failed": {"A": "1", "B": "2"}}, res["Value"])

        res = catalog._BookkeepingDBClient__getFileMetadata(["C"])
        self.assertEqual(True, res["OK"])
        self.assertEqual({"Successful": {}, "Failed": {"A": "1", "B": "2", "C": "File does not exist"}}, res["Value"])

        mock_RPC = mock.Mock()
        mock_RPC.getFileMetadata.return_value = {"OK": False, "Message": "Bo!"}

        self.moduleTested.BookkeepingClient.return_value = mock_RPC

        catalog = self.testClass()

        res = catalog._BookkeepingDBClient__getFileMetadata(["A"])
        self.assertEqual(True, res["OK"])
        self.assertEqual({"Successful": {}, "Failed": {"A": "Bo!"}}, res["Value"])

        res = catalog._BookkeepingDBClient__getFileMetadata(["A", "B"])
        self.assertEqual(True, res["OK"])
        self.assertEqual({"Successful": {}, "Failed": {"A": "Bo!", "B": "Bo!"}}, res["Value"])

        mock_RPC = mock.Mock()

        # side_effect does not work very well, cooked a workaround
        _myValues = [{"OK": False, "Message": "Bo!"}, {"OK": True, "Value": {"Successful": {"A": 1, "B": 2}}}]

        def _side_effect(_pfn):
            return _myValues.pop()

        mock_RPC.getFileMetadata.side_effect = _side_effect
        # mock_RPC.getFileMetadata.side_effect = [{'OK': True, 'Value': {'A': 1 , 'B': 2}},
        #                                         {'OK': False, 'Message': 'Bo!'}]

        self.moduleTested.BookkeepingClient.return_value = mock_RPC

        catalog = self.testClass()
        catalog.splitSize = 2

        res = catalog._BookkeepingDBClient__getFileMetadata(["A", "C", "B"])
        self.assertEqual(True, res["OK"])
        self.assertEqual(
            {"Successful": {"A": 1, "B": 2}, "Failed": {"C": "File does not exist", "B": "Bo!"}}, res["Value"]
        )

        mock_RPC = mock.Mock()
        mock_RPC.getFileMetadata.return_value = {"OK": True, "Value": {"Successful": {"A": str, "B": "2"}}}

        self.moduleTested.BookkeepingClient.return_value = mock_RPC

        catalog = self.testClass()

        res = catalog._BookkeepingDBClient__getFileMetadata(["A", "B"])
        self.assertEqual(True, res["OK"])
        self.assertEqual({"Successful": {"A": str}, "Failed": {"B": "2"}}, res["Value"])

        # Restore the module
        self.moduleTested.BookkeepingClient.return_value = self.mock_BookkeepingClient
        six.moves.reload_module(self.moduleTested)

    def test_addFile(self):
        """tests the output of addFile."""

        catalog = self.testClass()

        res = catalog.addFile(1)
        self.assertEqual(False, res["OK"])

        res = catalog.addFile([])
        self.assertEqual(False, res["OK"])

        res = catalog.addFile({})
        self.assertEqual(False, res["OK"])

        res = catalog.addFile(["path"])
        self.assertEqual(True, res["OK"])
        self.assertEqual({"Successful": {"A": True}, "Failed": {"B": "File does not exist"}}, res["Value"])

        res = catalog.addFile(["A"])
        self.assertEqual(True, res["OK"])
        self.assertEqual({"Successful": {"A": True}, "Failed": {"B": "File does not exist"}}, res["Value"])

        res = catalog.addFile(["A", "path"])
        self.assertEqual(True, res["OK"])
        self.assertEqual({"Successful": {"A": True}, "Failed": {"B": "File does not exist"}}, res["Value"])

    def test_addReplica(self):
        """tests the output of addReplica."""

        catalog = self.testClass()

        res = catalog.addReplica(1)
        self.assertEqual(False, res["OK"])

        res = catalog.addReplica([])
        self.assertEqual(False, res["OK"])

        res = catalog.addReplica({})
        self.assertEqual(False, res["OK"])

        res = catalog.addReplica(["path"])
        self.assertEqual(True, res["OK"])
        self.assertEqual({"Successful": {"A": True}, "Failed": {"B": "File does not exist"}}, res["Value"])

        res = catalog.addReplica(["A"])
        self.assertEqual(True, res["OK"])
        self.assertEqual({"Successful": {"A": True}, "Failed": {"B": "File does not exist"}}, res["Value"])

        res = catalog.addReplica(["A", "path"])
        self.assertEqual(True, res["OK"])
        self.assertEqual({"Successful": {"A": True}, "Failed": {"B": "File does not exist"}}, res["Value"])

    def test_removeFile(self):
        """tests the output of removeFile."""

        catalog = self.testClass()

        res = catalog.removeFile(1)
        self.assertEqual(False, res["OK"])

        res = catalog.removeFile([])
        self.assertEqual(False, res["OK"])

        res = catalog.removeFile({})
        self.assertEqual(False, res["OK"])

        res = catalog.removeFile(["A", "B", "C"])
        self.assertEqual(True, res["OK"])
        self.assertEqual({"Successful": {"A": True}, "Failed": {"B": "File does not exist"}}, res["Value"])

        res = catalog.removeFile({"A": 1, "B": 2, "C": 3})
        self.assertEqual(True, res["OK"])
        self.assertEqual({"Successful": {"A": True}, "Failed": {"B": "File does not exist"}}, res["Value"])

        # FIXME: to be continued, but the method is quite tangled to be tested
        # on a rational way

    def test_removeReplica(self):
        """tests the output of removeReplica."""

        catalog = self.testClass()

        res = catalog.removeReplica(1)
        self.assertEqual(False, res["OK"])

        res = catalog.removeReplica([])
        self.assertEqual(False, res["OK"])

        res = catalog.removeReplica({})
        self.assertEqual(False, res["OK"])

        res = catalog.removeReplica(["path"])
        self.assertEqual(True, res["OK"])
        self.assertEqual({"Successful": {"path": True}, "Failed": {}}, res["Value"])

        res = catalog.removeReplica(["A", "B", "path"])
        self.assertEqual(True, res["OK"])
        self.assertEqual({"Successful": {"path": True, "A": True, "B": True}, "Failed": {}}, res["Value"])

        res = catalog.removeReplica({"A": 2, "C": 3})
        self.assertEqual(True, res["OK"])
        self.assertEqual({"Successful": {"A": 1, "C": True}, "Failed": {}}, res["Value"])

    def test_setReplicaStatus(self):
        """tests the output of setReplicaStatus."""

        catalog = self.testClass()

        res = catalog.setReplicaStatus(1)
        self.assertEqual(False, res["OK"])

        res = catalog.setReplicaStatus([])
        self.assertEqual(False, res["OK"])

        res = catalog.setReplicaStatus({})
        self.assertEqual(False, res["OK"])

        res = catalog.setReplicaStatus(["path"])
        self.assertEqual(True, res["OK"])
        self.assertEqual({"Successful": {"path": True}, "Failed": {}}, res["Value"])

        res = catalog.setReplicaStatus(["A", "B", "path"])
        self.assertEqual(True, res["OK"])
        self.assertEqual({"Successful": {"path": True, "A": True, "B": True}, "Failed": {}}, res["Value"])

        res = catalog.setReplicaStatus({"A": 2, "C": 3})
        self.assertEqual(True, res["OK"])
        self.assertEqual({"Successful": {"A": 1, "C": True}, "Failed": {}}, res["Value"])

    def test_setReplicaHost(self):
        """tests the output of setReplicaHost."""

        catalog = self.testClass()

        res = catalog.setReplicaHost(1)
        self.assertEqual(False, res["OK"])

        res = catalog.setReplicaHost([])
        self.assertEqual(False, res["OK"])

        res = catalog.setReplicaHost({})
        self.assertEqual(False, res["OK"])

        res = catalog.setReplicaHost(["path"])
        self.assertEqual(True, res["OK"])
        self.assertEqual({"Successful": {"path": True}, "Failed": {}}, res["Value"])

        res = catalog.setReplicaHost(["A", "B", "path"])
        self.assertEqual(True, res["OK"])
        self.assertEqual({"Successful": {"path": True, "A": True, "B": True}, "Failed": {}}, res["Value"])

        res = catalog.setReplicaHost({"A": 2, "C": 3})
        self.assertEqual(True, res["OK"])
        self.assertEqual({"Successful": {"A": 1, "C": True}, "Failed": {}}, res["Value"])

    def test_removeDirectory(self):
        """tests the output of removeDirectory."""

        catalog = self.testClass()

        res = catalog.removeDirectory(1)
        self.assertEqual(False, res["OK"])

        res = catalog.removeDirectory([])
        self.assertEqual(False, res["OK"])

        res = catalog.removeDirectory({})
        self.assertEqual(False, res["OK"])

        res = catalog.removeDirectory(["path"])
        self.assertEqual(True, res["OK"])
        self.assertEqual({"Successful": {"path": True}, "Failed": {}}, res["Value"])

        res = catalog.removeDirectory(["A", "B", "path"])
        self.assertEqual(True, res["OK"])
        self.assertEqual({"Successful": {"path": True, "A": True, "B": True}, "Failed": {}}, res["Value"])

        res = catalog.removeDirectory({"A": 2, "C": 3})
        self.assertEqual(True, res["OK"])
        self.assertEqual({"Successful": {"A": 1, "C": True}, "Failed": {}}, res["Value"])

    def test_createDirectory(self):
        """tests the output of createDirectory."""

        catalog = self.testClass()

        res = catalog.createDirectory(1)
        self.assertEqual(False, res["OK"])

        res = catalog.createDirectory([])
        self.assertEqual(False, res["OK"])

        res = catalog.createDirectory({})
        self.assertEqual(False, res["OK"])

        res = catalog.createDirectory(["path"])
        self.assertEqual(True, res["OK"])
        self.assertEqual({"Successful": {"path": True}, "Failed": {}}, res["Value"])

        res = catalog.createDirectory(["A", "B", "path"])
        self.assertEqual(True, res["OK"])
        self.assertEqual({"Successful": {"path": True, "A": True, "B": True}, "Failed": {}}, res["Value"])

        res = catalog.createDirectory({"A": 2, "C": 3})
        self.assertEqual(True, res["OK"])
        self.assertEqual({"Successful": {"A": 1, "C": True}, "Failed": {}}, res["Value"])

    def test_removeLink(self):
        """tests the output of createDirectory."""

        catalog = self.testClass()

        res = catalog.removeLink(1)
        self.assertEqual(False, res["OK"])

        res = catalog.removeLink([])
        self.assertEqual(False, res["OK"])

        res = catalog.removeLink({})
        self.assertEqual(False, res["OK"])

        res = catalog.removeLink(["path"])
        self.assertEqual(True, res["OK"])
        self.assertEqual({"Successful": {"path": True}, "Failed": {}}, res["Value"])

        res = catalog.removeLink(["A", "B", "path"])
        self.assertEqual(True, res["OK"])
        self.assertEqual({"Successful": {"path": True, "A": True, "B": True}, "Failed": {}}, res["Value"])

        res = catalog.removeLink({"A": 2, "C": 3})
        self.assertEqual(True, res["OK"])
        self.assertEqual({"Successful": {"A": 1, "C": True}, "Failed": {}}, res["Value"])

    def test_createLink(self):
        """tests the output of createDirectory."""

        catalog = self.testClass()

        res = catalog.createLink(1)
        self.assertEqual(False, res["OK"])

        res = catalog.createLink([])
        self.assertEqual(False, res["OK"])

        res = catalog.createLink({})
        self.assertEqual(False, res["OK"])

        res = catalog.createLink(["path"])
        self.assertEqual(True, res["OK"])
        self.assertEqual({"Successful": {"path": True}, "Failed": {}}, res["Value"])

        res = catalog.createLink(["A", "B", "path"])
        self.assertEqual(True, res["OK"])
        self.assertEqual({"Successful": {"path": True, "A": True, "B": True}, "Failed": {}}, res["Value"])

        res = catalog.createLink({"A": 2, "C": 3})
        self.assertEqual(True, res["OK"])
        self.assertEqual({"Successful": {"A": 1, "C": True}, "Failed": {}}, res["Value"])

    def test_exists(self):
        """tests the output of exists."""

        catalog = self.testClass()

        res = catalog.exists(1)
        self.assertEqual(False, res["OK"])

        res = catalog.exists([])
        self.assertEqual(False, res["OK"])

        res = catalog.exists({})
        self.assertEqual(False, res["OK"])

        res = catalog.exists(["path"])
        self.assertEqual(True, res["OK"])
        self.assertEqual({"Successful": {"A": 1, "B": 2}, "Failed": {}}, res["Value"])

        res = catalog.exists(["A", "B", "path"])
        self.assertEqual(True, res["OK"])
        self.assertEqual({"Successful": {"A": 1, "B": 2}, "Failed": {}}, res["Value"])

        res = catalog.exists({"A": 2, "C": 3})
        self.assertEqual(True, res["OK"])
        self.assertEqual({"Successful": {"A": 1, "B": 2}, "Failed": {}}, res["Value"])

    def test_getFileMetadata(self):
        """tests the output of getFileMetadata."""

        catalog = self.testClass()

        res = catalog.getFileMetadata(1)
        self.assertEqual(False, res["OK"])

        res = catalog.getFileMetadata([])
        self.assertEqual(False, res["OK"])

        res = catalog.getFileMetadata({})
        self.assertEqual(False, res["OK"])

        res = catalog.getFileMetadata(["path"])
        self.assertEqual(True, res["OK"])
        self.assertEqual(
            {"Successful": {"A": {"FileSize": 1}, "B": {"FileSize": 2}}, "Failed": {"path": "File does not exist"}},
            res["Value"],
        )

        res = catalog.getFileMetadata(["A", "B", "path"])
        self.assertEqual(True, res["OK"])
        self.assertEqual(
            {"Successful": {"A": {"FileSize": 1}, "B": {"FileSize": 2}}, "Failed": {"path": "File does not exist"}},
            res["Value"],
        )

        res = catalog.getFileMetadata({"A": 2, "C": 3})
        self.assertEqual(True, res["OK"])
        self.assertEqual(
            {"Successful": {"A": {"FileSize": 1}, "B": {"FileSize": 2}}, "Failed": {"C": "File does not exist"}},
            res["Value"],
        )

    def test_getFileSize(self):
        """tests the output of getFileSize."""

        catalog = self.testClass()

        res = catalog.getFileSize(1)
        self.assertEqual(False, res["OK"])

        res = catalog.getFileSize([])
        self.assertEqual(False, res["OK"])

        res = catalog.getFileSize({})
        self.assertEqual(False, res["OK"])

        res = catalog.getFileSize(["path"])
        self.assertEqual(True, res["OK"])
        self.assertEqual({"Successful": {"A": 1, "B": 2}, "Failed": {"path": "File does not exist"}}, res["Value"])

        res = catalog.getFileSize(["A", "B", "path"])
        self.assertEqual(True, res["OK"])
        self.assertEqual({"Successful": {"A": 1, "B": 2}, "Failed": {"path": "File does not exist"}}, res["Value"])

        res = catalog.getFileSize({"A": 2, "C": 3})
        self.assertEqual(True, res["OK"])
        self.assertEqual({"Successful": {"A": 1, "B": 2}, "Failed": {"C": "File does not exist"}}, res["Value"])


#################################################################################
