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
"""stores the replica readed from an xml."""
from DIRAC import gLogger


class Replica(object):
    """Replica class."""

    #############################################################################
    def __init__(self):
        """initialize the class members."""
        self.params = []
        self.name = ""

    #############################################################################
    def addParam(self, param):
        """sets the parameters."""
        self.params += [param]

    #############################################################################
    def __repr__(self):
        """It idents the print output."""
        result = "\nReplica: "
        result += self.name + "\n"
        for param in self.params:
            result += str(param)

        return result

    #############################################################################
    def writeToXML(self):
        """writs an XML file."""
        gLogger.debug("Replica XML writing!!!")
        result = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE Replicas SYSTEM "book.dtd">
<Replicas>
"""
        for param in self.params:
            result += param.writeToXML(False)

        result += "</Replicas>"
        return result

    #############################################################################
