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
"""stores the job parameters."""


class JobParameters(object):
    def __init__(self):
        """initialize the class members."""
        self.name = ""
        self.value = ""
        self.type = ""

    def __repr__(self):
        """formats the output of the print."""
        result = self.name + "  " + self.value + "  " + self.type + "\n"
        return result

    def writeToXML(self):
        """creates an xml string."""
        result = (
            '  <TypedParameter Name="'
            + str(self.name)
            + '" Value="'
            + str(self.value)
            + '" Type="'
            + str(self.type)
            + '"/>\n'
        )
        return result
