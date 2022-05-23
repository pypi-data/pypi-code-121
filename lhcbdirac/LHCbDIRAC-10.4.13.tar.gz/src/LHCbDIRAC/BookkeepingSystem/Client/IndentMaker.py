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
"""Its ident the debug message."""
TAB = "\t"
SPACE = " "
DEFAULT = "___"


#############################################################################
def _createIndentedString(string, indent):
    """create string."""
    string = string.strip("\n")
    tokens = string.split("\n")
    newstr = ""
    for token in tokens[0:-1]:
        newstr += indent + token + "\n"
    newstr += indent + tokens[-1]
    return newstr


#############################################################################


def prepend(string, indent=DEFAULT):
    """add string."""
    return _createIndentedString(string, indent)


#############################################################################


def append(value, suffix):
    """append...."""
    lines = value.split("\n")
    maxLine = 0
    for line in lines:
        length = len(line)
        if length > maxLine:
            maxLine = length
    string = ""
    formats = "%-" + str(maxLine) + string
    for line in lines:
        string += formats % line
        string += " " + suffix + " \n"
    return string.strip("\n")
