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
"""check if a service or an agent is stalled."""
import os

# TODO: This should be modernised to use subprocess(32)
try:
    import commands
except ImportError:
    # Python 3's subprocess module contains a compatibility layer
    import subprocess as commands

from DIRAC import gLogger
from DIRAC.Core.Utilities.DIRACScript import DIRACScript

msg = None


def write_log(mesg):
    """create the log file."""
    global msg
    gLogger.notice(mesg)
    msg += mesg + "\n"


@DIRACScript()
def main():
    global msg

    from DIRAC.Core.Base import Script

    Script.addDefaultOptionValue("LogLevel", "verbose")
    Script.parseCommandLine(ignoreErrors=True)

    from DIRAC.Core.Utilities.Time import fromString, second, dateTime, timeInterval
    from DIRAC.Interfaces.API.DiracAdmin import DiracAdmin

    now = dateTime()
    runit_dir = "/opt/dirac/startup"
    logfile = "log/current"
    pollingtime = 60
    diracAdmin = DiracAdmin()
    mailadress = "lhcb-grid-shifter-oncall@cern.ch"
    subject = "CheckStalled"
    host = os.uname()[1]
    msg = "List of Services / agents which could be stalled on " + host + " \n\n"

    gLogger.getSubLogger("CheckStalledServices")
    write_log("The script " + Script.scriptName + " is running at " + str(now))

    fd = os.listdir(runit_dir)
    # remove the web log as the format is different
    for dirname in fd:
        if dirname.find("Web") == 0:
            fd.remove(dirname)

    for dirname in fd:
        status, result = commands.getstatusoutput("runsvstat " + runit_dir + "/" + dirname)
        filename = runit_dir + "/" + dirname + "/" + logfile
        with open(filename, "r") as fl:
            listLines = fl.readlines()
        lastLine = listLines[-1]
        write_log("Checking ----> " + dirname)
        for line in listLines:
            if line.find("WARN: Server is not who"):
                if line.find("Polling time") != -1:
                    try:
                        pollingtime = line.split(":")[4].split(" ")[1].split(".")[0]
                    except BaseException:
                        try:
                            pollingtime = line.split(":")[7].split(" ")[1].split(".")[0]
                        except BaseException:
                            write_log("    wrong format for Polling Time : " + line)
                            break
                else:
                    lastLine = line

        lastLineList = lastLine.split(" ")
        try:
            lastupdate = fromString(lastLineList[0] + " " + lastLineList[1])
        except BaseException:
            write_log("    EXCEPT : " + dirname)
            write_log("   last line is " + str(lastLineList))

        if isinstance(pollingtime, int):
            if int(pollingtime) < 59:
                pollingtime = 120

            interval = timeInterval(lastupdate, second * int(pollingtime))
            if not interval.includes(now):
                write_log("    the PollingTime is : " + str(pollingtime) + " s")
                write_log("    last update for " + dirname + " was : " + str(lastupdate))
                write_log("    Polling Time is " + str(pollingtime) + " s")
                write_log("    last known status" + result + "\n")
                write_log("   Last line is : \n" + lastLine)

    res = diracAdmin.sendMail(mailadress, subject, msg, fromAddress="joel.closier@cern.ch")
    if not res["OK"]:
        print("The mail could not be sent")


if __name__ == "__main__":
    main()
