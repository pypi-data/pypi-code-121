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
"""Base Entity System Manager."""


import os
from DIRAC import gLogger, S_OK, S_ERROR


class BaseESManager(object):
    """Base Entity manager class."""

    #############################################################################
    def __init__(self):
        """Initialize the class members."""
        self.__fileSeparator = "/"

    #############################################################################
    def getPathSeparator(self):
        """The path separator used."""
        return self.__fileSeparator

    #############################################################################
    def list(self, path="/", selectionDict=None, sortDict=None, startItem=0, maxitems=0):
        """list the path."""
        selectionDict = selectionDict if selectionDict is not None else {}
        sortDict = sortDict if sortDict is not None else {}
        gLogger.error("This method is not implemented!" + (str(self.__class__)))
        gLogger.error(str(path))
        gLogger.error(str(selectionDict))
        gLogger.error(str(sortDict))
        gLogger.error(str(startItem))
        gLogger.error(str(maxitems))
        return S_ERROR("Not Implemented!")

    #############################################################################
    @staticmethod
    def getAbsolutePath(path):
        """absolute path."""
        # get current working directory if empty
        if path == "" or path is None:
            path = "."
            # convert it into absolute path
        try:
            path = os.path.abspath(path)
            return S_OK(path)
        except IOError as ex:
            return S_ERROR("getAbsalutePath: " + str(ex))

    #############################################################################
    def mergePaths(self, path1, path2):
        """merge two path."""
        gLogger.debug("mergePaths(path1, path2) with input " + str(path1) + ", " + str(path2))
        path = self.getAbsolutePath(os.path.join(path1, path2))
        return path

    #############################################################################
    def get(self, path=""):
        """the path element."""
        gLogger.warn("not implemented" + path + str(self.__class__))
        return S_ERROR("Not implemented!")
