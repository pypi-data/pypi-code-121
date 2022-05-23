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
"""Unittest for: LHCbDIRAC.AccountingSystem.private.Plotters.JobStepPlotter.

JobStepPlotter.__bases__:
  DIRAC.AccountingSystem.private.Plotters.BaseReporter

We are assuming there is a solid test of __bases__, we are not testing them
here and assuming they work fine.

IMPORTANT: the test MUST be pylint compliant !
"""
import mock
import unittest


class JobStepPlotterTestCase(unittest.TestCase):
    """JobStepPlotterTestCase."""

    moduleTested = None
    classsTested = None

    def mockModuleTested(self, moduleTested):
        """Used to not redo the mocking done on the parent class ( if any )"""

        # Tries to get the mocks of the parent TestCases ( if any )
        for baseClass in self.__class__.__bases__:
            try:
                # pylint: disable=no-member
                moduleTested = baseClass.mockModuleTested(moduleTested)
            except TypeError:
                continue

        # And then makes its own mock
        class MockJobStep:
            # pylint: disable=missing-docstring,no-init
            definitionKeyFields = (
                "JobGroup",
                "RunNumber",
                "EventType",
                "ProcessingType",
                "ProcessingStep",
                "Site",
                "FinalStepState",
            )

        moduleTested.JobStep = mock.Mock(return_value=MockJobStep())

        return moduleTested

    def setUp(self):
        """Setup the test case."""

        import LHCbDIRAC.AccountingSystem.private.Plotters.JobStepPlotter as moduleTested

        self.moduleTested = self.mockModuleTested(moduleTested)
        self.classsTested = self.moduleTested.JobStepPlotter

    def tearDown(self):
        """Tear down the test case."""

        del self.moduleTested
        del self.classsTested


# ...............................................................................


class JobStepPlotterUnitTest(JobStepPlotterTestCase):
    """JobStepPlotterUnitTest.

    <constructor>
     - test_instantiate
    <class variables>
     - test_typeName
     - test_typeKeyFields
     - test_reportCPUEfficiencyName
     - test_reportCPUUsageName
     - test_reportPieCPUTimeName
     - test_reportCumulativeCPUTimeName
     - test_reportNormCPUTimeName
     - test_reportCumulativeNormCPUTimeName
     - test_reportPieNormCPUTimeName
     - test_reportInputDataName
     - test_reportCumulativeInputDataName
     - test_reportPieInputDataName
     - test_reportOutputDataName
     - test_reportCumulativeOutputDataName
     - test_reportPieOutputDataName
     - test_reportInputEventsName
     - test_reportCumulativeInputEventsName
     - test_reportPieInputEventsName
     - test_reportOutputEventsName
     - test_reportCumulativeOutputEventsName
     - test_reportPieOutputEventsName
     - test_reportInputEventsPerOutputEventsName
     - test_reportCPUTimePerOutputEventsName
     - test_reportCPUTimePerInputEventsName
    <methods>
    """

    def test_instantiate(self):
        """tests that we can instantiate one object of the tested class."""
        obj = self.classsTested(None, None)
        self.assertEqual("JobStepPlotter", obj.__class__.__name__, msg="Expected JobStepPlotter object")

    def test_typeName(self):
        """test the class variable "_typeName"."""
        obj = self.classsTested(None, None)
        self.assertEqual(obj._typeName, "JobStep", msg="Expected JobStep as value")

    def test_typeKeyFields(self):
        """test the class variable "_typeKeyFields"."""
        obj = self.classsTested(None, None)
        self.assertEqual(
            obj._typeKeyFields,
            ["JobGroup", "RunNumber", "EventType", "ProcessingType", "ProcessingStep", "Site", "FinalStepState"],
            msg="Expected keys from MockJobStep",
        )

    def test_reportCPUEfficiencyName(self):
        """test the class variable "_reportCPUEfficiencyName"."""
        obj = self.classsTested(None, None)
        self.assertEqual(obj._reportCPUEfficiencyName, "CPU efficiency", msg="Expected CPU efficiency as value")

    def test_reportCPUUsageName(self):
        """test the class variable "_reportCPUUsageName"."""
        obj = self.classsTested(None, None)
        self.assertEqual(obj._reportCPUUsageName, "CPU time", msg="Expected CPU time as value")

    def test_reportPieCPUTimeName(self):
        """test the class variable "_reportPieCPUTimeName"."""
        obj = self.classsTested(None, None)
        self.assertEqual(
            obj._reportPieCPUTimeName, "Pie plot of CPU time", msg="Expected Pie plot of CPU time as value"
        )

    def test_reportCumulativeCPUTimeName(self):
        """test the class variable "_reportCumulativeCPUTimeName"."""
        obj = self.classsTested(None, None)
        self.assertEqual(
            obj._reportCumulativeCPUTimeName, "Cumulative CPU time", msg="Expected Cumulative CPU time as value"
        )

    def test_reportNormCPUTimeName(self):
        """test the class variable "_reportNormCPUTimeName"."""
        obj = self.classsTested(None, None)
        self.assertEqual(obj._reportNormCPUTimeName, "NormCPU time", msg="Expected NormCPU time as value")

    def test_reportCumulativeNormCPUTimeName(self):
        """test the class variable "_reportCumulativeNormCPUTimeName"."""
        obj = self.classsTested(None, None)
        self.assertEqual(
            obj._reportCumulativeNormCPUTimeName,
            "Cumulative normalized CPU time",
            msg="Expected Cumulative normalized CPU time as value",
        )

    def test_reportPieNormCPUTimeName(self):
        """test the class variable "_reportPieNormCPUTimeName"."""
        obj = self.classsTested(None, None)
        self.assertEqual(
            obj._reportPieNormCPUTimeName, "Pie plot of NormCPU time", msg="Expected Pie plot of NormCPU time as value"
        )

    def test_reportInputDataName(self):
        """test the class variable "_reportInputDataName"."""
        obj = self.classsTested(None, None)
        self.assertEqual(obj._reportInputDataName, "Input Data", msg="Expected Input Data as value")

    def test_reportCumulativeInputDataName(self):
        """test the class variable "_reportCumulativeInputDataName"."""
        obj = self.classsTested(None, None)
        self.assertEqual(
            obj._reportCumulativeInputDataName, "Cumulative Input Data", msg="Expected Cumulative Input Data as value"
        )

    def test_reportPieInputDataName(self):
        """test the class variable "_reportPieInputDataName"."""
        obj = self.classsTested(None, None)
        self.assertEqual(
            obj._reportPieInputDataName, "Pie plot of Input Data", msg="Expected Pie plot of Input Data as value"
        )

    def test_reportOutputDataName(self):
        """test the class variable "_reportOutputDataName"."""
        obj = self.classsTested(None, None)
        self.assertEqual(obj._reportOutputDataName, "Output Data", msg="Expected Output Data as value")

    def test_reportCumulativeOutputDataName(self):
        """test the class variable "_reportCumulativeOutputDataName"."""
        obj = self.classsTested(None, None)
        self.assertEqual(
            obj._reportCumulativeOutputDataName, "Cumulative OutputData", msg="Expected Cumulative OutputData as value"
        )

    def test_reportPieOutputDataName(self):
        """test the class variable "_reportPieOutputDataName"."""
        obj = self.classsTested(None, None)
        self.assertEqual(
            obj._reportPieOutputDataName, "Pie plot of Output Data", msg="Expected Pie plot of Output Data as value"
        )

    def test_reportInputEventsName(self):
        """test the class variable "_reportInputEventsName"."""
        obj = self.classsTested(None, None)
        self.assertEqual(obj._reportInputEventsName, "Input Events", msg="Expected Input Events as value")

    def test_reportCumulativeInputEventsName(self):
        """test the class variable "_reportCumulativeInputEventsName"."""
        obj = self.classsTested(None, None)
        self.assertEqual(
            obj._reportCumulativeInputEventsName,
            "Cumulative Input Events",
            msg="Expected Cumulative Input Events as value",
        )

    def test_reportPieInputEventsName(self):
        """test the class variable "_reportPieInputEventsName"."""
        obj = self.classsTested(None, None)
        self.assertEqual(
            obj._reportPieInputEventsName, "Pie plot of Input Events", msg="Expected Pie plot of Input Events as value"
        )

    def test_reportOutputEventsName(self):
        """test the class variable "_reportOutputEventsName"."""
        obj = self.classsTested(None, None)
        self.assertEqual(obj._reportOutputEventsName, "Output Events", msg="Expected Output Events as value")

    def test_reportCumulativeOutputEventsName(self):
        """test the class variable "_reportCumulativeOutputEventsName"."""
        obj = self.classsTested(None, None)
        self.assertEqual(
            obj._reportCumulativeOutputEventsName,
            "Cumulative Output Events",
            msg="Expected Cumulative Output Events as value",
        )

    def test_reportPieOutputEventsName(self):
        """test the class variable "_reportPieOutputEventsName"."""
        obj = self.classsTested(None, None)
        self.assertEqual(
            obj._reportPieOutputEventsName,
            "Pie plot of Output Events",
            msg="Expected Pie plot of Output Events as value",
        )

    def test_reportInputEventsPerOutputEventsName(self):
        """test the class variable "_reportInputEventsPerOutputEventsName"."""
        obj = self.classsTested(None, None)
        self.assertEqual(
            obj._reportInputEventsPerOutputEventsName,
            "Input/Output Events",
            msg="Expected Input/Output Events as value",
        )

    def test_reportCPUTimePerOutputEventsName(self):
        """test the class variable "_reportCPUTimePerOutputEventsName"."""
        obj = self.classsTested(None, None)
        self.assertEqual(
            obj._reportCPUTimePerOutputEventsName,
            "CPUTime/Output Events",
            msg="Expected CPUTime/Output Events as value",
        )

    def test_reportCPUTimePerInputEventsName(self):
        """test the class variable "_reportCPUTimePerInputEventsName"."""
        obj = self.classsTested(None, None)
        self.assertEqual(
            obj._reportCPUTimePerInputEventsName, "CPUTime/Input Events", msg="Expected CPUTime/Input Events as value"
        )

    # FIXME: add crashes !


################################################################################


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(JobStepPlotterTestCase)
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(JobStepPlotterUnitTest))
    testResult = unittest.TextTestRunner(verbosity=2).run(suite)
