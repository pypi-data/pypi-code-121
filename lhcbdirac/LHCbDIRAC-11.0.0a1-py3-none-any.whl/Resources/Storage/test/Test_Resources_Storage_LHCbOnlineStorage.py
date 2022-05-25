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
"""Test_Resources_Storage_LHCbOnlineStorage."""
import mock
import unittest

import LHCbDIRAC.Resources.Storage.LHCbOnlineStorage as moduleTested

################################################################################


class LHCbOnlineStorage_TestCase(unittest.TestCase):
    def setUp(self):
        """Setup."""

        # Mock external libraries / modules not interesting for the unit test
        mock_xmlrpclib = mock.Mock()
        mock_xmlrpclib.Server.return_value("")
        self.mock_xmlrpclib = mock_xmlrpclib

        # Add mocks to moduleTested
        moduleTested.xmlrpclib = self.mock_xmlrpclib

        self.moduleTested = moduleTested
        self.testClass = self.moduleTested.LHCbOnlineStorage

    def tearDown(self):
        """TearDown."""
        del self.testClass
        del self.moduleTested
        del self.mock_xmlrpclib


################################################################################
# Tests


class LHCbOnlineStorage_Success(LHCbOnlineStorage_TestCase):
    def test_instantiate(self):
        """tests that we can instantiate one object of the tested class."""

        resource = self.testClass(
            "storageName",
            {
                "Protocol": "protocol",
                "Path": "path",
                "Host": "host",
                "Port": "port",
                "SpaceToken": "spaceToken",
                "WSUrl": "wspath",
            },
        )

        self.assertEqual("LHCbOnlineStorage", resource.__class__.__name__)

    def test_init(self):
        """tests that the init method does what it should do."""

        resource = self.testClass(
            "storageName",
            {
                "Protocol": "protocol",
                "Path": "path",
                "Host": "host",
                "Port": "port",
                "SpaceToken": "spaceToken",
                "WSUrl": "wspath",
            },
        )

        self.assertEqual("storageName", resource.name)
        self.assertEqual("protocol", resource.protocolParameters["Protocol"])
        self.assertEqual("path", resource.protocolParameters["Path"])
        self.assertEqual("host", resource.protocolParameters["Host"])
        self.assertEqual("port", resource.protocolParameters["Port"])
        self.assertEqual("spaceToken", resource.protocolParameters["SpaceToken"])
        self.assertEqual("wspath", resource.protocolParameters["WSUrl"])

    def test_getParameters(self):
        """tests the output of getParameters method."""

        resource = self.testClass(
            "storageName",
            {
                "Protocol": "protocol",
                "Path": "path",
                "Host": "host",
                "Port": "port",
                "SpaceToken": "spaceToken",
                "WSUrl": "wspath",
            },
        )

        res = resource.getParameters()

        self.assertEqual("storageName", res["StorageName"])
        self.assertEqual("protocol", res["Protocol"])
        self.assertEqual("path", res["Path"])
        self.assertEqual("host", res["Host"])
        self.assertEqual("port", res["Port"])
        self.assertEqual("spaceToken", res["SpaceToken"])
        self.assertEqual("wspath", res["WSUrl"])

    def test_getFileSize(self):
        """tests the output of getFileSize."""

        resource = self.testClass(
            "storageName",
            {
                "Protocol": "protocol",
                "Path": "path",
                "Host": "host",
                "Port": "port",
                "SpaceToken": "spaceToken",
                "WSUrl": "wspath",
            },
        )

        res = resource.getFileSize({})
        self.assertEqual(False, res["OK"])

        res = resource.getFileSize([])
        self.assertEqual(False, res["OK"])

        res = resource.getFileSize(["A", "B"])
        self.assertEqual(True, res["OK"])
        self.assertEqual({"A": 0, "B": 0}, res["Value"]["Successful"])
        self.assertEqual({}, res["Value"]["Failed"])

        res = resource.getFileSize({"A": 1, "B": {}})
        self.assertEqual(True, res["OK"])
        self.assertEqual({"A": 0, "B": 0}, res["Value"]["Successful"])
        self.assertEqual({}, res["Value"]["Failed"])

    def test_removeFile(self):
        """tests the output of removeFile."""

        resource = self.testClass(
            "storageName",
            {
                "Protocol": "protocol",
                "Path": "path",
                "Host": "host",
                "Port": "port",
                "SpaceToken": "spaceToken",
                "WSUrl": "wspath",
            },
        )

        # no need for mock here, we don't reach it

        res = resource.removeFile({})
        self.assertEqual(False, res["OK"])

        res = resource.removeFile([])
        self.assertEqual(False, res["OK"])

        resource.server.endMigratingFileBulk.return_value = (1, {})

        res = resource.removeFile(["A", "B"])
        self.assertEqual(True, res["OK"])
        self.assertEqual({"A": True, "B": True}, res["Value"]["Successful"])
        self.assertEqual({}, res["Value"]["Failed"])

        resource.server.endMigratingFileBulk.return_value = (1, {"B": "Did not work"})

        res = resource.removeFile(["A", "B"])
        self.assertEqual(True, res["OK"])
        self.assertEqual({"A": True}, res["Value"]["Successful"])
        self.assertEqual(["B"], list(res["Value"]["Failed"]))

        resource.server.endMigratingFileBulk.side_effect = Exception("Boom!")
        res = resource.removeFile(["A", "B"])
        # FIXME: This should return S_ERROR !!
        self.assertEqual(True, res["OK"])
        self.assertEqual({}, res["Value"]["Successful"])
        self.assertEqual(["A", "B"], list(res["Value"]["Failed"]))

    def test_retransferOnlineFile(self):
        """tests output of retransferOnlineFile."""

        resource = self.testClass(
            "storageName",
            {
                "Protocol": "protocol",
                "Path": "path",
                "Host": "host",
                "Port": "port",
                "SpaceToken": "spaceToken",
                "WSUrl": "wspath",
            },
        )
        resource.server.errorMigratingFile.return_value = (1, 0)

        res = resource.retransferOnlineFile({})
        self.assertEqual(False, res["OK"])

        res = resource.retransferOnlineFile([])
        self.assertEqual(False, res["OK"])

        res = resource.retransferOnlineFile(["A", "B"])
        self.assertEqual(True, res["OK"])
        self.assertEqual({"A": True, "B": True}, res["Value"]["Successful"])
        self.assertEqual({}, res["Value"]["Failed"])

        # side_effect does not work very well, cooked a workaround
        _myValues = [(0, 1), (1, 0)]

        def _side_effect(_pfn):
            return _myValues.pop()

        resource.server.errorMigratingFile.side_effect = _side_effect

        res = resource.retransferOnlineFile(["A", "B"])
        self.assertEqual(True, res["OK"])
        self.assertEqual({"A": True}, res["Value"]["Successful"])
        self.assertEqual(["B"], list(res["Value"]["Failed"]))

        resource.server.errorMigratingFile.side_effect = Exception("Boom!")
        res = resource.retransferOnlineFile(["A", "B"])
        # FIXME: This should return S_ERROR !!
        self.assertEqual(True, res["OK"])
        self.assertEqual({}, res["Value"]["Successful"])
        self.assertEqual(["A", "B"], list(res["Value"]["Failed"]))
