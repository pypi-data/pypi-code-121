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
"""stores the job configuration."""


class JobConfiguration(object):
    def __init__(self):
        """initialize the class members."""
        self.configName = ""  # None
        self.configVersion = ""  # None
        self.date = ""  # None
        self.time = ""  # None

    def __repr__(self):
        """formats the output of the print."""
        result = "JobConfiguration: \n"
        result += "ConfigName:" + self.configName + "\n"
        result += "ConfigVersion:" + self.configVersion + "\n"
        result += "Date and Time:" + self.date + " " + self.time
        return result

    def writeToXML(self):
        """creates an xml string."""
        result = (
            '<Job ConfigName="'
            + self.configName
            + '" ConfigVersion="'
            + self.configVersion
            + '" Date="'
            + self.date
            + '" Time="'
            + self.time
            + '">\n'
        )
        return result
