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
"""Retrieve from Bookkeeping the number of Jobs at each Site for a given Production."""
import DIRAC
from DIRAC.Core.Utilities.DIRACScript import DIRACScript


@DIRACScript()
def main():
    from DIRAC.Core.Base import Script

    Script.setUsageMessage(
        __doc__
        + "\n".join(
            [
                "Usage:",
                "  %s [option|cfgfile] ... ProdID" % Script.scriptName,
                "Arguments:",
                "  ProdID:   Production ID (mandatory)",
            ]
        )
    )
    Script.parseCommandLine(ignoreErrors=True)
    args = Script.getPositionalArgs()
    print("args =", args)
    if len(args) < 1:
        Script.showHelp()

    exitCode = 0

    from LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient import BookkeepingClient

    bk = BookkeepingClient()
    try:
        prod = int(args[0])
    except BaseException:
        Script.showHelp(exitCode=1)

    res = bk.getNbOfJobsBySites(prod)

    if res["OK"]:
        if not res["Value"]:
            print("No jobs for production", prod)
            DIRAC.exit(0)
        sites = dict([(site, num) for num, site in res["Value"]])
        shift = 0
        for site in sites:
            shift = max(shift, len(site) + 2)
        print("Site Name".ljust(shift), "Number of jobs")
        for site in sorted(sites):
            print(site.ljust(shift), str(sites[site]))
    else:
        print("ERROR getting number of jobs for %s:" % str(prod), res["Message"])
        exitCode = 2


if __name__ == "__main__":
    main()
