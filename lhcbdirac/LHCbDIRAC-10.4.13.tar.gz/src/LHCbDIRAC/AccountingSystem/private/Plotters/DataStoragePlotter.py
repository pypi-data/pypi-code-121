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
"""LHCbDIRAC.AccountingSystem.private.Plotters.DataStoragePlotter.

DataStoragePlotter.__bases__:
  DIRAC.AccountingSystem.private.Plotters.BaseReporter.BaseReporter
"""
from DIRAC import S_OK, S_ERROR
from DIRAC.AccountingSystem.private.Plotters.BaseReporter import BaseReporter

from LHCbDIRAC.AccountingSystem.Client.Types.DataStorage import DataStorage

# FIXME: refactor _reportMethods
# FIXME: refactor _plotMethods


class DataStoragePlotter(BaseReporter):
    """DataStoragePlotter as extension of BaseReporter."""

    _typeName = "DataStorage"
    _typeKeyFields = [dF[0] for dF in DataStorage().definitionKeyFields]

    # Catalog Space

    _reportCatalogSpaceName = "LFN size"

    def _reportCatalogSpace(self, reportRequest):
        """Reports about the LFN size and the catalog space from the accounting.

        :param reportRequest: <dict>
          { 'grouping'       : 'EventType',
            'groupingFields' : ( '%s', [ 'EventType' ] ),
            'startTime'      : 1355663249.0,
            'endTime'        : 1355749690.0,
            'condDict'       : { 'EventType' : 'Full stream' }
          }

        returns S_OK / S_ERROR
          { 'graphDataDict': { 'Full stream': { 1355616000L: 935.38852424691629,
                                                1355702400L: 843.84448707482204 }
                             },
            'data'         : { 'Full stream': { 1355616000L: 935388.52424691629,
                                                1355702400L: 843844.48707482207 }
                             },
            'unit'         : 'GB',
            'granularity'  : 86400
          }
        """

        if reportRequest["grouping"] == "StorageElement":
            return S_ERROR("Grouping by storage element when requesting lfn info makes no sense")

        selectString = self._getSelectStringForGrouping(reportRequest["groupingFields"])

        selectFields = (
            selectString + ", %s, %s, SUM(%s/%s)",
            reportRequest["groupingFields"][1] + ["startTime", "bucketLength", "LogicalSize", "entriesInBucket"],
        )

        retVal = self._getTimedData(
            reportRequest["startTime"],
            reportRequest["endTime"],
            selectFields,
            reportRequest["condDict"],
            reportRequest["groupingFields"],
            {"convertToGranularity": "average", "checkNone": True},
        )
        if not retVal["OK"]:
            return retVal

        dataDict, granularity = retVal["Value"]
        self.stripDataField(dataDict, 0)

        accumMaxValue = self._getAccumulationMaxValue(dataDict)
        suitableUnits = self._findSuitableUnit(dataDict, accumMaxValue, "bytes")

        # 3rd variable unused ( maxValue )
        baseDataDict, graphDataDict, __, unitName = suitableUnits

        return S_OK(
            {"data": baseDataDict, "graphDataDict": graphDataDict, "granularity": granularity, "unit": unitName}
        )

    def _plotCatalogSpace(self, reportRequest, plotInfo, filename):
        """Creates <filename>.png file containing information regarding the LFN
        size and the catalog space.

        :param reportRequest: <dict>
           { 'grouping'       : 'EventType',
             'groupingFields' : ( '%s', [ 'EventType' ] ),
             'startTime'      : 1355663249.0,
             'endTime'        : 1355749690.0,
             'condDict'       : { 'EventType' : 'Full stream' }
           }
        :param plotInfo: <dict> ( output of _reportCatalogSpace )
           { 'graphDataDict' : { 'Full stream' : { 1355616000L: 4.9003546130956819,
                                                   1355702400L: 4.9050379437065059 }
                               },
             'data'          : { 'Full stream' : { 1355616000L: 4900354613.0956821,
                                                   1355702400L: 4905037943.7065058 }
                               },
             'unit'          : 'PB',
             'granularity'   : 86400
            }
        :param filename: <str>
          '_plotCatalogSpace'

        returns S_OK / S_ERROR
           { 'plot': True, 'thumbnail': False }
        """

        startTime = reportRequest["startTime"]
        endTime = reportRequest["endTime"]
        span = plotInfo["granularity"]
        dataDict = plotInfo["graphDataDict"]

        metadata = {
            "title": "LFN space usage grouped by %s" % reportRequest["grouping"],
            "starttime": startTime,
            "endtime": endTime,
            "span": span,
            "ylabel": plotInfo["unit"],
        }

        dataDict = self._fillWithZero(span, startTime, endTime, dataDict)
        return self._generateStackedLinePlot(filename, dataDict, metadata)

    # .............................................................................
    # Catalog Files

    _reportCatalogFilesName = "LFN files"

    def _reportCatalogFiles(self, reportRequest):
        """Reports about the LFN files and the catalog files from the accounting.

        :param reportRequest: <dict>
          { 'grouping'       : 'EventType',
            'groupingFields' : ( '%s', [ 'EventType' ] ),
            'startTime'      : 1355663249.0,
            'endTime'        : 1355749690.0,
            'condDict'       : { 'EventType' : 'Full stream' }
          }

        returns S_OK / S_ERROR
          { 'graphDataDict' : { 'Full stream' : { 1355616000L : 420.47885754501203,
                                                  1355702400L : 380.35170637810842 }
                                                },
            'data'          : { 'Full stream' : { 1355616000L : 420.47885754501203,
                                                  1355702400L : 380.35170637810842 }
                                                },
            'unit'          : 'files',
            'granularity'   : 86400
          }
        """

        if reportRequest["grouping"] == "StorageElement":
            return S_ERROR("Grouping by storage element when requesting lfn info makes no sense")

        selectString = self._getSelectStringForGrouping(reportRequest["groupingFields"])
        selectFields = (
            selectString + ", %s, %s, SUM(%s/%s)",
            reportRequest["groupingFields"][1] + ["startTime", "bucketLength", "LogicalFiles", "entriesInBucket"],
        )
        retVal = self._getTimedData(
            reportRequest["startTime"],
            reportRequest["endTime"],
            selectFields,
            reportRequest["condDict"],
            reportRequest["groupingFields"],
            {"convertToGranularity": "average", "checkNone": True},
        )
        if not retVal["OK"]:
            return retVal

        dataDict, granularity = retVal["Value"]
        self.stripDataField(dataDict, 0)

        accumMaxValue = self._getAccumulationMaxValue(dataDict)
        suitableUnits = self._findSuitableUnit(dataDict, accumMaxValue, "files")

        # 3rd variable unused ( maxValue )
        baseDataDict, graphDataDict, __, unitName = suitableUnits

        return S_OK(
            {"data": baseDataDict, "graphDataDict": graphDataDict, "granularity": granularity, "unit": unitName}
        )

    def _plotCatalogFiles(self, reportRequest, plotInfo, filename):
        """Creates <filename>.png file containing information regarding the LFN
        files and the catalog files.

        :param reportRequest: <dict>
          { 'grouping'       : 'EventType',
            'groupingFields' : ( '%s', [ 'EventType' ] ),
            'startTime'      : 1355663249.0,
            'endTime'        : 1355749690.0,
            'condDict'       : { 'EventType' : 'Full stream' }
          }
        :param plotInfo: <dict> ( output of _reportCatalogFiles )
          { 'graphDataDict' : { 'Full stream' : { 1355616000L : 420.47885754501203,
                                                  1355702400L : 380.35170637810842 }
                              },
            'data'          : { 'Full stream' : { 1355616000L : 420.47885754501203,
                                                  1355702400L : 380.35170637810842 }
                              },
            'unit'          : 'files',
            'granularity'   : 86400
          }
        :param filename: <str>
          '_plotCatalogFiles'

        returns S_OK / S_ERROR
           { 'plot': True, 'thumbnail': False }
        """

        startTime = reportRequest["startTime"]
        endTime = reportRequest["endTime"]
        span = plotInfo["granularity"]
        dataDict = plotInfo["graphDataDict"]

        metadata = {
            "title": "Number of LFNs by %s" % reportRequest["grouping"],
            "starttime": startTime,
            "endtime": endTime,
            "span": span,
            "ylabel": plotInfo["unit"],
        }

        dataDict = self._fillWithZero(span, startTime, endTime, dataDict)
        return self._generateStackedLinePlot(filename, dataDict, metadata)

    # .............................................................................
    # Physical Space

    _reportPhysicalSpaceName = "PFN size"

    def _reportPhysicalSpace(self, reportRequest):
        """Reports about the PFN size and the physical space from the accounting.

        :param reportRequest: <dict>
          { 'grouping'       : 'EventType',
            'groupingFields' : ( '%s', [ 'EventType' ] ),
            'startTime'      : 1355663249.0,
            'endTime'        : 1355749690.0,
            'condDict'       : { 'EventType' : 'Full stream' }
          }

        returns S_OK / S_ERROR
          { 'graphDataDict' : { 'Full stream' : { 1355616000L : 14.754501202,
                                                  1355702400L : 15.237810842 }
                              },
            'data'          : { 'Full stream' : { 1355616000L : 14.754501202,
                                                  1355702400L : 15.237810842 }
                              },
            'unit'          : 'MB',
            'granularity'   : 86400
          }
        """

        selectString = self._getSelectStringForGrouping(reportRequest["groupingFields"])
        selectFields = (
            selectString + ", %s, %s, SUM(%s/%s)",
            reportRequest["groupingFields"][1] + ["startTime", "bucketLength", "PhysicalSize", "entriesInBucket"],
        )
        retVal = self._getTimedData(
            reportRequest["startTime"],
            reportRequest["endTime"],
            selectFields,
            reportRequest["condDict"],
            reportRequest["groupingFields"],
            {"convertToGranularity": "average", "checkNone": True},
        )
        if not retVal["OK"]:
            return retVal

        dataDict, granularity = retVal["Value"]
        self.stripDataField(dataDict, 0)

        accumMaxValue = self._getAccumulationMaxValue(dataDict)
        suitableUnits = self._findSuitableUnit(dataDict, accumMaxValue, "bytes")

        # 3rd variable unused ( maxValue )
        baseDataDict, graphDataDict, __, unitName = suitableUnits

        return S_OK(
            {"data": baseDataDict, "graphDataDict": graphDataDict, "granularity": granularity, "unit": unitName}
        )

    def _plotPhysicalSpace(self, reportRequest, plotInfo, filename):
        """Creates <filename>.png file containing information regarding the PFN
        size and the physical space.

        :param reportRequest: <dict>
          { 'grouping'       : 'EventType',
            'groupingFields' : ( '%s', [ 'EventType' ] ),
            'startTime'      : 1355663249.0,
            'endTime'        : 1355749690.0,
            'condDict'       : { 'EventType' : 'Full stream' }
          }
        :param plotInfo: <dict> ( output of _reportPhysicalSpace )
          { 'graphDataDict' : { 'Full stream' : { 1355616000L : 14.754501202,
                                                  1355702400L : 15.237810842 }
                              },
            'data'          : { 'Full stream' : { 1355616000L : 14.754501202,
                                                  1355702400L : 15.237810842 }
                              },
            'unit'          : 'MB',
            'granularity'   : 86400
          }
        :param filename: <str>
          '_plotPhysicalSpace'

        returns S_OK / S_ERROR
           { 'plot': True, 'thumbnail': False }
        """

        startTime = reportRequest["startTime"]
        endTime = reportRequest["endTime"]
        span = plotInfo["granularity"]
        dataDict = plotInfo["graphDataDict"]

        metadata = {
            "title": "PFN space usage by %s" % reportRequest["grouping"],
            "starttime": startTime,
            "endtime": endTime,
            "span": span,
            "ylabel": plotInfo["unit"],
        }

        dataDict = self._fillWithZero(span, startTime, endTime, dataDict)
        return self._generateStackedLinePlot(filename, dataDict, metadata)

    # .............................................................................
    # Physical Files

    _reportPhysicalFilesName = "PFN files"

    def _reportPhysicalFiles(self, reportRequest):
        """Reports about the PFN files and the physical files from the accounting.

        :param reportRequest: <dict>
           { 'grouping'       : 'EventType',
             'groupingFields' : ( '%s', [ 'EventType' ] ),
             'startTime'      : 1355663249.0,
             'endTime'        : 1355749690.0,
             'condDict'       : { 'EventType' : 'Full stream' }
           }

        returns S_OK / S_ERROR
          { 'graphDataDict' : { 'Full stream' : { 1355616000L : 42.47885754501203,
                                                  1355702400L : 38.35170637810842 }
                              },
            'data'          : { 'Full stream' : { 1355616000L : 42.47885754501203,
                                                  1355702400L : 38.35170637810842 }
                              },
            'unit'          : 'files',
            'granularity'   : 86400
          }
        """

        selectString = self._getSelectStringForGrouping(reportRequest["groupingFields"])
        selectFields = (
            selectString + ", %s, %s, SUM(%s/%s)",
            reportRequest["groupingFields"][1] + ["startTime", "bucketLength", "PhysicalFiles", "entriesInBucket"],
        )
        retVal = self._getTimedData(
            reportRequest["startTime"],
            reportRequest["endTime"],
            selectFields,
            reportRequest["condDict"],
            reportRequest["groupingFields"],
            {"convertToGranularity": "average", "checkNone": True},
        )
        if not retVal["OK"]:
            return retVal
        dataDict, granularity = retVal["Value"]
        self.stripDataField(dataDict, 0)

        accumMaxValue = self._getAccumulationMaxValue(dataDict)
        suitableUnits = self._findSuitableUnit(dataDict, accumMaxValue, "files")

        # 3rd variable unused ( maxValue )
        baseDataDict, graphDataDict, __, unitName = suitableUnits

        return S_OK(
            {"data": baseDataDict, "graphDataDict": graphDataDict, "granularity": granularity, "unit": unitName}
        )

    def _plotPhysicalFiles(self, reportRequest, plotInfo, filename):
        """Creates <filename>.png file containing information regarding the PFN
        files and the physical files.

        :param reportRequest: <dict>
           { 'grouping'       : 'EventType',
             'groupingFields' : ( '%s', [ 'EventType' ] ),
             'startTime'      : 1355663249.0,
             'endTime'        : 1355749690.0,
             'condDict'       : { 'EventType' : 'Full stream' }
           }
        :param plotInfo: <dict> ( output of _reportPhysicalFiles )
          { 'graphDataDict' : { 'Full stream' : { 1355616000L: 4.9003546130956819,
                                                  1355702400L: 4.9050379437065059 }
                              },
            'data'          : { 'Full stream' : { 1355616000L: 4900354613.0956821,
                                                  1355702400L: 4905037943.7065058 }
                              },
            'unit'          : 'PB',
            'granularity'   : 86400
          }
        :param filename: <str>
          '_plotPhysicalFiles'

        return S_OK / S_ERROR
           { 'plot': True, 'thumbnail': False }
        """

        startTime = reportRequest["startTime"]
        endTime = reportRequest["endTime"]
        span = plotInfo["granularity"]
        dataDict = plotInfo["graphDataDict"]

        metadata = {
            "title": "Number of PFNs by %s" % reportRequest["grouping"],
            "starttime": startTime,
            "endtime": endTime,
            "span": span,
            "ylabel": plotInfo["unit"],
        }

        dataDict = self._fillWithZero(span, startTime, endTime, dataDict)
        return self._generateStackedLinePlot(filename, dataDict, metadata)
