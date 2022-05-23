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
"""List file types from the Bookkeeping."""
import DIRAC
from DIRAC.Core.Utilities.DIRACScript import DIRACScript


@DIRACScript()
def main():
    from DIRAC.Core.Base import Script

    Script.setUsageMessage(__doc__ + "\n".join(["Usage:", "  %s [option|cfgfile]" % Script.scriptName]))
    Script.parseCommandLine(ignoreErrors=True)

    from LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient import BookkeepingClient

    bk = BookkeepingClient()
    exitCode = 0

    res = bk.getAvailableFileTypes()

    if res["OK"]:
        dbresult = res["Value"]
        print("Filetypes:")
        for record in dbresult["Records"]:
            print(str(record[0]).ljust(30) + str(record[1]))

    DIRAC.exit(exitCode)


if __name__ == "__main__":
    main()
