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
"""LHCbDIRAC.AccountingSystem.private.Plotters.PopularityPlotter.

PopularityPlotter.__bases__:
  DIRAC.AccountingSystem.private.Plotters.BaseReporter.BaseReporter
"""
from DIRAC import S_OK
from DIRAC.AccountingSystem.private.Plotters.BaseReporter import BaseReporter

from LHCbDIRAC.AccountingSystem.Client.Types.Popularity import Popularity

# FIXME: refactor _reportMethods
# FIXME: refactor _plotMethods


class PopularityPlotter(BaseReporter):
    """PopularityPlotter as extension of BaseReporter."""

    _typeName = "Popularity"
    _typeKeyFields = [dF[0] for dF in Popularity().definitionKeyFields]
    # FIXME: WTF is this ????, here includes StorageElement !!!
    _noSEtypeKeyFields = [dF[0] for dF in Popularity().definitionKeyFields]
    _noSEGrouping = (", ".join("%s" for f in _noSEtypeKeyFields), _noSEtypeKeyFields)

    # .............................................................................
    # data Usage

    _reportDataUsageName = "Data Usage"

    def _reportDataUsage(self, reportRequest):
        """Reports the data usage, from the Accounting DB.

        :param reportRequest: <dict>
          { 'groupingFields' : ( '%s', [ 'EventType' ] ),
            'startTime'      : 1355663249.0,
            'endTime'        : 1355749690.0,
            'condDict'       : { 'EventType' : '90000000' }
          }

        returns S_OK / S_ERROR
          { 'graphDataDict' : { '90000000' : { 1355616000L : 123.456789,
                                               1355702400L : 78.901234500000001 }
                                             },
            'data'          : { '90000000' : { 1355616000L : 123456.789,
                                               1355702400L : 78901.234500000006 }
                                             },
            'unit'          : 'kfiles',
            'granularity'   : 86400
          }
        """

        selectString = self._getSelectStringForGrouping(reportRequest["groupingFields"])
        selectFields = (
            selectString + ", %s, %s, SUM(%s)/SUM(%s)",
            reportRequest["groupingFields"][1] + ["startTime", "bucketLength", "Usage", "entriesInBucket"],
        )

        retVal = self._getTimedData(
            reportRequest["startTime"],
            reportRequest["endTime"],
            selectFields,
            reportRequest["condDict"],
            PopularityPlotter._noSEGrouping,
            {"convertToGranularity": "sum", "checkNone": True},
        )
        if not retVal["OK"]:
            return retVal

        dataDict, granularity = retVal["Value"]
        self.stripDataField(dataDict, 0)

        accumMaxValue = self._getAccumulationMaxValue(dataDict)
        suitableUnits = self._findSuitableUnit(dataDict, accumMaxValue, "files")

        # 3rd value, maxValue is not used
        baseDataDict, graphDataDict, __, unitName = suitableUnits

        return S_OK(
            {"data": baseDataDict, "graphDataDict": graphDataDict, "granularity": granularity, "unit": unitName}
        )

    def _plotDataUsage(self, reportRequest, plotInfo, filename):
        """Creates <filename>.png file containing information regarding the data
        usage.

        :param reportRequest: <dict>
           { 'grouping'       : 'EventType',
             'groupingFields' : ( '%s', [ 'EventType' ] ),
             'startTime'      : 1355663249.0,
             'endTime'        : 1355749690.0,
             'condDict'       : { 'StorageElement' : 'CERN' }
           }
        :param plotInfo: <dict> ( output of _reportDataUsage )
           { 'graphDataDict' : { '90000001' : { 1355616000L : 223.45678899999999,
                                                1355702400L : 148.90123449999999 },
                                 '90000000' : { 1355616000L : 123.456789,
                                                1355702400L : 78.901234500000001 }
                                },
             'data'          : { '90000001' : { 1355616000L : 223456.78899999999,
                                                1355702400L : 148901.23449999999 },
                                 '90000000' : { 1355616000L : 123456.789,
                                                1355702400L : 78901.234500000006 }
                                },
             'unit'          : 'kfiles',
             'granularity': 86400
            }
        :param filename: <str>
          '_plotDataUsage'

        returns S_OK / S_ERROR
           { 'plot': True, 'thumbnail': False }
        """

        startEpoch = reportRequest["startTime"]
        endEpoch = reportRequest["endTime"]
        granularity = plotInfo["granularity"]
        dataDict = plotInfo["graphDataDict"]

        metadata = {
            "title": "Data Usage grouped by %s" % reportRequest["grouping"],
            "starttime": startEpoch,
            "endtime": endEpoch,
            "span": granularity,
            "ylabel": plotInfo["unit"],
        }

        dataDict = self._fillWithZero(granularity, startEpoch, endEpoch, dataDict)
        return self._generateStackedLinePlot(filename, dataDict, metadata)

    # .............................................................................
    # normalized data Usage

    _reportNormalizedDataUsageName = "Normalized Data Usage"

    def _reportNormalizedDataUsage(self, reportRequest):
        """Reports the normalized data usage, from the Accounting DB.

        :param reportRequest: <dict>
          { 'groupingFields' : ( '%s', [ 'EventType' ] ),
            'startTime'      : 1355663249.0,
            'endTime'        : 1355749690.0,
            'condDict'       : { 'StorageElement' : 'CERN' }
          }

        returns S_OK / S_ERROR
          { 'graphDataDict' : { '90000001' : { 1355616000L : 223.45678899999999,
                                               1355702400L : 148.90123449999999 },
                                '90000000' : { 1355616000L : 123.456789,
                                               1355702400L : 78.901234500000001 }
                              },
            'data'          : { '90000001' : { 1355616000L : 223456.78899999999,
                                               1355702400L : 148901.23449999999 },
                                '90000000' : { 1355616000L : 123456.789,
                                               1355702400L : 78901.234500000006 }
                              },
            'unit'          : 'kfiles',
            'granularity'   : 86400
          }
        """

        selectString = self._getSelectStringForGrouping(reportRequest["groupingFields"])
        selectFields = (
            selectString + ", %s, %s, SUM(%s)/SUM(%s)",
            reportRequest["groupingFields"][1] + ["startTime", "bucketLength", "NormalizedUsage", "entriesInBucket"],
        )
        retVal = self._getTimedData(
            reportRequest["startTime"],
            reportRequest["endTime"],
            selectFields,
            reportRequest["condDict"],
            PopularityPlotter._noSEGrouping,
            {"convertToGranularity": "sum", "checkNone": True},
        )
        if not retVal["OK"]:
            return retVal

        dataDict, granularity = retVal["Value"]
        self.stripDataField(dataDict, 0)

        accumMaxValue = self._getAccumulationMaxValue(dataDict)
        suitableUnits = self._findSuitableUnit(dataDict, accumMaxValue, "files")

        # 3rd value, maxValue is not used
        baseDataDict, graphDataDict, __, unitName = suitableUnits

        return S_OK(
            {"data": baseDataDict, "graphDataDict": graphDataDict, "granularity": granularity, "unit": unitName}
        )

    def _plotNormalizedDataUsage(self, reportRequest, plotInfo, filename):
        """Creates <filename>.png file containing information regarding the
        normalized data usage.

        :param reportRequest: <dict>
           { 'grouping'       : 'EventType',
             'groupingFields' : ( '%s', [ 'EventType' ] ),
             'startTime'      : 1355663249.0,
             'endTime'        : 1355749690.0,
             'condDict'       : { 'StorageElement' : 'CERN' }
           }
        :param plotInfo: <dict> ( output of _reportNormalizedDataUsage )
           { 'graphDataDict' : { '90000001' : { 1355616000L : 223.45678899999999,
                                                1355702400L : 148.90123449999999 },
                                 '90000000' : { 1355616000L : 123.456789,
                                                1355702400L : 78.901234500000001 }
                                },
             'data'          : { '90000001' : { 1355616000L : 223456.78899999999,
                                                1355702400L : 148901.23449999999 },
                                 '90000000' : { 1355616000L : 123456.789,
                                                1355702400L : 78901.234500000006 }
                                },
             'unit'          : 'kfiles',
             'granularity': 86400
            }
        :param filename: <str>
          '_plotNormalizedDataUsage'

        returns S_OK / S_ERROR
           { 'plot': True, 'thumbnail': False }
        """

        startEpoch = reportRequest["startTime"]
        endEpoch = reportRequest["endTime"]
        dataDict = plotInfo["graphDataDict"]
        granularity = plotInfo["granularity"]

        metadata = {
            "title": "Normalized Data Usage grouped by %s" % reportRequest["grouping"],
            "starttime": startEpoch,
            "endtime": endEpoch,
            "span": granularity,
            "ylabel": plotInfo["unit"],
        }

        dataDict = self._fillWithZero(granularity, startEpoch, endEpoch, dataDict)
        return self._generateStackedLinePlot(filename, dataDict, metadata)
