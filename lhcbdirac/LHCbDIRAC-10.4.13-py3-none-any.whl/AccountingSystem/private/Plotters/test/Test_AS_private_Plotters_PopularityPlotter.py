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
"""Unittest for: LHCbDIRAC.AccountingSystem.private.Plotters.PopularityPlotter.

PopularityPlotter.__bases__:
  DIRAC.AccountingSystem.private.Plotters.BaseReporter

We are assuming there is a solid test of __bases__, we are not testing them
here and assuming they work fine.

IMPORTANT: the test MUST be pylint compliant !
"""
# pylint: disable=protected-access

import unittest
from decimal import Decimal

import mock


class PopularityPlotterTestCase(unittest.TestCase):
    """PopularityPlotterTestCase."""

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
        class MockPopularity(object):
            # pylint: disable=missing-docstring,no-init
            definitionKeyFields = (
                "DataType",
                "Activity",
                "FileType",
                "Production",
                "ProcessingPass",
                "Conditions",
                "EventType",
                "StorageElement",
            )

        moduleTested.Popularity = mock.Mock(return_value=MockPopularity())

        return moduleTested

    def setUp(self):
        """Setup the test case."""

        import LHCbDIRAC.AccountingSystem.private.Plotters.PopularityPlotter as moduleTested

        self.moduleTested = self.mockModuleTested(moduleTested)
        self.classsTested = self.moduleTested.PopularityPlotter

    def tearDown(self):
        """Tear down the test case."""

        del self.moduleTested
        del self.classsTested


# ...............................................................................


class PopularityPlotterUnitTest(PopularityPlotterTestCase):
    """PopularityPlotterUnitTest.

    <constructor>
     - test_instantiate
    <class variables>
     - test_typeName
     - test_typeKeyFields
     - test_reportDataUsageName
     - test_reportNormalizedDataUsageName
    <methods>
     - test_reportDataUsage
     - test_reportNormalizedDataUsage
     - test_plotDataUsage
     - test_plotNormalizedDataUsage
    """

    def test_instantiate(self):
        """tests that we can instantiate one object of the tested class."""
        obj = self.classsTested(None, None)
        self.assertEqual("PopularityPlotter", obj.__class__.__name__)

    def test_typeName(self):
        """test the class variable "_typeName"."""
        obj = self.classsTested(None, None)
        self.assertEqual(obj._typeName, "Popularity")

    def test_typeKeyFields(self):
        """test the class variable "_typeKeyFields"."""
        obj = self.classsTested(None, None)
        self.assertEqual(
            obj._typeKeyFields,
            [
                "DataType",
                "Activity",
                "FileType",
                "Production",
                "ProcessingPass",
                "Conditions",
                "EventType",
                "StorageElement",
            ],
        )

    def test_reportDataUsageName(self):
        """test the class variable "_reportDataUsageName"."""
        obj = self.classsTested(None, None)
        self.assertEqual(obj._reportDataUsageName, "Data Usage")

    def test_reportNormalizedDataUsageName(self):
        """test the class variable "_reportNormalizedDataUsageName"."""
        obj = self.classsTested(None, None)
        self.assertEqual(obj._reportNormalizedDataUsageName, "Normalized Data Usage")

    def test_reportDataUsage(self):
        """test the method "_reportDataUsage"."""

        mockAccountingDB = mock.MagicMock()
        mockAccountingDB._getConnection.return_value = {"OK": False, "Message": "No connection"}
        mockAccountingDB.retrieveBucketedData.return_value = {"OK": True, "Value": []}
        mockAccountingDB.calculateBucketLengthForTime.return_value = "BucketLength"
        obj = self.classsTested(mockAccountingDB, None)

        res = obj._reportDataUsage(
            {"groupingFields": [0, ["mehh"], "blah"], "startTime": "startTime", "endTime": "endTime", "condDict": {}}
        )
        #     self.assertEqual( res[ 'OK' ], False )
        #     self.assertEqual( res[ 'Message' ], 'No connection' )

        # Changed mocked to run over different lines of code
        mockAccountingDB._getConnection.return_value = {"OK": True, "Value": []}
        res = obj._reportDataUsage(
            {"groupingFields": [0, ["mehh"], "blah"], "startTime": "startTime", "endTime": "endTime", "condDict": {}}
        )
        self.assertEqual(res["OK"], True)
        self.assertEqual(
            res["Value"], {"graphDataDict": {}, "data": {}, "unit": "files", "granularity": "BucketLength"}
        )

        mockedData = (
            ("90000000", 1355616000, 86400, Decimal("123456.789")),
            ("90000000", 1355702400, 86400, Decimal("78901.2345")),
        )
        mockAccountingDB.retrieveBucketedData.return_value = {"OK": True, "Value": mockedData}
        mockAccountingDB.calculateBucketLengthForTime.return_value = 86400

        res = obj._reportDataUsage(
            {
                "groupingFields": ("%s", ["EventType"]),
                "startTime": 1355663249.0,
                "endTime": 1355749690.0,
                "condDict": {"EventType": "90000000"},
            }
        )
        self.assertEqual(res["OK"], True)
        self.assertEqual(
            res["Value"],
            {
                "graphDataDict": {"90000000": {1355616000: 123.456789, 1355702400: 78.901234500000001}},
                "data": {"90000000": {1355616000: 123456.789, 1355702400: 78901.234500000006}},
                "unit": "kfiles",
                "granularity": 86400,
            },
        )

    def test_reportNormalizedDataUsage(self):
        """test the method "_reportNormalizedDataUsage"."""

        mockAccountingDB = mock.Mock()
        mockAccountingDB._getConnection.return_value = {"OK": False, "Message": "No connection"}
        mockAccountingDB.retrieveBucketedData.return_value = {"OK": True, "Value": []}
        mockAccountingDB.calculateBucketLengthForTime.return_value = "BucketLength"
        obj = self.classsTested(mockAccountingDB, None)

        #     res = obj._reportNormalizedDataUsage( { 'groupingFields' : [ 0, [ 'mehh' ], 'blah' ],
        #                                             'startTime'      : 'startTime',
        #                                             'endTime'        : 'endTime',
        #                                             'condDict'       : {}
        #                                            } )
        #     self.assertEqual( res[ 'OK' ], False )
        #     self.assertEqual( res[ 'Message' ], 'No connection' )

        # Changed mocked to run over different lines of code
        mockAccountingDB._getConnection.return_value = {"OK": True, "Value": []}
        res = obj._reportNormalizedDataUsage(
            {"groupingFields": [0, ["mehh"], "blah"], "startTime": "startTime", "endTime": "endTime", "condDict": {}}
        )
        self.assertEqual(res["OK"], True)
        self.assertEqual(
            res["Value"], {"graphDataDict": {}, "data": {}, "unit": "files", "granularity": "BucketLength"}
        )

        mockedData = (
            ("90000000", 1355616000, 86400, Decimal("123456.789")),
            ("90000000", 1355702400, 86400, Decimal("78901.2345")),
            ("90000001", 1355616000, 86400, Decimal("223456.789")),
            ("90000001", 1355702400, 86400, Decimal("148901.2345")),
        )
        mockAccountingDB.retrieveBucketedData.return_value = {"OK": True, "Value": mockedData}
        mockAccountingDB.calculateBucketLengthForTime.return_value = 86400

        res = obj._reportNormalizedDataUsage(
            {
                "groupingFields": ("%s", ["EventType"]),
                "startTime": 1355663249.0,
                "endTime": 1355749690.0,
                "condDict": {"StorageElement": "CERN"},
            }
        )
        self.assertEqual(res["OK"], True)
        self.assertEqual(
            res["Value"],
            {
                "graphDataDict": {
                    "90000001": {1355616000: 223.45678899999999, 1355702400: 148.90123449999999},
                    "90000000": {1355616000: 123.456789, 1355702400: 78.901234500000001},
                },
                "data": {
                    "90000001": {1355616000: 223456.78899999999, 1355702400: 148901.23449999999},
                    "90000000": {1355616000: 123456.789, 1355702400: 78901.234500000006},
                },
                "unit": "kfiles",
                "granularity": 86400,
            },
        )


# ...............................................................................


class PopularityPlotterUnitTestCrashes(PopularityPlotterTestCase):
    """PopularityPlotterUnitTestCrashes.

    <constructor>
     - test_instantiate
    <class variables>
    <methods>
    - test_reportDataUsage
    - test_reportNormalizedDataUsage
    - test_plotDataUsage
    - test_plotNormalizedDataUsage
    """

    def test_instantiate(self):
        """test the constructor."""

        self.assertRaises(TypeError, self.classsTested)
        self.assertRaises(TypeError, self.classsTested, None)
        self.assertRaises(TypeError, self.classsTested, None, None, None, None)

        self.assertRaises(TypeError, self.classsTested, extraArgs=None)
        self.assertRaises(TypeError, self.classsTested, None, extraArgs=None)
        self.assertRaises(TypeError, self.classsTested, None, None, None, extraArgs=None)

    def test_reportDataUsage(self):
        """test the method "_reportDataUsage"."""

        mockAccountingDB = mock.Mock()
        mockAccountingDB._getConnection.return_value = {"OK": False, "Message": "No connection"}
        mockAccountingDB.retrieveBucketedData.return_value = {"OK": True, "Value": []}
        mockAccountingDB.calculateBucketLengthForTime.return_value = "BucketLength"
        obj = self.classsTested(mockAccountingDB, None)

        self.assertRaises(KeyError, obj._reportDataUsage, {})
        self.assertRaises(IndexError, obj._reportDataUsage, {"groupingFields": []})
        self.assertRaises(TypeError, obj._reportDataUsage, {"groupingFields": [1, 2]})
        self.assertRaises(TypeError, obj._reportDataUsage, {"groupingFields": [1, [2]]})
        self.assertRaises(TypeError, obj._reportDataUsage, {"groupingFields": ["1", "2"]})
        self.assertRaises(KeyError, obj._reportDataUsage, {"groupingFields": ["1", [2]]})
        self.assertRaises(KeyError, obj._reportDataUsage, {"groupingFields": ["1", [2, 2]], "startTime": None})
        self.assertRaises(
            KeyError, obj._reportDataUsage, {"groupingFields": ["1", [2, 2]], "startTime": None, "endTime": None}
        )
        self.assertRaises(
            TypeError,
            obj._reportDataUsage,
            {"groupingFields": ["1", [2, 2]], "startTime": None, "endTime": None, "condDict": None},
        )

    def test_reportNormalizedDataUsage(self):
        """test the method "_reportNormalizedDataUsage"."""

        mockAccountingDB = mock.Mock()
        mockAccountingDB._getConnection.return_value = {"OK": False, "Message": "No connection"}
        mockAccountingDB.retrieveBucketedData.return_value = {"OK": True, "Value": []}
        mockAccountingDB.calculateBucketLengthForTime.return_value = "BucketLength"
        obj = self.classsTested(mockAccountingDB, None)

        self.assertRaises(KeyError, obj._reportNormalizedDataUsage, {})
        self.assertRaises(IndexError, obj._reportNormalizedDataUsage, {"groupingFields": []})
        self.assertRaises(TypeError, obj._reportNormalizedDataUsage, {"groupingFields": [1, 2]})
        self.assertRaises(TypeError, obj._reportNormalizedDataUsage, {"groupingFields": [1, [2]]})
        self.assertRaises(TypeError, obj._reportNormalizedDataUsage, {"groupingFields": ["1", "2"]})
        self.assertRaises(KeyError, obj._reportNormalizedDataUsage, {"groupingFields": ["1", [2]]})
        self.assertRaises(
            KeyError, obj._reportNormalizedDataUsage, {"groupingFields": ["1", [2, 2]], "startTime": None}
        )
        self.assertRaises(
            KeyError,
            obj._reportNormalizedDataUsage,
            {"groupingFields": ["1", [2, 2]], "startTime": None, "endTime": None},
        )
        self.assertRaises(
            TypeError,
            obj._reportNormalizedDataUsage,
            {"groupingFields": ["1", [2, 2]], "startTime": None, "endTime": None, "condDict": None},
        )

    def test_plotDataUsage(self):
        """test the method "_plotDataUsage"."""

        obj = self.classsTested(None, None)
        self.assertRaises(TypeError, obj._plotDataUsage, None, None, None)
        self.assertRaises(KeyError, obj._plotDataUsage, {}, None, None)
        self.assertRaises(KeyError, obj._plotDataUsage, {"startTime": "startTime"}, None, None)
        self.assertRaises(TypeError, obj._plotDataUsage, {"startTime": "startTime", "endTime": "endTime"}, None, None)
        self.assertRaises(KeyError, obj._plotDataUsage, {"startTime": "startTime", "endTime": "endTime"}, {}, None)
        self.assertRaises(
            KeyError,
            obj._plotDataUsage,
            {"startTime": "startTime", "endTime": "endTime"},
            {"granularity": "granularity"},
            None,
        )
        self.assertRaises(
            KeyError,
            obj._plotDataUsage,
            {"startTime": "startTime", "endTime": "endTime", "grouping": "grouping"},
            {"granularity": "granularity"},
            None,
        )
        self.assertRaises(
            KeyError,
            obj._plotDataUsage,
            {"startTime": "startTime", "endTime": "endTime", "grouping": "grouping"},
            {"granularity": "granularity", "graphDataDict": "graphDataDict"},
            None,
        )

    def test_plotNormalizedDataUsage(self):
        """test the method "_plotNormalizedDataUsage"."""

        obj = self.classsTested(None, None)
        self.assertRaises(TypeError, obj._plotNormalizedDataUsage, None, None, None)
        self.assertRaises(KeyError, obj._plotNormalizedDataUsage, {}, None, None)
        self.assertRaises(KeyError, obj._plotNormalizedDataUsage, {"startTime": "startTime"}, None, None)
        self.assertRaises(
            TypeError, obj._plotNormalizedDataUsage, {"startTime": "startTime", "endTime": "endTime"}, None, None
        )
        self.assertRaises(
            KeyError, obj._plotNormalizedDataUsage, {"startTime": "startTime", "endTime": "endTime"}, {}, None
        )
        self.assertRaises(
            KeyError,
            obj._plotNormalizedDataUsage,
            {"startTime": "startTime", "endTime": "endTime"},
            {"granularity": "granularity"},
            None,
        )
        self.assertRaises(
            KeyError,
            obj._plotNormalizedDataUsage,
            {"startTime": "startTime", "endTime": "endTime", "grouping": "grouping"},
            {"granularity": "granularity"},
            None,
        )
        self.assertRaises(
            KeyError,
            obj._plotNormalizedDataUsage,
            {"startTime": "startTime", "endTime": "endTime", "grouping": "grouping"},
            {"granularity": "granularity", "graphDataDict": "graphDataDict"},
            None,
        )


################################################################################


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(PopularityPlotterTestCase)
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(PopularityPlotterUnitTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(PopularityPlotterUnitTestCrashes))
    testResult = unittest.TextTestRunner(verbosity=2).run(suite)
