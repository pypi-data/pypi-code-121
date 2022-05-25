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
"""stores the replica information."""
from DIRAC import gLogger


class ReplicaParam(object):
    """ReplicaParam class."""

    def __init__(self):
        """initialize the member of the class."""
        self.file = ""
        self.name = ""
        self.location = ""
        self.se = ""
        self.action = ""

    def __repr__(self):
        """formats the output of print."""
        result = "\n Replica:\n"
        result += self.file + " " + self.name + " " + self.location + " "
        result += self.se + " " + self.action

        return result

    def writeToXML(self, flag=True):
        """creates an XML string."""
        # job replica param
        gLogger.info("replica param", str(flag))
        if flag:
            result = '     <Replica Name="' + self.name + '" Location="' + self.location + '"/>\n'

        else:
            result = '<Replica File="' + self.file + '"\n'
            result += '      Name="' + self.name + '"\n'
            result += '      Location="' + self.location + '"\n'
            result += '      SE="' + self.se + '"/> \n'

        return result
