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
"""Unittest for:
LHCbDIRAC.AccountingSystem.private.Plotters.DataStoragePlotter.

DataStoragePlotter.__bases__:
  DIRAC.AccountingSystem.private.Plotters.BaseReporter

We are assuming there is a solid test of __bases__, we are not testing them
here and assuming they work fine.

IMPORTANT: the test MUST be pylint compliant !
"""
# pylint: disable=protected-access

import unittest
import math
import operator

from decimal import Decimal

import mock

from PIL import Image
from functools import reduce


def compare(file1Path, file2Path):
    """Function used to compare two plots.

    returns 0.0 if both are identical
    """

    # Crops image to remove the "Generated on xxxx UTC" string
    image1 = Image.open(file1Path).crop((0, 0, 800, 570))
    image2 = Image.open(file2Path).crop((0, 0, 800, 570))
    h1 = image1.histogram()
    h2 = image2.histogram()
    rms = math.sqrt(reduce(operator.add, map(lambda a, b: (a - b) ** 2, h1, h2)) / len(h1))
    return rms


# ...............................................................................


class DataStoragePlotterTestCase(unittest.TestCase):
    """DataStoragePlotterTestCase."""

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
        class MockDataStorage(object):
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

        moduleTested.DataStorage = mock.Mock(return_value=MockDataStorage())

        return moduleTested

    def setUp(self):
        """Setup the test case."""

        import LHCbDIRAC.AccountingSystem.private.Plotters.DataStoragePlotter as moduleTested

        self.moduleTested = self.mockModuleTested(moduleTested)
        self.classsTested = self.moduleTested.DataStoragePlotter

    def tearDown(self):
        """Tear down the test case."""

        del self.moduleTested
        del self.classsTested


# ...............................................................................


class DataStoragePlotterUnitTest(DataStoragePlotterTestCase):
    """DataStoragePlotterUnitTest.

    <constructor>
     - test_instantiate
    <class variables>
     - test_typeName
     - test_typeKeyFields
     - test_noSEtypeKeyFields
     - test_noSEGrouping
     - test_reportCatalogSpaceName
     - test_reportCatalogFilesName
     - test_reportPhysicalSpaceName
     - test_reportPhysicalFilesName
    <methods>
     - test_reportCatalogSpace
     - test_reportCatalogFiles
     - test_reportPhysicalSpace
     - test_reportPhysicalFiles
     - test_plotCatalogSpace
     - test_plotCatalogFiles
     - test_plotPhysicalSpace
     - test_plotPhysicalFiles
    """

    def test_instantiate(self):
        """tests that we can instantiate one object of the tested class."""
        obj = self.classsTested(None, None)
        self.assertEqual("DataStoragePlotter", obj.__class__.__name__)

    def test_typeName(self):
        """test the class variable "_typeName"."""
        obj = self.classsTested(None, None)
        self.assertEqual(obj._typeName, "DataStorage")

    #   def test_typeKeyFields( self ):
    #     ''' test the class variable "_typeKeyFields"
    #     '''
    #     obj = self.classsTested( None, None )
    #     self.assertEqual( obj._typeKeyFields, [ 'DataType', 'Activity', 'FileType',
    #                                             'Production', 'ProcessingPass',
    #                                             'Conditions', 'EventType', 'StorageElement' ] )

    def test_reportCatalogSpaceName(self):
        """test the class variable "_reportCatalogSpaceName"."""
        obj = self.classsTested(None, None)
        self.assertEqual(obj._reportCatalogSpaceName, "LFN size")

    def test_reportCatalogFilesName(self):
        """test the class variable "_reportCatalogFilesName"."""
        obj = self.classsTested(None, None)
        self.assertEqual(obj._reportCatalogFilesName, "LFN files")

    def test_reportPhysicalSpaceName(self):
        """test the class variable "_reportPhysicalSpaceName"."""
        obj = self.classsTested(None, None)
        self.assertEqual(obj._reportPhysicalSpaceName, "PFN size")

    def test_reportPhysicalFilesName(self):
        """test the class variable "_reportPhysicalFilesName"."""
        obj = self.classsTested(None, None)
        self.assertEqual(obj._reportPhysicalFilesName, "PFN files")

    def test_reportCatalogSpace(self):
        """test the method "_reportCatalogSpace"."""

        mockAccountingDB = mock.Mock()
        mockAccountingDB._getConnection.return_value = {"OK": False, "Message": "No connection"}
        mockAccountingDB.retrieveBucketedData.return_value = {"OK": True, "Value": []}
        mockAccountingDB.calculateBucketLengthForTime.return_value = "BucketLength"
        obj = self.classsTested(mockAccountingDB, None)

        res = obj._reportCatalogSpace({"grouping": "StorageElement"})
        self.assertEqual(res["OK"], False, msg="Rejected StorageElement grouping")
        self.assertEqual(res["Message"], "Grouping by storage element when requesting lfn info makes no sense")

        res = obj._reportCatalogSpace(
            {
                "grouping": "NextToABeer",
                "groupingFields": [0, ["mehh"], "blah"],
                "startTime": "startTime",
                "endTime": "endTime",
                "condDict": {},
            }
        )
        #     self.assertEqual( res[ 'OK' ], False )
        #     self.assertEqual( res[ 'Message' ], 'No connection' )

        # Changed mocked to run over different lines of code
        mockAccountingDB._getConnection.return_value = {"OK": True, "Value": []}
        res = obj._reportCatalogSpace(
            {
                "grouping": "NextToABeer",
                "groupingFields": [0, ["mehh"], "blah"],
                "startTime": "startTime",
                "endTime": "endTime",
                "condDict": {},
            }
        )
        self.assertEqual(res["OK"], True)
        self.assertEqual(res["Value"], {"graphDataDict": {}, "data": {}, "unit": "MB", "granularity": "BucketLength"})

        mockedData = (
            ("Full stream", 1355616000, 86400, Decimal("935388524246.91630989384787")),
            ("Full stream", 1355702400, 86400, Decimal("843844487074.82197482051816")),
        )
        mockAccountingDB.retrieveBucketedData.return_value = {"OK": True, "Value": mockedData}
        mockAccountingDB.calculateBucketLengthForTime.return_value = 86400

        res = obj._reportCatalogSpace(
            {
                "grouping": "EventType",
                "groupingFields": ("%s", ["EventType"]),
                "startTime": 1355663249.0,
                "endTime": 1355749690.0,
                "condDict": {"EventType": "Full stream"},
            }
        )
        self.assertEqual(res["OK"], True)
        self.assertEqual(
            res["Value"],
            {
                "graphDataDict": {"Full stream": {1355616000: 935.38852424691629, 1355702400: 843.84448707482204}},
                "data": {"Full stream": {1355616000: 935388.52424691629, 1355702400: 843844.48707482207}},
                "unit": "GB",
                "granularity": 86400,
            },
        )

    def test_reportCatalogFiles(self):
        """test the method "_reportCatalogFiles"."""

        mockAccountingDB = mock.Mock()
        mockAccountingDB._getConnection.return_value = {"OK": False, "Message": "No connection"}
        mockAccountingDB.retrieveBucketedData.return_value = {"OK": True, "Value": []}
        mockAccountingDB.calculateBucketLengthForTime.return_value = "BucketLength"
        obj = self.classsTested(mockAccountingDB, None)

        res = obj._reportCatalogFiles({"grouping": "StorageElement"})
        self.assertEqual(res["OK"], False)
        self.assertEqual(res["Message"], "Grouping by storage element when requesting lfn info makes no sense")

        res = obj._reportCatalogFiles(
            {
                "grouping": "NextToABeer",
                "groupingFields": [0, ["mehh"], "blah"],
                "startTime": "startTime",
                "endTime": "endTime",
                "condDict": {},
            }
        )
        #     self.assertEqual( res[ 'OK' ], False )
        #     self.assertEqual( res[ 'Message' ], 'No connection' )

        # Changed mocked to run over different lines of code
        mockAccountingDB._getConnection.return_value = {"OK": True, "Value": []}
        res = obj._reportCatalogFiles(
            {
                "grouping": "NextToABeer",
                "groupingFields": [0, ["mehh"], "blah"],
                "startTime": "startTime",
                "endTime": "endTime",
                "condDict": {},
            }
        )
        self.assertEqual(res["OK"], True, msg="Expected S_OK")
        self.assertEqual(
            res["Value"], {"graphDataDict": {}, "data": {}, "unit": "files", "granularity": "BucketLength"}
        )

        mockedData = (
            ("Full stream", 1355616000, 86400, Decimal("420.47885754501202")),
            ("Full stream", 1355702400, 86400, Decimal("380.35170637810842")),
        )
        mockAccountingDB.retrieveBucketedData.return_value = {"OK": True, "Value": mockedData}
        mockAccountingDB.calculateBucketLengthForTime.return_value = 86400

        res = obj._reportCatalogFiles(
            {
                "grouping": "EventType",
                "groupingFields": ("%s", ["EventType"]),
                "startTime": 1355663249.0,
                "endTime": 1355749690.0,
                "condDict": {"EventType": "Full stream"},
            }
        )
        self.assertEqual(res["OK"], True)
        self.assertEqual(
            res["Value"],
            {
                "graphDataDict": {"Full stream": {1355616000: 420.47885754501203, 1355702400: 380.35170637810842}},
                "data": {"Full stream": {1355616000: 420.47885754501203, 1355702400: 380.35170637810842}},
                "unit": "files",
                "granularity": 86400,
            },
        )

    def test_reportPhysicalSpace(self):
        """test the method "_reportPhysicalSpace"."""

        mockAccountingDB = mock.Mock()
        mockAccountingDB._getConnection.return_value = {"OK": False, "Message": "No connection"}
        mockAccountingDB.retrieveBucketedData.return_value = {"OK": True, "Value": []}
        mockAccountingDB.calculateBucketLengthForTime.return_value = "BucketLength"
        obj = self.classsTested(mockAccountingDB, None)

        res = obj._reportPhysicalSpace(
            {"groupingFields": [0, ["mehh"], "blah"], "startTime": "startTime", "endTime": "endTime", "condDict": {}}
        )
        #     self.assertEqual( res[ 'OK' ], False )
        #     self.assertEqual( res[ 'Message' ], 'No connection' )

        # Changed mocked to run over different lines of code
        mockAccountingDB._getConnection.return_value = {"OK": True, "Value": []}
        res = obj._reportPhysicalSpace(
            {
                "grouping": "NextToABeer",
                "groupingFields": [0, ["mehh"], "blah"],
                "startTime": "startTime",
                "endTime": "endTime",
                "condDict": {},
            }
        )
        self.assertEqual(res["OK"], True, msg="Expected S_OK")
        self.assertEqual(res["Value"], {"graphDataDict": {}, "data": {}, "unit": "MB", "granularity": "BucketLength"})

        mockedData = (
            ("Full stream", 1355616000, 86400, Decimal("14754501.202")),
            ("Full stream", 1355702400, 86400, Decimal("15237810.842")),
        )
        mockAccountingDB.retrieveBucketedData.return_value = {"OK": True, "Value": mockedData}
        mockAccountingDB.calculateBucketLengthForTime.return_value = 86400

        res = obj._reportPhysicalSpace(
            {
                "grouping": "EventType",
                "groupingFields": ("%s", ["EventType"]),
                "startTime": 1355663249.0,
                "endTime": 1355749690.0,
                "condDict": {"EventType": "Full stream"},
            }
        )
        self.assertEqual(res["OK"], True)
        self.assertEqual(
            res["Value"],
            {
                "graphDataDict": {"Full stream": {1355616000: 14.754501202, 1355702400: 15.237810842}},
                "data": {"Full stream": {1355616000: 14.754501202, 1355702400: 15.237810842}},
                "unit": "MB",
                "granularity": 86400,
            },
        )

    def test_reportPhysicalFiles(self):
        """test the method "_reportPhysicalFiles"."""

        mockAccountingDB = mock.Mock()
        mockAccountingDB._getConnection.return_value = {"OK": False, "Message": "No connection"}
        mockAccountingDB.retrieveBucketedData.return_value = {"OK": True, "Value": []}
        mockAccountingDB.calculateBucketLengthForTime.return_value = "BucketLength"
        obj = self.classsTested(mockAccountingDB, None)

        res = obj._reportPhysicalFiles(
            {"groupingFields": [0, ["mehh"], "blah"], "startTime": "startTime", "endTime": "endTime", "condDict": {}}
        )
        #     self.assertEqual( res[ 'OK' ], False )
        #     self.assertEqual( res[ 'Message' ], 'No connection' )

        # Changed mocked to run over different lines of code
        mockAccountingDB._getConnection.return_value = {"OK": True, "Value": []}
        res = obj._reportPhysicalFiles(
            {
                "grouping": "NextToABeer",
                "groupingFields": [0, ["mehh"], "blah"],
                "startTime": "startTime",
                "endTime": "endTime",
                "condDict": {},
            }
        )
        self.assertEqual(res["OK"], True, msg="Expected S_OK")
        self.assertEqual(
            res["Value"], {"graphDataDict": {}, "data": {}, "unit": "files", "granularity": "BucketLength"}
        )

        mockedData = (
            ("Full stream", 1355616000, 86400, Decimal("42.47885754501202")),
            ("Full stream", 1355702400, 86400, Decimal("38.35170637810842")),
        )
        mockAccountingDB.retrieveBucketedData.return_value = {"OK": True, "Value": mockedData}
        mockAccountingDB.calculateBucketLengthForTime.return_value = 86400

        res = obj._reportPhysicalFiles(
            {
                "grouping": "EventType",
                "groupingFields": ("%s", ["EventType"]),
                "startTime": 1355663249.0,
                "endTime": 1355749690.0,
                "condDict": {"EventType": "Full stream"},
            }
        )
        self.assertEqual(res["OK"], True)
        self.assertEqual(
            res["Value"],
            {
                "graphDataDict": {"Full stream": {1355616000: 42.47885754501202, 1355702400: 38.35170637810842}},
                "data": {"Full stream": {1355616000: 42.47885754501202, 1355702400: 38.35170637810842}},
                "unit": "files",
                "granularity": 86400,
            },
        )


# ...............................................................................


class DataStoragePlotterUnitTestCrashes(DataStoragePlotterTestCase):
    """DataStoragePlotterUnitTestCrashes.

    <constructor>
     - test_instantiate
    <class variables>
    <methods>
     - test_reportCatalogSpace
     - test_reportCatalogFiles
     - test_reportPhysicalSpace
     - test_reportPhysicalFiles
     - test_plotCatalogSpace
     - test_plotCatalogFiles
     - test_plotPhysicalSpace
     - test_plotPhysicalFiles
    """

    def test_instantiate(self):
        """test the constructor."""

        self.assertRaises(TypeError, self.classsTested)
        self.assertRaises(TypeError, self.classsTested, None)
        self.assertRaises(TypeError, self.classsTested, None, None, None, None)

        self.assertRaises(TypeError, self.classsTested, extraArgs=None)
        self.assertRaises(TypeError, self.classsTested, None, extraArgs=None)
        self.assertRaises(TypeError, self.classsTested, None, None, None, extraArgs=None)

    def test_reportCatalogSpace(self):
        """test the method "_reportCatalogSpace"."""

        mockAccountingDB = mock.Mock()
        mockAccountingDB._getConnection.return_value = {"OK": False, "Message": "No connection"}
        mockAccountingDB.retrieveBucketedData.return_value = {"OK": True, "Value": []}
        mockAccountingDB.calculateBucketLengthForTime.return_value = "BucketLength"
        obj = self.classsTested(mockAccountingDB, None)

        self.assertRaises(KeyError, obj._reportCatalogSpace, {})
        self.assertRaises(KeyError, obj._reportCatalogSpace, {"grouping": 1})
        self.assertRaises(IndexError, obj._reportCatalogSpace, {"grouping": 1, "groupingFields": []})
        self.assertRaises(TypeError, obj._reportCatalogSpace, {"grouping": 1, "groupingFields": [1, 2]})
        self.assertRaises(TypeError, obj._reportCatalogSpace, {"grouping": 1, "groupingFields": [1, [2]]})
        self.assertRaises(TypeError, obj._reportCatalogSpace, {"grouping": 1, "groupingFields": ["1", "2"]})
        self.assertRaises(KeyError, obj._reportCatalogSpace, {"grouping": 1, "groupingFields": ["1", [2]]})
        self.assertRaises(
            KeyError, obj._reportCatalogSpace, {"grouping": 1, "groupingFields": ["1", [2, 2]], "startTime": None}
        )
        self.assertRaises(
            KeyError,
            obj._reportCatalogSpace,
            {"grouping": 1, "groupingFields": ["1", [2, 2]], "startTime": None, "endTime": None},
        )
        self.assertRaises(
            TypeError,
            obj._reportCatalogSpace,
            {"grouping": 1, "groupingFields": ["1", [2, 2]], "startTime": None, "endTime": None, "condDict": None},
        )

    def test_reportCatalogFiles(self):
        """test the method "_reportCatalogFiles"."""

        mockAccountingDB = mock.Mock()
        mockAccountingDB._getConnection.return_value = {"OK": False, "Message": "No connection"}
        mockAccountingDB.retrieveBucketedData.return_value = {"OK": True, "Value": []}
        mockAccountingDB.calculateBucketLengthForTime.return_value = "BucketLength"
        obj = self.classsTested(mockAccountingDB, None)

        self.assertRaises(KeyError, obj._reportCatalogFiles, {})
        self.assertRaises(KeyError, obj._reportCatalogFiles, {"grouping": 1})
        self.assertRaises(IndexError, obj._reportCatalogFiles, {"grouping": 1, "groupingFields": []})
        self.assertRaises(TypeError, obj._reportCatalogFiles, {"grouping": 1, "groupingFields": [1, 2]})
        self.assertRaises(TypeError, obj._reportCatalogFiles, {"grouping": 1, "groupingFields": [1, [2]]})
        self.assertRaises(TypeError, obj._reportCatalogFiles, {"grouping": 1, "groupingFields": ["1", "2"]})
        self.assertRaises(KeyError, obj._reportCatalogFiles, {"grouping": 1, "groupingFields": ["1", [2]]})
        self.assertRaises(
            KeyError, obj._reportCatalogFiles, {"grouping": 1, "groupingFields": ["1", [2, 2]], "startTime": None}
        )
        self.assertRaises(
            KeyError,
            obj._reportCatalogFiles,
            {"grouping": 1, "groupingFields": ["1", [2, 2]], "startTime": None, "endTime": None},
        )
        self.assertRaises(
            TypeError,
            obj._reportCatalogFiles,
            {"grouping": 1, "groupingFields": ["1", [2, 2]], "startTime": None, "endTime": None, "condDict": None},
        )

    def test_reportPhysicalSpace(self):
        """test the method "_reportPhysicalSpace"."""

        mockAccountingDB = mock.Mock()
        mockAccountingDB._getConnection.return_value = {"OK": False, "Message": "No connection"}
        mockAccountingDB.retrieveBucketedData.return_value = {"OK": True, "Value": []}
        mockAccountingDB.calculateBucketLengthForTime.return_value = "BucketLength"
        obj = self.classsTested(mockAccountingDB, None)

        self.assertRaises(KeyError, obj._reportPhysicalSpace, {})
        self.assertRaises(IndexError, obj._reportPhysicalSpace, {"groupingFields": []})
        self.assertRaises(TypeError, obj._reportPhysicalSpace, {"groupingFields": [1, 2]})
        self.assertRaises(TypeError, obj._reportPhysicalSpace, {"groupingFields": [1, [2]]})
        self.assertRaises(TypeError, obj._reportPhysicalSpace, {"groupingFields": ["1", "2"]})
        self.assertRaises(KeyError, obj._reportPhysicalSpace, {"groupingFields": ["1", [2]]})
        self.assertRaises(KeyError, obj._reportPhysicalSpace, {"groupingFields": ["1", [2, 2]], "startTime": None})
        self.assertRaises(
            KeyError, obj._reportPhysicalSpace, {"groupingFields": ["1", [2, 2]], "startTime": None, "endTime": None}
        )
        self.assertRaises(
            TypeError,
            obj._reportPhysicalSpace,
            {"groupingFields": ["1", [2, 2]], "startTime": None, "endTime": None, "condDict": None},
        )

    def test_reportPhysicalFiles(self):
        """test the method "_reportPhysicalFiles"."""

        mockAccountingDB = mock.Mock()
        mockAccountingDB._getConnection.return_value = {"OK": False, "Message": "No connection"}
        mockAccountingDB.retrieveBucketedData.return_value = {"OK": True, "Value": []}
        mockAccountingDB.calculateBucketLengthForTime.return_value = "BucketLength"
        obj = self.classsTested(mockAccountingDB, None)

        self.assertRaises(KeyError, obj._reportPhysicalFiles, {})
        self.assertRaises(IndexError, obj._reportPhysicalFiles, {"groupingFields": []})
        self.assertRaises(TypeError, obj._reportPhysicalFiles, {"groupingFields": [1, 2]})
        self.assertRaises(TypeError, obj._reportPhysicalFiles, {"groupingFields": [1, [2]]})
        self.assertRaises(TypeError, obj._reportPhysicalFiles, {"groupingFields": ["1", "2"]})
        self.assertRaises(KeyError, obj._reportPhysicalFiles, {"groupingFields": ["1", [2]]})
        self.assertRaises(KeyError, obj._reportPhysicalFiles, {"groupingFields": ["1", [2, 2]], "startTime": None})
        self.assertRaises(
            KeyError, obj._reportPhysicalFiles, {"groupingFields": ["1", [2, 2]], "startTime": None, "endTime": None}
        )
        self.assertRaises(
            TypeError,
            obj._reportPhysicalFiles,
            {"groupingFields": ["1", [2, 2]], "startTime": None, "endTime": None, "condDict": None},
        )

    def test_plotCatalogSpace(self):
        """test the method "_plotCatalogSpace"."""

        obj = self.classsTested(None, None)
        self.assertRaises(TypeError, obj._plotCatalogSpace, None, None, None)
        self.assertRaises(KeyError, obj._plotCatalogSpace, {}, None, None)
        self.assertRaises(KeyError, obj._plotCatalogSpace, {"startTime": "startTime"}, None, None)
        self.assertRaises(
            TypeError, obj._plotCatalogSpace, {"startTime": "startTime", "endTime": "endTime"}, None, None
        )
        self.assertRaises(KeyError, obj._plotCatalogSpace, {"startTime": "startTime", "endTime": "endTime"}, {}, None)
        self.assertRaises(
            KeyError,
            obj._plotCatalogSpace,
            {"startTime": "startTime", "endTime": "endTime"},
            {"granularity": "granularity"},
            None,
        )
        self.assertRaises(
            KeyError,
            obj._plotCatalogSpace,
            {"startTime": "startTime", "endTime": "endTime", "grouping": "grouping"},
            {"granularity": "granularity"},
            None,
        )
        self.assertRaises(
            KeyError,
            obj._plotCatalogSpace,
            {"startTime": "startTime", "endTime": "endTime", "grouping": "grouping"},
            {"granularity": "granularity", "graphDataDict": "graphDataDict"},
            None,
        )

    def test_plotCatalogFiles(self):
        """test the method "_plotCatalogFiles"."""

        obj = self.classsTested(None, None)
        self.assertRaises(TypeError, obj._plotCatalogFiles, None, None, None)
        self.assertRaises(KeyError, obj._plotCatalogFiles, {}, None, None)
        self.assertRaises(KeyError, obj._plotCatalogFiles, {"startTime": "startTime"}, None, None)
        self.assertRaises(
            TypeError, obj._plotCatalogFiles, {"startTime": "startTime", "endTime": "endTime"}, None, None
        )
        self.assertRaises(KeyError, obj._plotCatalogFiles, {"startTime": "startTime", "endTime": "endTime"}, {}, None)
        self.assertRaises(
            KeyError,
            obj._plotCatalogFiles,
            {"startTime": "startTime", "endTime": "endTime"},
            {"granularity": "granularity"},
            None,
        )
        self.assertRaises(
            KeyError,
            obj._plotCatalogFiles,
            {"startTime": "startTime", "endTime": "endTime", "grouping": "grouping"},
            {"granularity": "granularity"},
            None,
        )
        self.assertRaises(
            KeyError,
            obj._plotCatalogFiles,
            {"startTime": "startTime", "endTime": "endTime", "grouping": "grouping"},
            {"granularity": "granularity", "graphDataDict": "graphDataDict"},
            None,
        )

    def test_plotPhysicalSpace(self):
        """test the method "_plotPhysicalSpace"."""

        obj = self.classsTested(None, None)
        self.assertRaises(TypeError, obj._plotPhysicalSpace, None, None, None)
        self.assertRaises(KeyError, obj._plotPhysicalSpace, {}, None, None)
        self.assertRaises(KeyError, obj._plotPhysicalSpace, {"startTime": "startTime"}, None, None)
        self.assertRaises(
            TypeError, obj._plotPhysicalSpace, {"startTime": "startTime", "endTime": "endTime"}, None, None
        )
        self.assertRaises(KeyError, obj._plotPhysicalSpace, {"startTime": "startTime", "endTime": "endTime"}, {}, None)
        self.assertRaises(
            KeyError,
            obj._plotPhysicalSpace,
            {"startTime": "startTime", "endTime": "endTime"},
            {"granularity": "granularity"},
            None,
        )
        self.assertRaises(
            KeyError,
            obj._plotPhysicalSpace,
            {"startTime": "startTime", "endTime": "endTime", "grouping": "grouping"},
            {"granularity": "granularity"},
            None,
        )
        self.assertRaises(
            KeyError,
            obj._plotPhysicalSpace,
            {"startTime": "startTime", "endTime": "endTime", "grouping": "grouping"},
            {"granularity": "granularity", "graphDataDict": "graphDataDict"},
            None,
        )

    def test_plotPhysicalFiles(self):
        """test the method "_plotPhysicalFiles"."""

        obj = self.classsTested(None, None)
        self.assertRaises(TypeError, obj._plotPhysicalFiles, None, None, None)
        self.assertRaises(KeyError, obj._plotPhysicalFiles, {}, None, None)
        self.assertRaises(KeyError, obj._plotPhysicalFiles, {"startTime": "startTime"}, None, None)
        self.assertRaises(
            TypeError, obj._plotPhysicalFiles, {"startTime": "startTime", "endTime": "endTime"}, None, None
        )
        self.assertRaises(KeyError, obj._plotPhysicalFiles, {"startTime": "startTime", "endTime": "endTime"}, {}, None)
        self.assertRaises(
            KeyError,
            obj._plotPhysicalFiles,
            {"startTime": "startTime", "endTime": "endTime"},
            {"granularity": "granularity"},
            None,
        )
        self.assertRaises(
            KeyError,
            obj._plotPhysicalFiles,
            {"startTime": "startTime", "endTime": "endTime", "grouping": "grouping"},
            {"granularity": "granularity"},
            None,
        )
        self.assertRaises(
            KeyError,
            obj._plotPhysicalFiles,
            {"startTime": "startTime", "endTime": "endTime", "grouping": "grouping"},
            {"granularity": "granularity", "graphDataDict": "graphDataDict"},
            None,
        )


################################################################################
#############################################################################


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(DataStoragePlotterTestCase)
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(DataStoragePlotterTestCase))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(DataStoragePlotterUnitTestCrashes))
    testResult = unittest.TextTestRunner(verbosity=2).run(suite)
