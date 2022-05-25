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
"""Restart any agent  and service installed on a VOBOX."""
import re
import os
import sys

from DIRAC.Core.Base.Script import Script


@Script()
def main():
    if "DIRAC" not in os.environ:
        print("The DIRAC environment is not set")
        sys.exit(0)
    else:
        diracroot = os.environ["DIRAC"]

    if os.path.isdir(os.path.join(diracroot, "runit")) and os.path.isdir(os.path.join(diracroot, "startup")):
        diracrunit = os.path.join(diracroot, "runit")
        diracstartup = os.path.join(diracroot, "startup")
        for link in os.listdir(diracstartup):
            system = link.split("_")[0]
            agent = link.split("_")[1]
            if re.search("Agent", link):
                if not os.path.isdir(os.path.join(diracrunit, system)):
                    os.mkdir(os.path.join(diracrunit, system))

                diracsystem = os.path.join(diracrunit, system)
                if not os.path.isdir(os.path.join(diracroot, "control", system, agent)):
                    print(diracsystem)
                    print(agent)
                    os.mkdir(os.path.join(diracroot, "control", system, agent))

                print("Restart Agent " + agent)
                filename_stop = os.path.join(diracroot, "control", system, agent, "stop_agent")
                print(filename_stop)
                with open(filename_stop, "w"):
                    pass
            else:
                if re.search("Framework_SystemAdministrator", link):
                    print("Skip Framework_SystemAdministrator")
                else:
                    print("Restart Service " + os.path.join(diracstartup, link))
                    os.system("runsvctrl t " + os.path.join(diracstartup, link))

    sys.exit(0)


if __name__ == "__main__":
    main()
