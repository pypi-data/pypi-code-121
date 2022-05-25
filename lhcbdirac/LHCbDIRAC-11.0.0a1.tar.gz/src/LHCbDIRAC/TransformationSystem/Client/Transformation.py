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
"""Client module to deal with transformations, but mostly dedicated to
DataManipulation (e.g.: replications)"""

from DIRAC import gLogger, S_OK, S_ERROR
from DIRAC.TransformationSystem.Client.Transformation import Transformation as DIRACTransformation
from DIRAC.DataManagementSystem.Utilities.DMSHelpers import resolveSEGroup

from LHCbDIRAC.TransformationSystem.Client.TransformationClient import TransformationClient
from LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient import BookkeepingClient

COMPONENT_NAME = "Transformation"


class Transformation(DIRACTransformation):
    """Class for dealing with Transformation objects."""

    #############################################################################

    def __init__(self, transID=0, transClientIn=None):
        """Just params setting.

        transClient is passed here as LHCbDIRAC TransformationsClient, it
        will be self.transClient
        """

        if not transClientIn:
            self.transClient = TransformationClient()
        else:
            self.transClient = transClientIn

        super(Transformation, self).__init__(transID=transID, transClient=self.transClient)

    #############################################################################

    def testBkQuery(self, bkQuery, printOutput=False, bkClient=None):
        """just pretty print of the result of a BK Query."""

        if bkClient is None:
            bkClient = BookkeepingClient()

        res = bkClient.getFiles(bkQuery)
        if not res["OK"]:
            return self._errorReport(res, "Failed to perform BK query")
        gLogger.info("The supplied query returned %d files" % len(res["Value"]))
        if printOutput:
            self._prettyPrint(res)
        return S_OK(res["Value"])

    #############################################################################

    def setBkQuery(self, queryDict, test=False):
        """set a BKK Query."""
        if test:
            res = self.testBkQuery(queryDict)
            if not res["OK"]:
                return res
        transID = self.paramValues["TransformationID"]
        if self.exists and transID:
            res = self.transClient.addBookkeepingQuery(transID, queryDict)
            if not res["OK"]:
                return res
        self.item_called = "BkQuery"
        self.paramValues[self.item_called] = queryDict
        return S_OK()

    #############################################################################

    def getBkQuery(self, printOutput=False):
        """get a BKK Query."""
        if self.paramValues["BkQuery"]:
            return S_OK(self.paramValues["BkQuery"])
        res = self.__executeOperation("getBookkeepingQuery")
        if not res["OK"]:
            return res
        self.item_called = "BkQuery"
        self.paramValues[self.item_called] = res["Value"]
        return S_OK(res["Value"])

    #############################################################################

    def deleteTransformationBkQuery(self):
        """delete a BKK Query."""
        transID = self.paramValues["TransformationID"]
        if self.exists and transID:
            res = self.transClient.deleteTransformationBookkeepingQuery(transID)
            if not res["OK"]:
                return res
        self.item_called = "BkQuery"
        self.paramValues[self.item_called] = {}
        return S_OK()

    #############################################################################

    def addTransformation(self, addFiles=True, printOutput=False):
        """Add a transformation, using TransformationClient()"""
        res = super(Transformation, self).addTransformation(addFiles, printOutput)
        if res["OK"]:
            transID = res["Value"]
        else:
            return res

        bkQuery = self.paramValues.get("BkQuery")
        if bkQuery:
            res = self.setBkQuery(bkQuery)
            if not res["OK"]:
                return self._errorReport(res, "Failed to set BK query")
        else:
            self.transClient.deleteTransformationParameter(transID, "BkQuery")

        return S_OK(transID)

    def setSEParam(self, key, seList):
        return self.__setSE(key, seList)

    def setAdditionalParam(self, key, val):
        self.item_called = key
        return self.__setParam(val)

    # This is a trick to overwrite the __checkSEs method of the base class
    def _Transformation__checkSEs(self, seList):
        # This test allows to set some parameters empty
        if seList == []:
            return S_OK()
        if resolveSEGroup(seList):
            return S_OK()
        gLogger.error("Some SEs are unknown in %s" % ",".join(seList))
        return S_ERROR("Some StorageElements not known")
