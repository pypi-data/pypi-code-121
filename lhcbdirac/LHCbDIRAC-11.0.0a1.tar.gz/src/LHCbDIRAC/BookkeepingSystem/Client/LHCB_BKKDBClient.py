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
"""LHCb Bookkeeping database client."""
from LHCbDIRAC.BookkeepingSystem.Client.BaseESClient import BaseESClient
from LHCbDIRAC.BookkeepingSystem.Client.LHCbBookkeepingManager import LHCbBookkeepingManager


class LHCB_BKKDBClient(BaseESClient):
    """Client which used to browse the Entities."""

    #############################################################################

    def __init__(self, url=None, web=False, welcome=True):
        """Initialize the basic class."""
        BaseESClient.__init__(self, LHCbBookkeepingManager(url=url, web=web, welcome=welcome), "/")

    #############################################################################

    def get(self, path=""):
        """get path."""
        return self.getManager().get(path)

    #############################################################################
    def help(self):
        """help function."""
        return self.getManager().help()  # pylint: disable=no-member

    #############################################################################
    def getPossibleParameters(self):
        """available trees."""
        return self.getManager().getPossibleParameters()  # pylint: disable=no-member

    #############################################################################
    def setParameter(self, name):
        """tree used."""
        return self.getManager().setParameter(name)  # pylint: disable=no-member

    #############################################################################
    def getLogicalFiles(self):
        """lfns."""
        return self.getManager().getLogicalFiles()  # pylint: disable=no-member

    #############################################################################
    def getFilesPFN(self):
        """PFNS."""
        return self.getManager().getFilesPFN()  # pylint: disable=no-member

    #############################################################################
    def getNumberOfEvents(self, files):
        """number of events."""
        return self.getManager().getNumberOfEvents(files)  # pylint: disable=no-member

    #############################################################################
    def writeJobOptions(
        self, files, optionsFile="jobOptions.opts", savedType=None, catalog=None, savePfn=None, dataset=None
    ):
        """Gaudi card."""
        return self.getManager().writeJobOptions(  # pylint: disable=no-member
            files, optionsFile, savedType, catalog, savePfn, dataset
        )

    #############################################################################
    def getJobInfo(self, lfn):
        """how a file is created."""
        return self.getManager().getJobInfo(lfn)  # pylint: disable=no-member

    #############################################################################
    def setVerbose(self, value):
        """only important information."""
        return self.getManager().setVerbose(value)  # pylint: disable=no-member

    #############################################################################
    def setAdvancedQueries(self, value):
        """Advanced queries."""
        return self.getManager().setAdvancedQueries(value)  # pylint: disable=no-member

    #############################################################################
    def getLimitedFiles(self, selectionDict, sortDict, startItem, maxitems):
        """get files used by Web portal."""
        return self.getManager().getLimitedFiles(  # pylint: disable=no-member
            selectionDict, sortDict, startItem, maxitems
        )

    #############################################################################
    def getAncestors(self, files, depth):
        """ancestor of files."""
        return self.getManager().getAncestors(files, depth)  # pylint: disable=no-member

    #############################################################################
    def getLogfile(self, filename):
        """log file of a given file."""
        return self.getManager().getLogfile(filename)  # pylint: disable=no-member

    #############################################################################
    def writePythonOrJobOptions(self, startItem, maxitems, path, optstype):
        """python job option."""
        return self.getManager().writePythonOrJobOptions(  # pylint: disable=no-member
            startItem, maxitems, path, optstype
        )

    #############################################################################
    def getLimitedInformations(self, startItem, maxitems, path):
        """statistics."""
        return self.getManager().getLimitedInformations(startItem, maxitems, path)  # pylint: disable=no-member

    #############################################################################
    def getProcessingPassSteps(self, in_dict):
        """step."""
        return self.getManager().getProcessingPassSteps(in_dict)  # pylint: disable=no-member

    #############################################################################
    def getMoreProductionInformations(self, prodid):
        """production details."""
        return self.getManager().getMoreProductionInformations(prodid)  # pylint: disable=no-member

    #############################################################################
    def getAvailableProductions(self):
        """available productions."""
        return self.getManager().getAvailableProductions()  # pylint: disable=no-member

    #############################################################################
    def getFileHistory(self, lfn):
        """ "file history."""
        return self.getManager().getFileHistory(lfn)  # pylint: disable=no-member

    #############################################################################
    def getCurrentParameter(self):
        """curent bookkeeping path."""
        return self.getManager().getCurrentParameter()  # pylint: disable=no-member

    #############################################################################
    def getQueriesTypes(self):
        """type of the current query."""
        return self.getManager().getQueriesTypes()  # pylint: disable=no-member

    #############################################################################
    def getProductionProcessingPassSteps(self, in_dict):
        """the steps which produced a given production."""
        return self.getManager().getProductionProcessingPassSteps(in_dict)  # pylint: disable=no-member

    #############################################################################
    def getAvailableDataQuality(self):
        """available data quality."""
        return self.getManager().getAvailableDataQuality()  # pylint: disable=no-member

    #############################################################################
    def setDataQualities(self, values):
        """set data qualities."""
        self.getManager().setDataQualities(values)  # pylint: disable=no-member

    #############################################################################
    def getStepsMetadata(self, bkDict):
        """returns detailed step metadata."""
        return self.getManager().getStepsMetadata(bkDict)  # pylint: disable=no-member

    #############################################################################
    def setFileTypes(self, fileTypeList):
        """it sets the file types."""
        return self.getManager().setFileTypes(fileTypeList)  # pylint: disable=no-member

    #############################################################################
    def getFilesWithMetadata(self, dataset):
        """it sets the file types.

        :param dict dataset: it is a bookkeeping dictionary, which contains the conditions used to retreive the lfns
        :return: S_OK lfns with metadata
        """
        return self.getManager().getFilesWithMetadata(dataset)  # pylint: disable=no-member
