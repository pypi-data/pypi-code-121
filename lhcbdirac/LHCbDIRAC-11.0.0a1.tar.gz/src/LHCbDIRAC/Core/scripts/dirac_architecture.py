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
"""Returns the platform supported by the current WN."""
import LbPlatformUtils
from DIRAC.Core.Base.Script import Script


def sendMail(msg=""):
    """send a notification mail when no platform is found."""
    from DIRAC.FrameworkSystem.Client.NotificationClient import NotificationClient
    from DIRAC.ConfigurationSystem.Client.Helpers.Operations import Operations
    from DIRAC import gConfig

    mailAddress = Operations().getValue("EMail/JobFailures", "Vladimir.Romanovskiy@cern.ch")
    site = gConfig.getValue("LocalSite/Site")
    ce = gConfig.getValue("LocalSite/GridCE")
    queue = gConfig.getValue("LocalSite/CEQueue")
    body = "*** THIS IS AN AUTOMATED MESSAGE ***" + "\n\n" + msg + "\n\n"
    body = body + "At site %s, CE = %s, queue = %s" % (site, ce, queue) + "\n\n"

    for mA in mailAddress.replace(" ", "").split(","):
        NotificationClient().sendMail(
            mailAddress, "Problem with DIRAC architecture", body, "federico.stagni@cern.ch", localAttempt=False
        )


@Script()
def main():

    Script.registerSwitch("", "BinaryTag", "   Print the host binary tag instead of the host dirac_platform")
    Script.parseCommandLine(ignoreErrors=True)

    from DIRAC import gConfig, gLogger, exit as dExit
    from DIRAC.ConfigurationSystem.Client.Helpers.Operations import Operations

    parList = Script.getUnprocessedSwitches()
    for switch, _val in parList:
        if switch == "BinaryTag":
            try:
                # Get the binaryTag name. If an error occurs, an exception is thrown
                binaryTag = LbPlatformUtils.host_binary_tag()
                if not binaryTag:
                    gLogger.fatal("There is no binaryTag corresponding to this machine")
                    sendMail("There is no binaryTag corresponding to this machine")
                    dExit(1)
                print(binaryTag)
                dExit(0)
            except Exception as e:
                msg = "Exception getting binaryTag: " + repr(e)
                gLogger.exception(msg, lException=e)
                sendMail(msg)
                dExit(1)

    try:
        site = gConfig.getValue("/LocalSite/Site")
        grid = site.split(".")[0]
        ce = gConfig.getValue("/LocalSite/GridCE")

        allowContainers = gConfig.getValue("/Resources/Sites/%s/%s/CEs/%s/AllowContainers" % (grid, site, ce), None)
        if allowContainers is None:
            allowContainers = gConfig.getValue("/Resources/Sites/%s/%s/AllowContainers" % (grid, site), None)
        if allowContainers is None:
            allowContainers = Operations().getValue("GaudiExecution/AllowContainers", "no")

        if allowContainers.lower() in ("yes", "true", "all"):
            allowContainers = True
        elif allowContainers.lower() in ("no", "false", "none", ""):
            allowContainers = False
        else:
            gLogger.warn("Invalid value for AllowContainers", repr(allowContainers))
            allowContainers = False

        # Get the platform name. If an error occurs, an exception is thrown
        platform = LbPlatformUtils.dirac_platform(allow_containers=allowContainers)
        if not platform:
            gLogger.fatal("There is no platform corresponding to this machine")
            sendMail("There is no platform corresponding to this machine")
            dExit(1)
        print(platform)
        dExit(0)

    except Exception as e:
        msg = "Exception getting platform: " + repr(e)
        gLogger.exception(msg, lException=e)
        sendMail(msg)
        dExit(1)


if __name__ == "__main__":
    main()
