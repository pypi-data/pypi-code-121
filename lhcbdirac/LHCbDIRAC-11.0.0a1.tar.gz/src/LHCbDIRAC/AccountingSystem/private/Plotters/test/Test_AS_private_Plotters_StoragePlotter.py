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
"""Unittest for: LHCbDIRAC.AccountingSystem.private.Plotters.StoragePlotter.

StoragePlotter.__bases__:
  DIRAC.AccountingSystem.private.Plotters.BaseReporter

We are assuming there is a solid test of __bases__, we are not testing them
here and assuming they work fine.

IMPORTANT: the test MUST be pylint compliant !
"""
# pylint: disable=protected-access

import unittest
from decimal import Decimal

import mock


class StoragePlotterTestCase(unittest.TestCase):
    """StoragePlotterTestCase."""

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
        class MockStorage(object):
            # pylint: disable=missing-docstring,no-init
            definitionKeyFields = ("StorageElement", "Directory")

        moduleTested.Storage = mock.Mock(return_value=MockStorage())

        return moduleTested

    def setUp(self):
        """Setup the test case."""

        import LHCbDIRAC.AccountingSystem.private.Plotters.StoragePlotter as moduleTested

        self.moduleTested = self.mockModuleTested(moduleTested)
        self.classsTested = self.moduleTested.StoragePlotter

    def tearDown(self):
        """Tear down the test case."""

        del self.moduleTested
        del self.classsTested


# ...............................................................................


class StoragePlotterUnitTest(StoragePlotterTestCase):
    """DataStoragePlotterUnitTest.

    <constructor>
     - test_instantiate
    <class variables>
     - test_typeName
     - test_typeKeyFields
     - test_reportCatalogSpaceName
     - test_reportCatalogFilesName
     - test_reportPhysicalSpaceName
     - test_reportPhysicalFilesName
     - test_reportPFNvsLFNFileMultiplicityName
     - test_reportPFNvsLFNSizeMultiplicityName
    <methods>
     - test_reportCatalogSpace
     - test_plotCatalogSpace
     - test_reportCatalogFiles
     - test_plotCatalogFiles
     - test_reportPhysicalSpace
     - test_plotPhysicalSpace
     - test_reportPhysicalFiles
     - test_plotPhysicalFiles
    """

    # FIXME: missing test_reportPFNvsLFNFileMultiplicity
    # FIXME: missing test_plotPFNvsLFNFileMultiplicity
    # FIXME: missing test_reportPFNvsLFNSizeMultiplicity
    # FIXME: missing test_plotPFNvsLFNSizeMultiplicity
    # FIXME: missing test_multiplicityReport

    def test_instantiate(self):
        """tests that we can instantiate one object of the tested class."""
        obj = self.classsTested(None, None)
        self.assertEqual("StoragePlotter", obj.__class__.__name__)

    def test_typeName(self):
        """test the class variable "_typeName"."""
        obj = self.classsTested(None, None)
        self.assertEqual(obj._typeName, "Storage")

    def test_typeKeyFields(self):
        """test the class variable "_typeKeyFields"."""
        obj = self.classsTested(None, None)
        self.assertEqual(obj._typeKeyFields, ["StorageElement", "Directory"])

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

    def test_reportPFNvsLFNFileMultiplicityName(self):
        """test the class variable "_reportPFNvsLFNFileMultiplicityName"."""
        obj = self.classsTested(None, None)
        self.assertEqual(obj._reportPFNvsLFNFileMultiplicityName, "PFN/LFN file ratio")

    def test_reportPFNvsLFNSizeMultiplicityName(self):
        """test the class variable "_reportPFNvsLFNSizeMultiplicityName"."""
        obj = self.classsTested(None, None)
        self.assertEqual(obj._reportPFNvsLFNSizeMultiplicityName, "PFN/LFN size ratio")

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

        #     res = obj._reportCatalogSpace( { 'grouping'       : 'NextToABeer',
        #                                      'groupingFields' : [ 0, [ 'mehh' ], 'blah' ],
        #                                      'startTime'      : 'startTime',
        #                                      'endTime'        : 'endTime',
        #                                      'condDict'       : {}
        #                                     } )
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
            ("/lhcb/data", 1355616000, 86400, Decimal("4935388524246.91")),
            ("/lhcb/data", 1355702400, 86400, Decimal("4843844487074.82")),
            ("/lhcb/LHCb", 1355616000, 86400, Decimal("3935388524246.91")),
            ("/lhcb/LHCb", 1355702400, 86400, Decimal("3843844487074.82")),
        )
        mockAccountingDB.retrieveBucketedData.return_value = {"OK": True, "Value": mockedData}
        mockAccountingDB.calculateBucketLengthForTime.return_value = 86400

        res = obj._reportCatalogSpace(
            {
                "grouping": "Directory",
                "groupingFields": ("%s", ["Directory"]),
                "startTime": 1355663249.0,
                "endTime": 1355749690.0,
                "condDict": {"Directory": ["/lhcb/data", "/lhcb/LHCb"]},
            }
        )
        self.assertEqual(res["OK"], True)
        self.assertEqual(
            res["Value"],
            {
                "graphDataDict": {
                    "/lhcb/data": {1355616000: 4.9353885242469104, 1355702400: 4.8438444870748203},
                    "/lhcb/LHCb": {1355616000: 3.93538852424691, 1355702400: 3.8438444870748198},
                },
                "data": {
                    "/lhcb/data": {1355616000: 4935388.5242469106, 1355702400: 4843844.4870748203},
                    "/lhcb/LHCb": {1355616000: 3935388.5242469101, 1355702400: 3843844.4870748199},
                },
                "unit": "TB",
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

        #     res = obj._reportCatalogFiles( { 'grouping'       : 'NextToABeer',
        #                                      'groupingFields' : [ 0, [ 'mehh' ], 'blah' ],
        #                                      'startTime'      : 'startTime',
        #                                      'endTime'        : 'endTime',
        #                                      'condDict'       : {}
        #                                     } )
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
            ("/lhcb/data", 1355616000, 86400, Decimal("4935388524246.91")),
            ("/lhcb/data", 1355702400, 86400, Decimal("4843844487074.82")),
            ("/lhcb/LHCb", 1355616000, 86400, Decimal("3935388524246.91")),
            ("/lhcb/LHCb", 1355702400, 86400, Decimal("3843844487074.82")),
        )
        mockAccountingDB.retrieveBucketedData.return_value = {"OK": True, "Value": mockedData}
        mockAccountingDB.calculateBucketLengthForTime.return_value = 86400

        res = obj._reportCatalogFiles(
            {
                "grouping": "Directory",
                "groupingFields": ("%s", ["Directory"]),
                "startTime": 1355663249.0,
                "endTime": 1355749690.0,
                "condDict": {"Directory": ["/lhcb/data", "/lhcb/LHCb"]},
            }
        )
        self.assertEqual(res["OK"], True)
        self.assertEqual(
            res["Value"],
            {
                "graphDataDict": {
                    "/lhcb/data": {1355616000: 4935388.5242469106, 1355702400: 4843844.4870748203},
                    "/lhcb/LHCb": {1355616000: 3935388.5242469101, 1355702400: 3843844.4870748199},
                },
                "data": {
                    "/lhcb/data": {1355616000: 4935388524246.9102, 1355702400: 4843844487074.8203},
                    "/lhcb/LHCb": {1355616000: 3935388524246.9102, 1355702400: 3843844487074.8198},
                },
                "unit": "Mfiles",
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

        #     res = obj._reportPhysicalSpace( { 'groupingFields' : [ 0, [ 'mehh' ], 'blah' ],
        #                                       'startTime'      : 'startTime',
        #                                       'endTime'        : 'endTime',
        #                                       'condDict'       : {}
        #                                      } )
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
            ("CERN-ARCHIVE", 1355616000, 86400, Decimal("2344556767812.91")),
            ("CERN-ARCHIVE", 1355702400, 86400, Decimal("2544556767812.91")),
            ("CERN-DST", 1355616000, 86400, Decimal("344556767812.91")),
            ("CERN-DST", 1355702400, 86400, Decimal("544556767812.91")),
        )
        mockAccountingDB.retrieveBucketedData.return_value = {"OK": True, "Value": mockedData}
        mockAccountingDB.calculateBucketLengthForTime.return_value = 86400

        res = obj._reportPhysicalSpace(
            {
                "grouping": "StorageElement",
                "groupingFields": ("%s", ["StorageElement"]),
                "startTime": 1355663249.0,
                "endTime": 1355749690.0,
                "condDict": {"StorageElement": ["CERN-ARCHIVE", "CERN-DST"]},
            }
        )
        self.assertEqual(res["OK"], True)
        self.assertEqual(
            res["Value"],
            {
                "graphDataDict": {
                    "CERN-ARCHIVE": {1355616000: 2.34455676781291, 1355702400: 2.5445567678129102},
                    "CERN-DST": {1355616000: 0.34455676781290995, 1355702400: 0.54455676781290996},
                },
                "data": {
                    "CERN-ARCHIVE": {1355616000: 2344556.76781291, 1355702400: 2544556.76781291},
                    "CERN-DST": {1355616000: 344556.76781290997, 1355702400: 544556.76781291002},
                },
                "unit": "TB",
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

        #     res = obj._reportPhysicalFiles( { 'groupingFields' : [ 0, [ 'mehh' ], 'blah' ],
        #                                       'startTime'      : 'startTime',
        #                                       'endTime'        : 'endTime',
        #                                       'condDict'       : {}
        #                                      } )
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
            ("CERN-ARCHIVE", 1355616000, 86400, Decimal("412658.91")),
            ("CERN-ARCHIVE", 1355702400, 86400, Decimal("413658.91")),
            ("CERN-BUFFER", 1355616000, 86400, Decimal("250658.91")),
            ("CERN-BUFFER", 1355702400, 86400, Decimal("261658.91")),
            ("CERN-DST", 1355616000, 86400, Decimal("186658.91")),
            ("CERN-DST", 1355702400, 86400, Decimal("187658.91")),
        )
        mockAccountingDB.retrieveBucketedData.return_value = {"OK": True, "Value": mockedData}
        mockAccountingDB.calculateBucketLengthForTime.return_value = 86400

        res = obj._reportPhysicalFiles(
            {
                "grouping": "StorageElement",
                "groupingFields": ("%s", ["StorageElement"]),
                "startTime": 1355663249.0,
                "endTime": 1355749690.0,
                "condDict": {"StorageElement": ["CERN-ARCHIVE", "CERN-DST", "CERN-BUFFER"]},
            }
        )
        self.assertEqual(res["OK"], True)
        self.assertEqual(
            res["Value"],
            {
                "graphDataDict": {
                    "CERN-BUFFER": {1355616000: 250.65890999999999, 1355702400: 261.65890999999999},
                    "CERN-ARCHIVE": {1355616000: 412.65890999999999, 1355702400: 413.65890999999999},
                    "CERN-DST": {1355616000: 186.65890999999999, 1355702400: 187.65890999999999},
                },
                "data": {
                    "CERN-BUFFER": {1355616000: 250658.91, 1355702400: 261658.91},
                    "CERN-ARCHIVE": {1355616000: 412658.90999999997, 1355702400: 413658.90999999997},
                    "CERN-DST": {1355616000: 186658.91, 1355702400: 187658.91},
                },
                "unit": "kfiles",
                "granularity": 86400,
            },
        )

    def test_multiplicityReport(self):
        """test the method "_multiplicityReport"."""

        mockAccountingDB = mock.Mock()
        mockAccountingDB._getConnection.return_value = {"OK": False, "Message": "No connection"}
        mockAccountingDB.retrieveBucketedData.return_value = {"OK": True, "Value": []}
        mockAccountingDB.calculateBucketLengthForTime.return_value = "BucketLength"
        obj = self.classsTested(mockAccountingDB, None)

        #     res = obj._multiplicityReport( { 'groupingFields' : [ 0, [ 'mehh' ], 'blah' ],
        #                                      'startTime'      : 'startTime',
        #                                      'endTime'        : 'endTime',
        #                                      'condDict'       : {}
        #                                      }, '', '' )
        #     self.assertEqual( res[ 'OK' ], False )
        #     self.assertEqual( res[ 'Message' ], 'No connection' )
        #
        # We are using mock 0.7, we need this little hack
        side_values = [{"OK": False, "Message": "No connection"}, {"OK": True, "Value": []}]

        def side_effect():
            return side_values.pop()

        # Changed mocked to run over different lines of code
        #     mockAccountingDB._getConnection.side_effect = side_effect
        #     res = obj._multiplicityReport( { 'groupingFields' : [ 0, [ 'mehh' ], 'blah' ],
        #                                      'startTime'      : 'startTime',
        #                                      'endTime'        : 'endTime',
        #                                      'condDict'       : {}
        #                                     }, '', '' )
        #     self.assertEqual( res[ 'OK' ], False )
        #     self.assertEqual( res[ 'Message' ], 'No connection' )

        # Changed mocked to run over different lines of code
        mockAccountingDB._getConnection.return_value = {"OK": True, "Value": []}


# ...............................................................................


class StoragePlotterUnitTestCrashes(StoragePlotterTestCase):
    """StoragePlotterUnitTestCrashes.

    <constructor>
     - test_instantiate
    <class variables>
    <methods>
     - test_reportCatalogSpace
     - test_plotCatalogSpace
     - test_reportCatalogFiles
     - test_plotCatalogFiles
     - test_reportPhysicalSpace
     - test_plotPhysicalSpace
     - test_reportPhysicalFiles
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


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(StoragePlotterTestCase)
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(StoragePlotterUnitTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(StoragePlotterUnitTestCrashes))
    testResult = unittest.TextTestRunner(verbosity=2).run(suite)
