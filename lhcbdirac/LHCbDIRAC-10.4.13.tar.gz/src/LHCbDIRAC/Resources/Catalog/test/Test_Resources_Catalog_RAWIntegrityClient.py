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
"""Test_Resources_Catalog_RAWIntegrityClient."""
import mock
import unittest

from six.moves import reload_module
from DIRAC import gLogger
import LHCbDIRAC.Resources.Catalog.RAWIntegrityClient as moduleTested

################################################################################


class RAWIntegrityClient_TestCase(unittest.TestCase):
    def setUp(self):
        """Setup."""

        gLogger.setLevel("DEBUG")

        # Mock external libraries / modules not interesting for the unit test
        mock_pathFinder = mock.MagicMock()
        mock_pathFinder.getServiceURL.return_value = "cookiesURL"
        self.mock_pathFinder = mock_pathFinder

        mock_RPC = mock.MagicMock()
        mock_RPC.addFile.return_value = {"OK": True}
        #    mock_RPC.addMigratingReplicas.return_value    = { 'OK' : True }
        #    mock_RPC.removeMigratingFiles.return_value    = { 'OK' : True }
        #    mock_RPC.removeMigratingReplicas.return_value = { 'OK' : True }
        #
        mock_RPCClient = mock.MagicMock()
        mock_RPCClient.return_value = mock_RPC
        self.mock_RPCClient = mock_RPCClient

        # Add mocks to moduleTested
        moduleTested.PathFinder = self.mock_pathFinder
        moduleTested.RPCClient = self.mock_RPCClient

        self.moduleTested = moduleTested
        self.testClass = self.moduleTested.RAWIntegrityClient

    def tearDown(self):
        """TearDown."""
        del self.testClass
        del self.moduleTested
        del self.mock_pathFinder
        del self.mock_RPCClient


################################################################################


class RAWIntegrityClient_Success(RAWIntegrityClient_TestCase):
    def test_instantiate(self):
        """tests that we can instantiate one object of the tested class."""

        catalog = self.testClass()
        self.assertEqual("RAWIntegrityClient", catalog.__class__.__name__)

    def test_exists(self):
        """tests the output of exists."""

        catalog = self.testClass()

        res = catalog.exists("1")
        self.assertTrue(res["OK"])

        res = catalog.exists({})
        self.assertFalse(res["OK"])

        res = catalog.exists(["path1"])
        self.assertTrue(res["OK"])

        res = catalog.exists({"A": 1, "B": 2})
        self.assertTrue(res["OK"])
        self.assertEqual({"Failed": {}, "Successful": {"A": False, "B": False}}, res["Value"])

    def test_addFile(self):
        """tests the output of addFile."""

        catalog = self.testClass()
        catalog.rawIntegritySrv = mock.MagicMock()

        res = catalog.addFile({"1": {"PFN": "pfn", "Size": 123, "SE": "aSe", "GUID": "aGuid", "Checksum": "aCksm"}})
        self.assertTrue(res["OK"])

        fileDict = {"PFN": "pfn", "Size": "10", "SE": "se", "GUID": "guid", "Checksum": "checksum"}

        fileDict["Size"] = "10"

        #    res = catalog.addFile( { 'lfn1' : fileDict } )
        #    self.assertTrue(res['OK'])
        #    self.assertEqual( { 'Successful' : { 'lfn1' : True }, 'Failed' : {} }, res['Value'] )
        #
        #    res = catalog.addFile( { 'lfn1' : fileDict, 'lfn2' : fileDict } )
        #    self.assertTrue(res['OK'])
        #    self.assertEqual( { 'Successful' : { 'lfn1' : True, 'lfn2' : True }, 'Failed' : {} }, res['Value'] )
        #
        #    mock_RPC = mock.Mock()
        #    mock_RPC.addFile.return_value = { 'OK' : False, 'Message' : 'Bo!' }
        #
        #    self.moduleTested.RPCClient.return_value = mock_RPC
        #    catalog = self.testClass()
        #
        #    res = catalog.addFile( { 'lfn1' : fileDict } )
        #    self.assertTrue(res['OK'])
        #    self.assertEqual( { 'Successful' : {}, 'Failed' : {'lfn1' : 'Bo!' } }, res['Value'] )
        #
        #    res = catalog.addFile( { 'lfn1' : fileDict, 'lfn2' : fileDict } )
        #    self.assertTrue(res['OK'])
        #    self.assertEqual( { 'Successful' : {}, 'Failed' : {  'lfn1' : 'Bo!', 'lfn2' : 'Bo!' } }, res['Value'] )

        # Restore the module
        self.moduleTested.RPCClient.return_value = self.mock_RPCClient
        reload_module(self.moduleTested)


################################################################################
