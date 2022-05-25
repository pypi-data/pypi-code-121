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
"""reads the data quality."""


class Quality(object):
    """Quality class."""

    def __init__(self):
        """initialize the class members."""
        self.group = ""
        self.flag = ""
        self.params = []

    def addParam(self, param):
        """adds a param."""
        self.params += [param]

    def __repr__(self):
        """formats the output of the print."""
        result = "Quality: "
        result += self.group + " " + self.flag + "\n"

        for param in self.params:
            result += str(param)

        result += "\n"
        return result

    def writeToXML(self):
        """creates an XML string."""
        return '<Quality Group="' + self.group + '" Flag="' + self.flag + '"/>\n'
