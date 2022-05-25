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
"""Client test."""
# pylint: disable=protected-access, missing-docstring, invalid-name, line-too-long

import unittest

from mock import MagicMock

from DIRAC import S_OK, gLogger

from LHCbDIRAC.TransformationSystem.Client.TaskManager import LHCbWorkflowTasks
from LHCbDIRAC.TransformationSystem.Client.TransformationClient import TransformationClient
from LHCbDIRAC.TransformationSystem.Utilities.PluginUtilities import PluginUtilities, groupByRun


def getSitesForSE(ses):
    if ses == "pippo":
        return {"OK": True, "Value": ["Site2", "Site3"]}
    else:
        return {"OK": True, "Value": ["Site3"]}


class ClientTestCase(unittest.TestCase):
    def setUp(self):
        tcMock = MagicMock()
        sc = MagicMock()
        jmc = MagicMock()

        self.l_wft = LHCbWorkflowTasks(tcMock, submissionClient=sc, jobMonitoringClient=jmc)
        self.tc = TransformationClient()
        self.tc.dataProcessingTypes = ["MCSimulation", "DataReconstruction"]

        self.tsMock = MagicMock()

        self.fcMock = MagicMock()
        self.fcMock.getFileSize.return_value = S_OK({"Failed": [], "Successful": cachedLFNSize})

        gLogger.setLevel("DEBUG")

        self.maxDiff = None

    def tearDown(self):
        pass


class TaskManagerSuccess(ClientTestCase):
    pass


class TransformationClientSuccess(ClientTestCase):
    def test__applyTransformationFilesStateMachine(self):
        tsFiles = {}
        dictOfNewLFNsStatus = {}
        res = self.tc._applyTransformationFilesStateMachine(tsFiles, dictOfNewLFNsStatus, False)
        self.assertEqual(res, {})

        tsFiles = {}
        dictOfNewLFNsStatus = {"foo": ["status", 2, 1234]}
        res = self.tc._applyTransformationFilesStateMachine(tsFiles, dictOfNewLFNsStatus, False)
        self.assertEqual(res, {})

        tsFiles = {"foo": ["status", 2, 1234]}
        dictOfNewLFNsStatus = {"foo": "status"}
        res = self.tc._applyTransformationFilesStateMachine(tsFiles, dictOfNewLFNsStatus, False)
        self.assertEqual(res, {})

        tsFiles = {"foo": ["status", 2, 1234]}
        dictOfNewLFNsStatus = {"foo": "statusA"}
        res = self.tc._applyTransformationFilesStateMachine(tsFiles, dictOfNewLFNsStatus, False)
        self.assertEqual(res, {"foo": "statusA"})

        tsFiles = {"foo": ["status", 2, 1234], "bar": ["status", 2, 5678]}
        dictOfNewLFNsStatus = {"foo": "status"}
        res = self.tc._applyTransformationFilesStateMachine(tsFiles, dictOfNewLFNsStatus, False)
        self.assertEqual(res, {})

        tsFiles = {"foo": ["status", 2, 1234], "bar": ["status", 2, 5678]}
        dictOfNewLFNsStatus = {"foo": "statusA"}
        res = self.tc._applyTransformationFilesStateMachine(tsFiles, dictOfNewLFNsStatus, False)
        self.assertEqual(res, {"foo": "statusA"})

        tsFiles = {"foo": ["status", 2, 1234], "bar": ["status", 2, 5678]}
        dictOfNewLFNsStatus = {"foo": "A", "bar": "B"}
        res = self.tc._applyTransformationFilesStateMachine(tsFiles, dictOfNewLFNsStatus, False)
        self.assertEqual(res, {"foo": "A", "bar": "B"})

        tsFiles = {"foo": ["status", 2, 1234]}
        dictOfNewLFNsStatus = {"foo": "A", "bar": "B"}
        res = self.tc._applyTransformationFilesStateMachine(tsFiles, dictOfNewLFNsStatus, False)
        self.assertEqual(res, {"foo": "A"})

        tsFiles = {"foo": ["Assigned", 2, 1234]}
        dictOfNewLFNsStatus = {"foo": "A", "bar": "B"}
        res = self.tc._applyTransformationFilesStateMachine(tsFiles, dictOfNewLFNsStatus, False)
        self.assertEqual(res, {"foo": "A"})

        tsFiles = {"foo": ["Assigned", 2, 1234], "bar": ["Assigned", 2, 5678]}
        dictOfNewLFNsStatus = {"foo": "Assigned", "bar": "Processed"}
        res = self.tc._applyTransformationFilesStateMachine(tsFiles, dictOfNewLFNsStatus, False)
        self.assertEqual(res, {"bar": "Processed"})

        tsFiles = {"foo": ["Processed", 2, 1234], "bar": ["Unused", 2, 5678]}
        dictOfNewLFNsStatus = {"foo": "Assigned", "bar": "Processed"}
        res = self.tc._applyTransformationFilesStateMachine(tsFiles, dictOfNewLFNsStatus, False)
        self.assertEqual(res, {"bar": "Processed"})

        tsFiles = {"foo": ["Processed", 2, 1234], "bar": ["Unused", 2, 5678]}
        dictOfNewLFNsStatus = {"foo": "Assigned", "bar": "Processed"}
        res = self.tc._applyTransformationFilesStateMachine(tsFiles, dictOfNewLFNsStatus, True)
        self.assertEqual(res, {"foo": "Assigned", "bar": "Processed"})

        tsFiles = {"foo": ["Processed", 2, 1234], "bar": ["Unused", 2, 5678]}
        dictOfNewLFNsStatus = {"foo": "Assigned", "bar": "Processed"}
        res = self.tc._applyTransformationFilesStateMachine(tsFiles, dictOfNewLFNsStatus, True)
        self.assertEqual(res, {"foo": "Assigned", "bar": "Processed"})

        tsFiles = {"foo": ["MaxReset", 12, 1234], "bar": ["Processed", 22, 5678]}
        dictOfNewLFNsStatus = {"foo": "Unused", "bar": "Unused"}
        res = self.tc._applyTransformationFilesStateMachine(tsFiles, dictOfNewLFNsStatus, False)
        self.assertEqual(res, {})

        tsFiles = {"foo": ["MaxReset", 12, 1234], "bar": ["Processed", 22, 5678]}
        dictOfNewLFNsStatus = {"foo": "Unused", "bar": "Unused"}
        res = self.tc._applyTransformationFilesStateMachine(tsFiles, dictOfNewLFNsStatus, True)
        self.assertEqual(res, {"foo": "Unused", "bar": "Unused"})

        tsFiles = {"foo": ["Assigned", 20, 1234], "bar": ["Processed", 2, 5678]}
        dictOfNewLFNsStatus = {"foo": "Unused", "bar": "Unused"}
        res = self.tc._applyTransformationFilesStateMachine(tsFiles, dictOfNewLFNsStatus, False)
        self.assertEqual(res, {"foo": "MaxReset"})

        tsFiles = {"foo": ["Assigned", 20, 1234], "bar": ["Processed", 2, 5678]}
        dictOfNewLFNsStatus = {"foo": "Unused", "bar": "Unused"}
        res = self.tc._applyTransformationFilesStateMachine(tsFiles, dictOfNewLFNsStatus, True)
        self.assertEqual(res, {"foo": "Unused", "bar": "Unused"})

    def test__applyTransformationStatusStateMachine(self):
        transIDAsDict = {123: ["Active", "MCSimulation"]}
        dictOfProposedstatus = {123: "Stopped"}
        res = self.tc._applyTransformationStatusStateMachine(transIDAsDict, dictOfProposedstatus, False)
        self.assertEqual(res, "Stopped")

        transIDAsDict = {123: ["New", "MCSimulation"]}
        dictOfProposedstatus = {123: "Active"}
        res = self.tc._applyTransformationStatusStateMachine(transIDAsDict, dictOfProposedstatus, False)
        self.assertEqual(res, "Active")

        transIDAsDict = {123: ["New", "MCSimulation"]}
        dictOfProposedstatus = {123: "New"}
        res = self.tc._applyTransformationStatusStateMachine(transIDAsDict, dictOfProposedstatus, False)
        self.assertEqual(res, "New")

        transIDAsDict = {123: ["New", "MCSimulation"]}
        dictOfProposedstatus = {123: "Stopped"}
        res = self.tc._applyTransformationStatusStateMachine(transIDAsDict, dictOfProposedstatus, False)
        self.assertEqual(res, "New")

        transIDAsDict = {123: ["New", "MCSimulation"]}
        dictOfProposedstatus = {123: "Stopped"}
        res = self.tc._applyTransformationStatusStateMachine(transIDAsDict, dictOfProposedstatus, True)
        self.assertEqual(res, "Stopped")

        transIDAsDict = {123: ["New", "MCSimulation"]}
        dictOfProposedstatus = {123: "Idle"}
        res = self.tc._applyTransformationStatusStateMachine(transIDAsDict, dictOfProposedstatus, False)
        self.assertEqual(res, "New")

        transIDAsDict = {123: ["Active", "MCSimulation"]}
        dictOfProposedstatus = {123: "Idle"}
        res = self.tc._applyTransformationStatusStateMachine(transIDAsDict, dictOfProposedstatus, False)
        self.assertEqual(res, "Idle")

        transIDAsDict = {123: ["Active", "MCSimulation"]}
        dictOfProposedstatus = {123: "Completed"}
        res = self.tc._applyTransformationStatusStateMachine(transIDAsDict, dictOfProposedstatus, False)
        self.assertEqual(res, "Flush")

        transIDAsDict = {123: ["Active", "MCSimulation"]}
        dictOfProposedstatus = {123: "Complete"}
        res = self.tc._applyTransformationStatusStateMachine(transIDAsDict, dictOfProposedstatus, False)
        self.assertEqual(res, "Active")


# Test data for plugins
data = {
    "/this/is/at_1": ["SE1"],
    "/this/is/at_2": ["SE2"],
    "/this/is/at_12": ["SE1", "SE2"],
    "/this/is/also/at_12": ["SE1", "SE2"],
    "/this/is/at_123": ["SE1", "SE2", "SE3"],
    "/this/is/at_23": ["SE2", "SE3"],
    "/this/is/at_4": ["SE4"],
}

cachedLFNSize = {
    "/this/is/at_1": 1,
    "/this/is/at_2": 2,
    "/this/is/at_12": 12,
    "/this/is/also/at_12": 12,
    "/this/is/at_123": 123,
    "/this/is/at_23": 23,
    "/this/is/at_4": 4,
}

runFiles = [
    {"LFN": "/this/is/at_1", "RunNumber": 1},
    {"LFN": "/this/is/at_2", "RunNumber": 2},
    {"LFN": "/this/is/at_12", "RunNumber": 12},
    {"LFN": "/this/is/also/at_12", "RunNumber": 12},
    {"LFN": "/this/is/at_123", "RunNumber": 123},
    {"LFN": "/this/is/at_23", "RunNumber": 23},
    {"LFN": "/this/is/at_4", "RunNumber": 4},
]

cachedLFNAncestors = {1: {"": 1}}


class PluginsUtilitiesSuccess(ClientTestCase):
    def test_groupByRun(self):

        # no files, nothing happens
        resDict = groupByRun([])
        self.assertEqual(resDict, {})

        # some files
        resDict = groupByRun(list(runFiles))
        resExpected = {
            1: ["/this/is/at_1"],
            2: ["/this/is/at_2"],
            4: ["/this/is/at_4"],
            12: ["/this/is/at_12", "/this/is/also/at_12"],
            23: ["/this/is/at_23"],
            123: ["/this/is/at_123"],
        }
        self.assertEqual(resDict, resExpected)

    def test_groupByRunAndParam(self):

        # no files, nothing happens
        pu = PluginUtilities(fc=self.fcMock, dataManager=MagicMock(), rmClient=MagicMock())
        pu.transFiles = []
        resDict = pu.getFilesGroupedByRunAndParam({})
        self.assertEqual(resDict, {})

        # some files, no params (it seems it's never called with params...?
        pu = PluginUtilities(fc=self.fcMock, dataManager=MagicMock(), rmClient=MagicMock())
        pu.transFiles = runFiles
        resDict = pu.getFilesGroupedByRunAndParam(data)
        resExpected = {
            1: {None: ["/this/is/at_1"]},
            2: {None: ["/this/is/at_2"]},
            4: {None: ["/this/is/at_4"]},
            12: {None: ["/this/is/at_12", "/this/is/also/at_12"]},
            23: {None: ["/this/is/at_23"]},
            123: {None: ["/this/is/at_123"]},
        }
        self.assertEqual(resDict, resExpected)

    def test_getRAWAncestorsForRun(self):

        # no files, nothing happens
        #     tsMock = MagicMock()
        #     tsMock.getTransformationFiles.return_value=S_OK( [] )
        #     pu = PluginUtilities(transClient=tsMock, fc=self.fcMock, dataManager=MagicMock(), rmClient=MagicMock() )
        #     res = pu.getRAWAncestorsForRun( 1 )
        #     self.assertEqual( res, 0 )

        # some files
        #     tsMock = MagicMock()
        #     tsMock.getTransformationFiles.return_value = S_OK( [{'LFN':'this/is/at_1', 'Status':'Unused'},
        #                                                         {'LFN':'this/is/not_here', 'Status':'MissingInFC'}] )
        #     bkMock = MagicMock()
        #     bkMock.getFileAncestors.return_value =
        #     pu = PluginUtilities( transClient=tsMock, fc=self.fcMock, dataManager=MagicMock(), rmClient=MagicMock() )
        #     res = pu.getRAWAncestorsForRun( 1 )
        #     self.assertEqual( res, 0 )
        pass


#############################################################################
#############################################################################
if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ClientTestCase)
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TaskManagerSuccess))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TransformationClientSuccess))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(PluginsUtilitiesSuccess))
    testResult = unittest.TextTestRunner(verbosity=2).run(suite)
