#!/usr/bin/env python
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

from DIRAC.Core.Base.Script import Script


@Script()
def main():

    Script.setUsageMessage("Gives an overview of the grid resources status")
    Script.parseCommandLine()

    from LHCbDIRAC.Interfaces.API.DiracLHCb import DiracLHCb

    DiracLHCb().gridWeather(printOutput=True)


if __name__ == "__main__":
    main()
