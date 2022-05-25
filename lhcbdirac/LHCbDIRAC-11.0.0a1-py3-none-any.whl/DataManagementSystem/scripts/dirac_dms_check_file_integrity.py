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
import DIRAC
from DIRAC.Core.Base.Script import Script


@Script()
def main():
    from LHCbDIRAC.DataManagementSystem.Client.DMScript import DMScript

    dmScript = DMScript()
    dmScript.registerBKSwitches()
    dmScript.registerFileSwitches()

    fixIt = False
    Script.registerSwitch("", "FixIt", "Set replicas problematic if needed")
    Script.setUsageMessage(
        """
  Check the integrity of the state of the storages and information in the File Catalogs
  for a given file or a collection of files.

  Usage:
     %s <lfn | fileContainingLfns> <SE> <status>
  """
        % Script.scriptName
    )

    Script.parseCommandLine()

    for opt, val in Script.getUnprocessedSwitches():
        if opt == "FixIt":
            fixIt = True

    from DIRAC import gLogger

    gLogger.setLevel("INFO")
    from LHCbDIRAC.DataManagementSystem.Client.DataIntegrityClient import DataIntegrityClient

    for lfn in Script.getPositionalArgs():
        dmScript.setLFNsFromFile(lfn)
    lfns = dmScript.getOption("LFNs")
    if not lfns:
        print("No LFNs given...")
        Script.showHelp(exitCode=1)

    integrityClient = DataIntegrityClient()
    res = integrityClient.catalogFileToBK(lfns)
    if not res["OK"]:
        gLogger.error(res["Message"])
        DIRAC.exit(1)
    replicas = res["Value"]["CatalogReplicas"]
    metadata = res["Value"]["CatalogMetadata"]
    res = integrityClient.checkPhysicalFiles(replicas, metadata, fixIt=fixIt)
    if not res["OK"]:
        gLogger.error(res["Message"])
        DIRAC.exit(1)
    DIRAC.exit(0)


if __name__ == "__main__":
    main()
