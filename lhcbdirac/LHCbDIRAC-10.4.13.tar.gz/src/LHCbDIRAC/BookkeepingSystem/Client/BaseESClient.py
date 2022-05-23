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
"""Base Entity System client."""
from LHCbDIRAC.BookkeepingSystem.Client.BaseESManager import BaseESManager


class BaseESClient(object):
    """Basic client."""

    #############################################################################
    def __init__(self, esManager=BaseESManager(), path="/"):
        """The Entity manager must be initialized which will be used to manipulate
        the databaase."""
        self.__ESManager = esManager
        result = self.getManager().getAbsolutePath(path)
        if result["OK"]:
            self.__currentDirectory = result["Value"]

    #############################################################################
    def list(self, path="", selectionDict=None, sortDict=None, startItem=0, maxitems=0):
        """It lists the database content as a Linux File System."""
        selectionDict = selectionDict if selectionDict is not None else {}
        sortDict = sortDict if sortDict is not None else {}
        res = self.getManager().mergePaths(self.__currentDirectory, path)
        if res["OK"]:
            return self.getManager().list(res["Value"], selectionDict, sortDict, startItem, maxitems)
        return res

    #############################################################################
    def getManager(self):
        """It returns the manager whicg used to manipulate the database."""
        return self.__ESManager

    #############################################################################
    def get(self, path=""):
        """It return the actual directory."""
        return self.getManager().get(path)

    #############################################################################
    def getPathSeparator(self):
        """It returns the space separator."""
        return self.getManager().getPathSeparator()

    #############################################################################
