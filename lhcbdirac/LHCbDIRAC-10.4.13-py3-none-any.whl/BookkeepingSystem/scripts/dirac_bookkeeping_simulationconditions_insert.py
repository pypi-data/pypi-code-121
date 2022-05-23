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
"""Insert a new set of simulation conditions in the Bookkeeping."""
from builtins import input

import DIRAC
from DIRAC import gLogger
from DIRAC.Core.Utilities.DIRACScript import DIRACScript


@DIRACScript()
def main():
    from DIRAC.Core.Base import Script

    Script.setUsageMessage(__doc__ + "\n".join(["Usage:", "  %s [option|cfgfile] ..." % Script.scriptName]))
    Script.parseCommandLine(ignoreErrors=True)

    from LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient import BookkeepingClient

    bk = BookkeepingClient()

    exitCode = 0

    desc = input("SimDescription: ")
    beamcond = input("BeamCond: ")
    beamEnergy = input("BeamEnergy: ")
    generator = input("Generator: ")
    magneticField = input("MagneticField: ")
    detectorCond = input("DetectorCond: ")
    luminosity = input("Luminosity: ")
    g4settings = input("G4settings: ")
    gLogger.notice("Do you want to add these new simulation conditions? (yes or no)")
    value = input("Choice:")
    choice = value.lower()
    if choice in ["yes", "y"]:
        in_dict = {
            "SimDescription": desc,
            "BeamCond": beamcond,
            "BeamEnergy": beamEnergy,
            "Generator": generator,
            "MagneticField": magneticField,
            "DetectorCond": detectorCond,
            "Luminosity": luminosity,
            "G4settings": g4settings,
            "Visible": "Y",
        }
        res = bk.insertSimConditions(in_dict)
        if res["OK"]:
            gLogger.notice("The simulation conditions added successfully!")
        else:
            gLogger.error(res["Message"])
            exitCode = 2
    elif choice in ["no", "n"]:
        gLogger.notice("Aborted!")
    else:
        gLogger.notice("Unexpected choice:", value)
        exitCode = 2

    DIRAC.exit(exitCode)


if __name__ == "__main__":
    main()
