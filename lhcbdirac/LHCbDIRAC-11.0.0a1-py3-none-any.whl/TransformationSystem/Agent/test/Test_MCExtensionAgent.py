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
"""Unit test for the MCExtensionAgent."""
import datetime
import copy
import importlib
import unittest

from mock import Mock, MagicMock
from DIRAC import S_OK, S_ERROR, gLogger

from LHCbDIRAC.TransformationSystem.Agent.MCExtensionAgent import MCExtensionAgent


class MCExtensionAgentTestCase(unittest.TestCase):
    def setUp(self):
        self.mockAM = MagicMock()
        self.mockAM.am_getOption.return_value = S_OK()
        self.agent = importlib.import_module("LHCbDIRAC.TransformationSystem.Agent.MCExtensionAgent")
        self.agent.AgentModule = self.mockAM
        self.agent.DIRACMCExtensionAgent = self.mockAM
        self.agent = MCExtensionAgent()
        print(dir(self.agent))
        self.agent.log = gLogger

    # def test_execute( self ):
    #   # self.agent = self.moduleTested.MCExtensionAgent( 'MCExtensionAgent', 'MCExtensionAgent', 'MCExtensionAgent' )
    #   self.agent.transformationTypes = ['MCSimulation', 'Simulation']
    #   self.agent.rpcProductionRequest = Mock()
    #   self.agent._checkProductionRequest = Mock()
    #
    #   ###########################################################################
    #
    #   # disabled by configuration
    #   self.mockAM.am_getOption.side_effect = lambda optionName,
    # defaultValue: {( 'EnableFlag', 'True' ) : 'False'}[( optionName, defaultValue )]
    #
    #   ret = self.agent.execute()
    #   self.assertTrue( ret['OK'] )
    #
    #   ###########################################################################
    #
    #   # bad request
    #   # self.mockAM.am_getOption.side_effect = lambda optionName,
    # defaultValue: {( 'EnableFlag', 'True' ) : 'True'}[( optionName, defaultValue )]
    #   self.agent.rpcProductionRequest.getProductionRequestSummary.return_value = S_ERROR()
    #
    #   ret = self.agent.execute()
    #   self.assertFalse( ret['OK'] )
    #
    #   ###########################################################################
    #
    #   # normal operation
    #   # self.mockAM.am_getOption.side_effect = lambda optionName,
    # defaultValue: {( 'EnableFlag', 'True' ) : 'True'}[( optionName, defaultValue )]
    #   productionRequests = {10964: {'bkTotal': 259499L, 'master': 10960, 'reqTotal': 500000L},
    #                         10965: {'bkTotal': 610999L, 'master': 10960, 'reqTotal': 1000000L},
    #                         10966: {'bkTotal': 660995L, 'master': 10959, 'reqTotal': 1000000L}}
    #   self.agent.rpcProductionRequest.getProductionRequestSummary.return_value = S_OK( productionRequests )
    #   self.agent._checkProductionRequest.return_value = S_OK()
    #
    #   ret = self.agent.execute()
    #   self.assertTrue( ret['OK'] )
    #   self.assertEqual( self.agent._checkProductionRequest.call_count, len( productionRequests ) )
    #   self.agent._checkProductionRequest.assert_has_calls(
    # [call( ID, summary ) for ID, summary in productionRequests.items()] )

    def test__checkProductionRequest(self):
        # self.agent = self.moduleTested.MCExtensionAgent( 'MCExtensionAgent', 'MCExtensionAgent', 'MCExtensionAgent' )
        self.agent.transformationTypes = ["MCSimulation", "Simulation"]
        self.agent.rpcProductionRequest = Mock()
        self.agent.transClient = Mock()
        self.agent._extendProduction = Mock()

        completeProductionRequestID = 12417
        completeProductionRequestSummary = {"bkTotal": 503999, "master": 12415, "reqTotal": 500000}

        incompleteProductionRequestID = 11162
        incompleteProductionRequestSummary = {"bkTotal": 296999, "master": 11158, "reqTotal": 500000}
        missingEventsExp = 203001

        productionsProgressNoStripping = {
            "Rows": [
                {"BkEvents": 390499, "ProductionID": 24781, "RequestID": 11162, "Used": 0},
                {"BkEvents": 296999, "ProductionID": 24782, "RequestID": 11162, "Used": 1},
            ]
        }
        productionsProgressWithStripping = {
            "Rows": [
                {"BkEvents": 2969990, "ProductionID": 24781, "RequestID": 11162, "Used": 0},
                {"BkEvents": 296999, "ProductionID": 24782, "RequestID": 11162, "Used": 1},
            ]
        }
        extensionFactorExp = 10.0

        transformations = {
            24781: {
                "AgentType": "Automatic",
                "AuthorDN": "/DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=romanov/CN=427293/CN=Vladimir Romanovskiy",
                "AuthorGroup": "lhcb_prod",
                "Body": "<Workflow>...</Workflow>",
                "CreationDate": datetime.datetime(2013, 6, 10, 18, 30, 22),
                "Description": "",
                "EventsPerTask": 0,
                "FileMask": "",
                "GroupSize": 1,
                "InheritedFrom": 0,
                "LastUpdate": datetime.datetime(2013, 6, 12, 6, 59, 56),
                "LongDescription": "prodDescription",
                "MaxNumberOfTasks": 0,
                "Plugin": "",
                "Status": "Idle",
                "TransformationFamily": "11158",
                "TransformationGroup": "Sim08a/Digi13/Trig0x409f0045/Reco14a/Stripping20NoPrescalingFlag",
                "TransformationID": 24781,
                "TransformationName": "Request_11162_bof.xml",
                "Type": "MCSimulation",
            },
            24782: {
                "AgentType": "Automatic",
                "AuthorDN": "/DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=romanov/CN=427293/CN=Vladimir Romanovskiy",
                "AuthorGroup": "lhcb_prod",
                "Body": "<Workflow>...<Workflow>",
                "CreationDate": datetime.datetime(2013, 6, 10, 18, 30, 27),
                "Description": "",
                "EventsPerTask": 0,
                "FileMask": "",
                "GroupSize": 5,
                "InheritedFrom": 0,
                "LastUpdate": datetime.datetime(2013, 6, 12, 6, 59, 56),
                "LongDescription": "prodDescription",
                "MaxNumberOfTasks": 0,
                "Plugin": "BySize",
                "Status": "Idle",
                "TransformationFamily": "11158",
                "TransformationGroup": "Sim08a/Digi13/Trig0x409f0045/Reco14a/Stripping20NoPrescalingFlag",
                "TransformationID": 24782,
                "TransformationName": "Request_bof.xml",
                "Type": "Merge",
            },
        }
        simulation = transformations[24781]

        ###########################################################################

        # complete production request, no extension needed
        ret = self.agent._checkProductionRequest(completeProductionRequestID, completeProductionRequestSummary)
        self.assertTrue(ret["OK"])
        self.assertFalse(self.agent._extendProduction.called)
        self.agent._extendProduction.reset_mock()

        ###########################################################################

        # failed request for production progress
        self.agent.rpcProductionRequest.getProductionProgressList.return_value = S_ERROR()

        ret = self.agent._checkProductionRequest(incompleteProductionRequestID, incompleteProductionRequestSummary)
        self.assertFalse(ret["OK"])
        self.assertFalse(self.agent._extendProduction.called)
        self.agent._extendProduction.reset_mock()

        ###########################################################################

        # failed request for production
        self.agent.rpcProductionRequest.getProductionProgressList.return_value = S_OK(productionsProgressNoStripping)
        self.agent.transClient.getTransformation.return_value = S_ERROR()

        ret = self.agent._checkProductionRequest(incompleteProductionRequestID, incompleteProductionRequestSummary)
        self.assertFalse(ret["OK"])
        self.assertFalse(self.agent._extendProduction.called)
        self.agent._extendProduction.reset_mock()

        ###########################################################################

        # simulation production not found
        self.agent.rpcProductionRequest.getProductionProgressList.return_value = S_OK(productionsProgressNoStripping)
        noSimulationTransformations = copy.deepcopy(transformations)
        for t in noSimulationTransformations.values():
            t["Type"] = "Merge"
        self.agent.transClient.getTransformation.side_effect = lambda transformationID: S_OK(
            noSimulationTransformations[transformationID]
        )

        ret = self.agent._checkProductionRequest(incompleteProductionRequestID, incompleteProductionRequestSummary)
        self.assertFalse(ret["OK"])
        self.assertFalse(self.agent._extendProduction.called)
        self.agent._extendProduction.reset_mock()

        ###########################################################################

        # non idle simulation
        self.agent.rpcProductionRequest.getProductionProgressList.return_value = S_OK(productionsProgressNoStripping)
        nonIdleSimulationTransformations = copy.deepcopy(transformations)
        for t in nonIdleSimulationTransformations.values():
            if t["Type"] == "MCSimulation":
                t["Status"] = "Active"
        self.agent.transClient.getTransformation.side_effect = lambda transformationID: S_OK(
            nonIdleSimulationTransformations[transformationID]
        )

        ret = self.agent._checkProductionRequest(incompleteProductionRequestID, incompleteProductionRequestSummary)
        self.assertTrue(ret["OK"])
        self.assertFalse(self.agent._extendProduction.called)
        self.agent._extendProduction.reset_mock()

        ###########################################################################

        # no stripping production (no extension factor)
        self.agent.rpcProductionRequest.getProductionProgressList.return_value = S_OK(productionsProgressNoStripping)
        self.agent.transClient.getTransformation.side_effect = lambda transformationID: S_OK(
            transformations[transformationID]
        )
        self.agent._extendProduction.return_value = S_OK()

        #     ret = self.agent._checkProductionRequest( incompleteProductionRequestID, incompleteProductionRequestSummary )
        #     self.assertTrue( ret['OK'] )
        #     self.agent._extendProduction.assert_called_once_with( simulation, 1.0, missingEventsExp )
        #     self.agent._extendProduction.reset_mock()

        ###########################################################################

        # stripping production (extension factor)
        self.agent.rpcProductionRequest.getProductionProgressList.return_value = S_OK(productionsProgressWithStripping)
        self.agent.transClient.getTransformation.side_effect = lambda transformationID: S_OK(
            transformations[transformationID]
        )
        self.agent._extendProduction.return_value = S_OK()

    #     ret = self.agent._checkProductionRequest( incompleteProductionRequestID, incompleteProductionRequestSummary )
    #     self.assertTrue( ret['OK'] )
    #     self.agent._extendProduction.assert_called_once_with( simulation, extensionFactorExp, missingEventsExp )
    #     self.agent._extendProduction.reset_mock()

    def test__extendProduction(self):
        # self.agent = self.moduleTested.MCExtensionAgent( 'MCExtensionAgent', 'MCExtensionAgent', 'MCExtensionAgent' )
        self.agent.transformationTypes = ["MCSimulation", "Simulation"]
        self.agent.transClient = Mock()
        self.agent.transClient.extendTransformation.return_value = S_OK()
        self.agent.transClient.setTransformationParameter.return_value = S_OK()

        self.agent.cpuTimeAvg = 1000000
        self.agent.cpuNormalizationFactorAvg = 1.0

        production = {
            "AgentType": "Automatic",
            "AuthorDN": "/DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=romanov/CN=427293/CN=Vladimir Romanovskiy",
            "AuthorGroup": "lhcb_prod",
            "Body": """
        <Workflow>
          <origin></origin>
          <description><![CDATA[prodDescription]]></description>
          <descr_short></descr_short>
          <version>0.0</version>
          <type></type>
          <name>Request_12416_MCSimulation_Sim08a/Digi13/Trig0x40760037/Reco14a/Stripping20bof</name>
          <Parameter name="CPUe" type="JDL" linked_module="" linked_parameter="" in="True" out="False" description="C">
            <value><![CDATA[10]]></value>
          </Parameter>
        </Workflow>
      """,
            "CreationDate": datetime.datetime(2013, 6, 4, 8, 12),
            "Description": "",
            "EventsPerTask": 0,
            "FileMask": "",
            "GroupSize": 1,
            "InheritedFrom": 0,
            "LastUpdate": datetime.datetime(2013, 6, 4, 8, 12, 3),
            "LongDescription": "prodDescription",
            "MaxNumberOfTasks": 0,
            "Plugin": "",
            "Status": "Idle",
            "TransformationFamily": "12415",
            "TransformationGroup": "Sim08a/Digi13/Trig0x40760037/Reco14a/Stripping20r1NoPrescalingFl",
            "TransformationID": 24614,
            "TransformationName": "Request_12416_bof.xml",
            "Type": "MCSimulation",
        }
        extensionFactor = 2.0
        eventsNeeded = 1000000

        productionIDExp = 24614
        numberOfTasksExp = 32

        ret = self.agent._extendProduction(production, extensionFactor, eventsNeeded)
        self.assertTrue(ret["OK"])
        self.agent.transClient.extendTransformation.assert_called_once_with(productionIDExp, numberOfTasksExp)


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(MCExtensionAgentTestCase)
    testResult = unittest.TextTestRunner(verbosity=2).run(suite)
