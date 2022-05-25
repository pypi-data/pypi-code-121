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
"""stores the data quality informations."""


class QualityParameters(object):
    def __init__(self):
        """initialize the class members."""
        self.name = ""
        self.value = ""

    def __repr__(self):
        """formats the output of the print command."""
        return self.name + " " + self.value + "\n"

    def writeToXML(self):
        """creates an xml string."""
        return '  <Parameter Name="' + str(self.name) + '" Value="' + str(self.value) + '"/>\n'
