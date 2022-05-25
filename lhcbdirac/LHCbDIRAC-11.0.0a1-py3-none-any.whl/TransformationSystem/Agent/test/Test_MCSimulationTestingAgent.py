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
"""Test class for the MCSimulationTestingAgent."""
import datetime
import importlib
import unittest
from mock import MagicMock, patch

from LHCbDIRAC.TransformationSystem.Agent.MCSimulationTestingAgent import MCSimulationTestingAgent
from LHCbDIRAC.ProductionManagementSystem.Client.Production import Production
from DIRAC.Core.Workflow.Workflow import fromXMLString
from DIRAC import gLogger

try:
    with open("./src/LHCbDIRAC/TransformationSystem/Agent/test/testWF.xml") as fd:
        storedJobDescription = fd.read()
except IOError:
    with open("./TransformationSystem/Agent/test/testWF.xml") as fd:
        storedJobDescription = fd.read()


class MCSimulationTestingAgentTestCase(unittest.TestCase):
    def setUp(self):
        self.mockAM = MagicMock()
        self.agent = importlib.import_module("LHCbDIRAC.TransformationSystem.Agent.MCSimulationTestingAgent")
        self.agent.AgentModule = self.mockAM
        self.agent = MCSimulationTestingAgent()
        self.agent.log = gLogger
        self.agent.log.setLevel("DEBUG")
        self.transID = 1
        self.tasks = [
            {
                "TargetSE": "Unknown",
                "TransformationID": 1,
                "LastUpdateTime": datetime.datetime(2014, 7, 29, 12, 12, 13),
                "RunNumber": 0,
                "CreationTime": datetime.datetime(2014, 7, 29, 12, 12, 13),
                "ExternalID": "0",
                "ExternalStatus": "Running",
                "TaskID": 1,
            },
            {
                "TargetSE": "Unknown",
                "TransformationID": 1,
                "LastUpdateTime": datetime.datetime(2014, 7, 29, 12, 12, 13),
                "RunNumber": 0,
                "CreationTime": datetime.datetime(2014, 7, 29, 12, 12, 13),
                "ExternalID": "0",
                "ExternalStatus": "Created",
                "TaskID": 2,
            },
        ]
        self.report = {
            "subject": "MCSimulation Test Failure Report. TransformationID: " + str(self.transID),
            "body": [
                "MCSimulation Test Failure Report. TransformationID: " + str(self.transID),
                "",
                "Transformation:",
                "----------------------------------------------------------------------",
                "TransformationID: " + str(self.transID),
                "TransformationName: transName",
                "LastUpdate: 29/07/2014 13:06",
                "Status: New",
                "Description: description",
                "TransformationFamily: 0",
                "Plugin: Standard",
                "Type: MCSimulation",
                "AgentType: Manual",
                "GroupSize: 1",
                "MaxNumberOfTasks: 0",
                "AuthorDN: /DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=sbidwell/CN=758039/CN=Simon Bidwell",
                "TransformationGroup: General",
                "InheritedFrom: 0",
                "CreationDate: 29/07/2014 13:06",
                "FileMask: ",
                "EventsPerTask: 0",
                "AuthorGroup: devGroup",
                "",
                "Number of Tasks: " + str(len(self.tasks)),
                "Tasks:",
                "----------------------------------------------------------------------",
                "TaskID: 1",
                "TargetSE: Unknown",
                "LastUpdateTime: 29/07/2014 12:12",
                "RunNumber: 0",
                "CreationTime: 29/07/2014 12:12",
                "ExternalID: 0",
                "ExternalStatus: Running",
                "",
                "TaskID: 2",
                "TargetSE: Unknown",
                "LastUpdateTime: 29/07/2014 12:12",
                "RunNumber: 0",
                "CreationTime: 29/07/2014 12:12",
                "ExternalID: 0",
                "ExternalStatus: Created",
                "",
            ],
        }

        self.transClientMock = MagicMock()
        self.transClientMock.getTransformations.return_value = {
            "OK": True,
            "Value": [
                {
                    "Body": "",
                    "LastUpdate": datetime.datetime(2014, 7, 29, 13, 6, 8),
                    "Status": "New",
                    "TransformationID": 1,
                    "Description": "description",
                    "TransformationFamily": 0,
                    "Plugin": "Standard",
                    "Type": "MCSimulation",
                    "AgentType": "Manual",
                    "GroupSize": 1,
                    "LongDescription": "longDescription",
                    "MaxNumberOfTasks": 0,
                    "Hot": 0,
                    "AuthorDN": "/DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=sbidwell/CN=758039/CN=Simon Bidwell",
                    "TransformationName": "transName",
                    "TransformationGroup": "General",
                    "InheritedFrom": 0,
                    "CreationDate": datetime.datetime(2014, 7, 29, 13, 6, 8),
                    "FileMask": "",
                    "EventsPerTask": 0,
                    "AuthorGroup": "devGroup",
                }
            ],
        }
        self.transClientMock.getStoredJobDescription.return_value = {"OK": True, "Value": ((1, storedJobDescription),)}
        self.transClientMock.setTransformationParameter.return_value = {"OK": True}
        self.transClientMock.extendTransformation.return_value = {"OK": True, "Value": [3, 4, 5]}

        self.bkClientMock = MagicMock()
        self.bkClientMock.bulkJobInfo.return_value = {
            "OK": True,
            "Value": {
                "Failed": [],
                "Successful": {
                    "123": [
                        {
                            "ApplicationName": "Gauss",
                            "ApplicationVersion": "v30r14",
                            "CPUTIME": 1000.0,
                            "DIRACJobId": 1563495,
                            "DIRACVersion": "v2r13 build 3",
                            "EventInputStat": None,
                            "ExecTime": 2000.0,
                            "FirstEventNumber": 1,
                            "JobId": 123456,
                            "Location": "LCG.Glasgow.uk",
                            "Name": "00001764_00000195_5",
                            "NumberOfEvents": 100,
                            "Production": 1764,
                            "StatisticsRequested": None,
                            "TotalLumonosity": 0,
                            "WNCACHE": "1024KB",
                            "WNCPUHS06": 10.0,
                            "WNCPUPOWER": None,
                            "WNMEMORY": "8195868kB",
                            "WNMODEL": "DualCoreAMDOpteron(tm)",
                            "WORKERNODE": "node046.",
                        },
                        {
                            "ApplicationName": "Boole",
                            "ApplicationVersion": "v30r14",
                            "CPUTIME": 100.0,
                            "DIRACJobId": 1563495,
                            "DIRACVersion": "v2r13 build 3",
                            "EventInputStat": None,
                            "ExecTime": 200.0,
                            "FirstEventNumber": 1,
                            "JobId": 123456,
                            "Location": "LCG.Glasgow.uk",
                            "Name": "00001764_00000195_5",
                            "NumberOfEvents": 100,
                            "Production": 1764,
                            "StatisticsRequested": None,
                            "TotalLumonosity": 0,
                            "WNCACHE": "1024KB",
                            "WNCPUHS06": 10.0,
                            "WNCPUPOWER": None,
                            "WNMEMORY": "8195868kB",
                            "WNMODEL": "DualCoreAMDOpteron(tm)",
                            "WORKERNODE": "node046.",
                        },
                        {
                            "ApplicationName": "Bof",
                            "ApplicationVersion": "v30r14",
                            "CPUTIME": 100.0,
                            "DIRACJobId": 1563495,
                            "DIRACVersion": "v2r13 build 3",
                            "EventInputStat": None,
                            "ExecTime": 200.0,
                            "FirstEventNumber": 1,
                            "JobId": 123456,
                            "Location": "LCG.Glasgow.uk",
                            "Name": "00001764_00000195_5",
                            "NumberOfEvents": 100,
                            "Production": 1764,
                            "StatisticsRequested": None,
                            "TotalLumonosity": 0,
                            "WNCACHE": "1024KB",
                            "WNCPUHS06": 10.0,
                            "WNCPUPOWER": None,
                            "WNMEMORY": "8195868kB",
                            "WNMODEL": "DualCoreAMDOpteron(tm)",
                            "WORKERNODE": "node046.",
                        },
                        {
                            "ApplicationName": "Moore",
                            "ApplicationVersion": "v30r14",
                            "CPUTIME": 200.0,
                            "DIRACJobId": 1563495,
                            "DIRACVersion": "v2r13 build 3",
                            "EventInputStat": None,
                            "ExecTime": 200.0,
                            "FirstEventNumber": 1,
                            "JobId": 123456,
                            "Location": "LCG.Glasgow.uk",
                            "Name": "00001764_00000195_5",
                            "NumberOfEvents": 100,
                            "Production": 1764,
                            "StatisticsRequested": None,
                            "TotalLumonosity": 0,
                            "WNCACHE": "1024KB",
                            "WNCPUHS06": 10.0,
                            "WNCPUPOWER": None,
                            "WNMEMORY": "8195868kB",
                            "WNMODEL": "DualCoreAMDOpteron(tm)",
                            "WORKERNODE": "node046.",
                        },
                    ]
                },
            },
            "rpcStub": (
                (
                    "Bookkeeping/BookkeepingManager",
                    {
                        "delegatedDN": "/DC=ch/CN=Simon Bidwell",
                        "delegatedGroup": "lhcb_user",
                        "keepAliveLapse": 150,
                        "skipCACheck": False,
                        "timeout": 3600,
                    },
                ),
                "bulkJobInfo",
                ([123, 456],),
            ),
        }

        self.notifyClientMock = MagicMock()
        self.notifyClientMock.sendMail.return_value = {"OK": True, "Value": "The mail was succesfully sent"}

        self.operationsMock = MagicMock()
        self.operationsMock.getValue.return_value = "sbidwell"

        self.agent.transClient = self.transClientMock
        self.agent.bkClient = self.bkClientMock
        self.agent.notifyClient = self.notifyClientMock
        self.agent.operations = self.operationsMock
        self.agent.email = "myEmail@cern.ch"

    def tearDown(self):
        pass

    def test_send_report(self):
        res = self.agent._sendReport(self.report)
        self.assertEqual(res, None)

    def test_update_workflow(self):
        CPUe = 1
        MCCpu = 25
        s1 = """<Parameter name="CPUe" type="string" linked_module="" linked_parameter="" in="True" out="False" """
        s1 += """description="CPU time per event"><value><![CDATA[1]]></value></Parameter>\n"""
        CPUe_xml = self.test_workflow = s1
        s2 = """<Parameter name="maxNumberOfEvents" type="string" linked_module="" linked_parameter="" """
        s2 += """in="True" out="False" description="Maximum number of events to produce (Gauss)">"""
        s2 += """<value><![CDATA[150000]]></value></Parameter>\n"""
        max_e_xml = self.test_workflow = s2
        res = self.agent._updateWorkflow(self.transID, CPUe, MCCpu)
        self.assertTrue(res["OK"])
        prod = Production()
        prod.LHCbJob.workflow = fromXMLString(res["Value"])
        cpue_param = prod.LHCbJob.workflow.findParameter("CPUe")
        max_e_param = prod.LHCbJob.workflow.findParameter("maxNumberOfEvents")
        self.assertEqual(CPUe_xml, cpue_param.toXML())
        self.assertEqual(max_e_xml, max_e_param.toXML())

    @patch("LHCbDIRAC.TransformationSystem.Agent.MCSimulationTestingAgent.getEventsToProduce")
    def test_calculate_parameters(self, _patch_mock):
        #     expected_max_e = 100
        # mock to make getEventsToProduce to return 100
        #     patch_mock.return_value = expected_max_e
        res = self.agent._calculateParameters(self.tasks)
        self.assertTrue(res["OK"])
        self.assertEqual(res["Value"]["CPUe"], 130.0)


#     self.assertEqual( res['Value']['max_e'], expected_max_e )


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(MCSimulationTestingAgentTestCase)
    testResult = unittest.TextTestRunner(verbosity=2).run(suite)
