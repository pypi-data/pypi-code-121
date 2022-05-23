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
"""Insert new file types in the Bookkeeping."""
from builtins import input

import DIRAC
from DIRAC import gLogger
from DIRAC.Core.Utilities.DIRACScript import DIRACScript


@DIRACScript()
def main():
    from DIRAC.Core.Base import Script

    Script.setUsageMessage(__doc__ + "\n".join(["Usage:", "  %s [option|cfgfile]" % Script.scriptName]))
    Script.parseCommandLine(ignoreErrors=True)

    from LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient import BookkeepingClient

    bk = BookkeepingClient()

    exitCode = 0

    ftype = input("FileType: ")
    desc = input("Description: ")
    version = input("File type version: ")
    gLogger.notice("Do you want to add this new file type? (yes or no)")
    value = input("Choice:")
    choice = value.lower()
    if choice in ["yes", "y"]:
        res = bk.insertFileTypes(ftype.upper(), desc, version)
        if res["OK"]:
            gLogger.notice("The file types added successfully!")
        else:
            gLogger.error("Error discovered!", res["Message"])
    elif choice in ["no", "n"]:
        gLogger.notice("Aborted!")
    else:
        gLogger.error("Unexpected choice:", value)

    DIRAC.exit(exitCode)


if __name__ == "__main__":
    main()
