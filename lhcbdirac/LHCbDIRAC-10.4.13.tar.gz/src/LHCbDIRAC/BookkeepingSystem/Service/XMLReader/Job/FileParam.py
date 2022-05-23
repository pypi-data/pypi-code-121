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
"""declare a file parameter."""


class FileParam(object):
    def __init__(self):
        """initialize the class members."""
        self.name = ""
        self.value = ""

    def __repr__(self):
        """formats the output of print."""
        result = "\nFileParam: \n"
        result += self.name + " " + self.value + "\n"
        return result

    def writeToXML(self):
        """creates an xml string."""
        return '    <Parameter  Name="' + self.name + '"     Value="' + self.value + '"/>\n'
