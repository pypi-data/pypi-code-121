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
"""LHCbDIRAC.AccountingSystem.private.Plotters.StoragePlotter.

StoragePlotter.__bases__:
  DIRAC.AccountingSystem.private.Plotters.BaseReporter.BaseReporter
"""
from DIRAC import S_OK, S_ERROR
from DIRAC.AccountingSystem.private.Plotters.BaseReporter import BaseReporter

from LHCbDIRAC.AccountingSystem.Client.Types.Storage import Storage

# FIXME: refactor _reportMethods
# FIXME: refactor _plotMethods


class StoragePlotter(BaseReporter):
    """StoragePlotter as extension of BaseReporter."""

    _typeName = "Storage"
    _typeKeyFields = [dF[0] for dF in Storage().definitionKeyFields]

    # .............................................................................
    # catalog Space

    _reportCatalogSpaceName = "LFN size"

    def _reportCatalogSpace(self, reportRequest):
        """Reports about LFN size and catalog space from the accounting.

        :param reportRequest: <dict>
          { 'grouping'       : 'Directory',
            'groupingFields' : ( '%s', [ 'Directory' ] ),
            'startTime'      : 1355663249.0,
            'endTime'        : 1355749690.0,
            'condDict'       : { 'Directory' : [ '/lhcb/data', '/lhcb/LHCb' ] }
          }

        returns S_OK / S_ERROR
          { 'graphDataDict' : { '/lhcb/data' : { 1355616000L : 4.9353885242469104,
                                                 1355702400L : 4.8438444870748203 },
                                '/lhcb/LHCb' : { 1355616000L : 3.93538852424691,
                                                 1355702400L : 3.8438444870748198 }
                               },
            'data'          : { '/lhcb/data' : { 1355616000L : 4935388.5242469106,
                                                 1355702400L : 4843844.4870748203 },
                                '/lhcb/LHCb' : { 1355616000L : 3935388.5242469101,
                                                 1355702400L : 3843844.4870748199 }
                               },
            'unit'          : 'TB',
            'granularity'   : 86400
           }
        """

        if reportRequest["grouping"] == "StorageElement":
            return S_ERROR("Grouping by storage element when requesting lfn info makes no sense")

        selectField = self._getSelectStringForGrouping(reportRequest["groupingFields"])
        selectFields = (
            selectField + ", %s, %s, SUM(%s)/SUM(%s)",
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

        accumMaxVal = self._getAccumulationMaxValue(dataDict)
        suitableUnits = self._findSuitableUnit(dataDict, accumMaxVal, "bytes")

        # 3rd value, maxValue is not used
        baseDataDict, graphDataDict, __, unitName = suitableUnits

        return S_OK(
            {"data": baseDataDict, "graphDataDict": graphDataDict, "granularity": granularity, "unit": unitName}
        )

    def _plotCatalogSpace(self, reportRequest, plotInfo, filename):
        """Creates <filename>.png file containing information regarding the LFN
        size and the catalog space.

        :param reportRequest: <dict>
           { 'grouping'       : 'Directory',
             'groupingFields' : ( '%s', [ 'Directory' ] ),
             'startTime'      : 1355663249.0,
             'endTime'        : 1355749690.0,
             'condDict'       : { 'Directory' : [ '/lhcb/data', '/lhcb/LHCb' ] }
           }
        :param plotInfo: <dict> ( output of _reportCatalogSpace )
           { 'graphDataDict' : { '/lhcb/data' : { 1355616000L : 4.9353885242469104,
                                                  1355702400L : 4.8438444870748203 },
                                 '/lhcb/LHCb' : { 1355616000L : 3.93538852424691,
                                                  1355702400L : 3.8438444870748198 }
                                },
             'data'          : { '/lhcb/data' : { 1355616000L : 4935388.5242469106,
                                                  1355702400L : 4843844.4870748203 },
                                 '/lhcb/LHCb' : { 1355616000L : 3935388.5242469101,
                                                  1355702400L : 3843844.4870748199 }
                                },
             'unit'          : 'TB',
             'granularity'   : 86400
            }
        :param filename: <str>
          '_plotCatalogSpace'

        returns S_OK / S_ERROR
           { 'plot': True, 'thumbnail': False }
        """

        startEpoch = reportRequest["startTime"]
        endEpoch = reportRequest["endTime"]
        granularity = plotInfo["granularity"]
        dataDict = plotInfo["graphDataDict"]

        metadata = {
            "title": "LFN space usage by %s" % reportRequest["grouping"],
            "starttime": startEpoch,
            "endtime": endEpoch,
            "span": granularity,
            "ylabel": plotInfo["unit"],
        }

        dataDict = self._fillWithZero(granularity, startEpoch, endEpoch, dataDict)
        return self._generateStackedLinePlot(filename, dataDict, metadata)

    # .............................................................................
    # catalog Files

    _reportCatalogFilesName = "LFN files"

    def _reportCatalogFiles(self, reportRequest):
        """Reports about the LFN files and the catalog files from the accounting.

        :param reportRequest: <dict>
          { 'grouping'       : 'Directory',
            'groupingFields' : ( '%s', [ 'Directory' ] ),
            'startTime'      : 1355663249.0,
            'endTime'        : 1355749690.0,
            'condDict'       : { 'Directory' : [ '/lhcb/data', '/lhcb/LHCb' ] }
           }

        returns S_OK / S_ERROR
          { 'graphDataDict' : { '/lhcb/data' : { 1355616000L : 4935388.5242469106,
                                                 1355702400L : 4843844.4870748203 },
                                '/lhcb/LHCb' : { 1355616000L : 3935388.5242469101,
                                                 1355702400L : 3843844.4870748199 }
                               },
            'data'          : { '/lhcb/data' : { 1355616000L : 4935388524246.9102,
                                                 1355702400L : 4843844487074.8203 },
                                '/lhcb/LHCb' : { 1355616000L : 3935388524246.9102,
                                                 1355702400L : 3843844487074.8198 }
                               },
            'unit'          : 'Mfiles',
            'granularity'   : 86400
           }
        """

        if reportRequest["grouping"] == "StorageElement":
            return S_ERROR("Grouping by storage element when requesting lfn info makes no sense")

        selectField = self._getSelectStringForGrouping(reportRequest["groupingFields"])
        selectFields = (
            selectField + ", %s, %s, SUM(%s)/SUM(%s)",
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

        accumMaxVal = self._getAccumulationMaxValue(dataDict)
        suitableUnits = self._findSuitableUnit(dataDict, accumMaxVal, "files")

        # 3rd value, maxValue is not used
        baseDataDict, graphDataDict, __, unitName = suitableUnits

        return S_OK(
            {"data": baseDataDict, "graphDataDict": graphDataDict, "granularity": granularity, "unit": unitName}
        )

    def _plotCatalogFiles(self, reportRequest, plotInfo, filename):
        """Creates <filename>.png file containing information regarding the LFN
        files and the catalog files.

        :param reportRequest: <dict>
          { 'grouping'       : 'Directory',
            'groupingFields' : ( '%s', [ 'Directory' ] ),
            'startTime'      : 1355663249.0,
            'endTime'        : 1355749690.0,
            'condDict'       : { 'Directory' : [ '/lhcb/data', '/lhcb/LHCb' ] }
           }
        :param plotInfo: <dict> ( output of _reportCatalogFiles )
          { 'graphDataDict' : { '/lhcb/data' : { 1355616000L : 4935388.5242469106,
                                                 1355702400L : 4843844.4870748203 },
                                '/lhcb/LHCb' : { 1355616000L : 3935388.5242469101,
                                                 1355702400L : 3843844.4870748199 }
                              },
            'data'          : { '/lhcb/data' : { 1355616000L : 4935388524246.9102,
                                                 1355702400L : 4843844487074.8203 },
                                '/lhcb/LHCb' : { 1355616000L : 3935388524246.9102,
                                                1355702400L : 3843844487074.8198 }
                                        },
            'unit'          : 'Mfiles',
            'granularity'   : 86400
           }
        :param filename: <str>
          '_plotCatalogFiles'

        returns S_OK / S_ERROR
           { 'plot': True, 'thumbnail': False }
        """
        startEpoch = reportRequest["startTime"]
        endEpoch = reportRequest["endTime"]
        granularity = plotInfo["granularity"]
        dataDict = plotInfo["graphDataDict"]

        metadata = {
            "title": "Number of LFNs by %s" % reportRequest["grouping"],
            "starttime": startEpoch,
            "endtime": endEpoch,
            "span": granularity,
            "ylabel": plotInfo["unit"],
        }

        dataDict = self._fillWithZero(granularity, startEpoch, endEpoch, dataDict)
        return self._generateStackedLinePlot(filename, dataDict, metadata)

    # .............................................................................
    # Physical Space

    _reportPhysicalSpaceName = "PFN size"

    def _reportPhysicalSpace(self, reportRequest):
        """Reports about the PFN size and the physical space from the accounting.

        :param reportRequest: <dict>
          { 'grouping'       : 'StorageElement',
            'groupingFields' : ( '%s', [ 'StorageElement' ] ),
            'startTime'      : 1355663249.0,
            'endTime'        : 1355749690.0,
            'condDict'       : { 'StorageElement' : [ 'CERN-ARCHIVE', 'CERN-DST' ] }
           }

        returns S_OK / S_ERROR
          { 'graphDataDict' : { 'CERN-ARCHIVE' : { 1355616000L : 2.34455676781291,
                                                   1355702400L : 2.5445567678129102 },
                                'CERN-DST'     : { 1355616000L : 0.34455676781290995,
                                                   1355702400L : 0.54455676781290996 }
                               },
            'data'          : { 'CERN-ARCHIVE' : { 1355616000L : 2344556.76781291,
                                                   1355702400L : 2544556.76781291 },
                                'CERN-DST'     : { 1355616000L : 344556.76781290997,
                                                   1355702400L : 544556.76781291002 }
                               },
            'unit'          : 'TB',
            'granularity'   : 86400
           }
        """

        selectField = self._getSelectStringForGrouping(reportRequest["groupingFields"])
        selectFields = (
            selectField + ", %s, %s, SUM(%s/%s)",
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

        accumMaxVal = self._getAccumulationMaxValue(dataDict)
        suitableUnits = self._findSuitableUnit(dataDict, accumMaxVal, "bytes")

        # 3rd value, maxValue is not used
        baseDataDict, graphDataDict, __, unitName = suitableUnits

        return S_OK(
            {"data": baseDataDict, "graphDataDict": graphDataDict, "granularity": granularity, "unit": unitName}
        )

    def _plotPhysicalSpace(self, reportRequest, plotInfo, filename):
        """Creates <filename>.png file containing information regarding the PFN
        size and the physical space.

        :param reportRequest: <dict>
          { 'grouping'       : 'StorageElement',
            'groupingFields' : ( '%s', [ 'StorageElement' ] ),
            'startTime'      : 1355663249.0,
            'endTime'        : 1355749690.0,
            'condDict'       : { 'StorageElement' : [ 'CERN-ARCHIVE', 'CERN-DST' ] }
          }
        :param plotInfo: <dict> ( output of _reportPhysicalSpace )
          { 'graphDataDict' : { 'CERN-ARCHIVE' : { 1355616000L : 2.34455676781291,
                                                   1355702400L : 2.5445567678129102 },
                                'CERN-DST'     : { 1355616000L : 0.34455676781290995,
                                                   1355702400L : 0.54455676781290996 }
                              },
            'data'          : { 'CERN-ARCHIVE' : { 1355616000L : 2344556.76781291,
                                                   1355702400L : 2544556.76781291 },
                                'CERN-DST'     : { 1355616000L : 344556.76781290997,
                                                   1355702400L : 544556.76781291002 }
                              },
            'unit'          : 'TB',
            'granularity'   : 86400
           }
        :param filename: <str>
          '_plotPhysicalSpace'

        returns S_OK / S_ERROR
           { 'plot': True, 'thumbnail': False }
        """

        startEpoch = reportRequest["startTime"]
        endEpoch = reportRequest["endTime"]
        granularity = plotInfo["granularity"]
        dataDict = plotInfo["graphDataDict"]

        metadata = {
            "title": "PFN space usage by %s" % reportRequest["grouping"],
            "starttime": startEpoch,
            "endtime": endEpoch,
            "span": granularity,
            "ylabel": plotInfo["unit"],
        }
        dataDict = self._fillWithZero(granularity, startEpoch, endEpoch, dataDict)
        return self._generateStackedLinePlot(filename, dataDict, metadata)

    # .............................................................................
    # physical Files

    _reportPhysicalFilesName = "PFN files"

    def _reportPhysicalFiles(self, reportRequest):
        """Reports about the PFN files and the physical files from the accounting.

        :param reportRequest: <dict>
           { 'grouping'       : 'StorageElement',
             'groupingFields' : ( '%s', [ 'StorageElement' ] ),
             'startTime'      : 1355663249.0,
             'endTime'        : 1355749690.0,
             'condDict'       : { 'StorageElement' : [ 'CERN-ARCHIVE', 'CERN-DST', 'CERN-BUFFER' ] }
            }

        returns S_OK / S_ERROR
          { 'graphDataDict' : { 'CERN-BUFFER'  : { 1355616000L : 250.65890999999999,
                                                   1355702400L : 261.65890999999999 },
                                'CERN-ARCHIVE' : { 1355616000L : 412.65890999999999,
                                                   1355702400L : 413.65890999999999 },
                                'CERN-DST'     : { 1355616000L : 186.65890999999999,
                                                   1355702400L : 187.65890999999999 }
                               },
            'data'          : { 'CERN-BUFFER'  : { 1355616000L : 250658.91,
                                                   1355702400L : 261658.91 },
                                'CERN-ARCHIVE' : { 1355616000L : 412658.90999999997,
                                                   1355702400L : 413658.90999999997 },
                                'CERN-DST'     : { 1355616000L : 186658.91,
                                                   1355702400L : 187658.91 }
                               },
            'unit'          : 'kfiles',
            'granularity'   : 86400
           }
        """

        selectField = self._getSelectStringForGrouping(reportRequest["groupingFields"])
        selectFields = (
            selectField + ", %s, %s, SUM(%s/%s)",
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

        accumMaxVal = self._getAccumulationMaxValue(dataDict)
        suitableUnits = self._findSuitableUnit(dataDict, accumMaxVal, "files")

        # 3rd value, maxValue is not used
        baseDataDict, graphDataDict, __, unitName = suitableUnits

        return S_OK(
            {"data": baseDataDict, "graphDataDict": graphDataDict, "granularity": granularity, "unit": unitName}
        )

    def _plotPhysicalFiles(self, reportRequest, plotInfo, filename):
        """Creates <filename>.png file containing information regarding the PFN
        files and the physical files.

        :param reportRequest: <dict>
           { 'grouping'       : 'StorageElement',
             'groupingFields' : ( '%s', [ 'StorageElement' ] ),
             'startTime'      : 1355663249.0,
             'endTime'        : 1355749690.0,
             'condDict'       : { 'StorageElement' : [ 'CERN-ARCHIVE', 'CERN-DST', 'CERN-BUFFER' ] }
            }
        :param plotInfo: <dict> ( output of _reportPhysicalFiles )
          { 'graphDataDict' : { 'CERN-BUFFER'  : { 1355616000L : 250.65890999999999,
                                                   1355702400L : 261.65890999999999 },
                                'CERN-ARCHIVE' : { 1355616000L : 412.65890999999999,
                                                   1355702400L : 413.65890999999999 },
                                'CERN-DST'     : { 1355616000L : 186.65890999999999,
                                                   1355702400L : 187.65890999999999 }
                              },
            'data'          : { 'CERN-BUFFER'  : { 1355616000L : 250658.91,
                                                   1355702400L : 261658.91 },
                                'CERN-ARCHIVE' : { 1355616000L : 412658.90999999997,
                                                   1355702400L : 413658.90999999997 },
                                'CERN-DST'     : { 1355616000L : 186658.91,
                                                   1355702400L : 187658.91 }
                              },
            'unit'          : 'kfiles',
            'granularity'   : 86400
           }
        :param filename: <str>
          '_plotPhysicalFiles'

        return S_OK / S_ERROR
           { 'plot': True, 'thumbnail': False }
        """

        startEpoch = reportRequest["startTime"]
        endEpoch = reportRequest["endTime"]
        granularity = plotInfo["granularity"]
        dataDict = plotInfo["graphDataDict"]

        metadata = {
            "title": "Number of PFNs by %s" % reportRequest["grouping"],
            "starttime": startEpoch,
            "endtime": endEpoch,
            "span": granularity,
            "ylabel": plotInfo["unit"],
        }

        dataDict = self._fillWithZero(granularity, startEpoch, endEpoch, dataDict)
        return self._generateStackedLinePlot(filename, dataDict, metadata)

    # .............................................................................
    # PFN vs LFN File Multiplicity

    _reportPFNvsLFNFileMultiplicityName = "PFN/LFN file ratio"

    def _reportPFNvsLFNFileMultiplicity(self, reportRequest):

        logicalField = "LogicalFiles"
        physicalField = "PhysicalFiles"

        return self._multiplicityReport(reportRequest, logicalField, physicalField)

    def _plotPFNvsLFNFileMultiplicity(self, reportRequest, plotInfo, filename):

        startEpoch = reportRequest["startTime"]
        endEpoch = reportRequest["endTime"]
        granularity = plotInfo["granularity"]
        dataDict = plotInfo["graphDataDict"]

        metadata = {
            "title": "Ratio of PFN/LFN files by %s" % reportRequest["grouping"],
            "starttime": startEpoch,
            "endtime": endEpoch,
            "span": granularity,
            "ylabel": plotInfo["unit"],
        }

        dataDict = self._fillWithZero(granularity, startEpoch, endEpoch, dataDict)
        return self._generateStackedLinePlot(filename, dataDict, metadata)

    # .............................................................................
    # PFN vs LFN Size Multiplicity

    _reportPFNvsLFNSizeMultiplicityName = "PFN/LFN size ratio"

    def _reportPFNvsLFNSizeMultiplicity(self, reportRequest):

        logicalField = "LogicalSize"
        physicalField = "PhysicalSize"

        return self._multiplicityReport(reportRequest, logicalField, physicalField)

    def _plotPFNvsLFNSizeMultiplicity(self, reportRequest, plotInfo, filename):

        startEpoch = reportRequest["startTime"]
        endEpoch = reportRequest["endTime"]
        granularity = plotInfo["granularity"]
        dataDict = plotInfo["graphDataDict"]

        metadata = {
            "title": "Ratio of PFN/LFN space used by %s" % reportRequest["grouping"],
            "starttime": startEpoch,
            "endtime": endEpoch,
            "span": granularity,
            "ylabel": plotInfo["unit"],
        }

        dataDict = self._fillWithZero(granularity, startEpoch, endEpoch, dataDict)
        return self._generateStackedLinePlot(filename, dataDict, metadata)

    # .............................................................................
    # helper methods

    def _multiplicityReport(self, reportRequest, logicalField, physicalField):

        # Step 1 get the total LFNs for each bucket
        selectFields = (
            "%s, %s, %s, SUM(%s)/SUM(%s)",
            ["Directory", "startTime", "bucketLength", logicalField, "entriesInBucket"],
        )
        retVal = self._getTimedData(
            reportRequest["startTime"],
            reportRequest["endTime"],
            selectFields,
            reportRequest["condDict"],
            ("%s", ["Directory"]),
            {"convertToGranularity": "average", "checkNone": True},
        )
        if not retVal["OK"]:
            return retVal

        # 2nd element ( granularity ) is unused
        dataDict, __ = retVal["Value"]
        self.stripDataField(dataDict, 0)
        bucketTotals = self._getBucketTotals(dataDict)

        # Step 2 get the total PFNs
        _selectField = self._getSelectStringForGrouping(reportRequest["groupingFields"])
        selectFields = (
            _selectField + ", %s, %s, SUM(%s/%s)",
            reportRequest["groupingFields"][1] + ["startTime", "bucketLength", physicalField, "entriesInBucket"],
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

        # Step 3 divide the PFNs by the total amount of LFNs
        finalData = {}

        # FIXME: TO BE replaced by a faster implementation ( see below )
        for k in dataDict:
            for bt in dataDict[k]:
                if bt in bucketTotals:
                    if k not in finalData:
                        finalData[k] = {}
                    finalData[k][bt] = dataDict[k][bt] / bucketTotals[bt]

        #    for key, bucketTotal in dataDict.items():
        #      for bt in bucketTotal.values():
        #        if bt in bucketTotals:
        #          if key not in finalData:
        #            finalData[ key ] = {}
        #          finalData[ key ][ bt ] = bucketTotal[ bt ] / bucketTotals[ bt ]

        return S_OK({"data": finalData, "graphDataDict": finalData, "granularity": granularity, "unit": "PFN / LFN"})
