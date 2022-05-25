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
"""dirac-production-runjoblocal.

Module created to run failed jobs locally on a CVMFS-configured machine.
It creates the necessary environment, downloads the necessary files, modifies the necessary
files and runs the job

Usage:
  dirac-production-runjoblocal (job ID) (Data imput mode) -  No parenthesis
"""
import sys
import os
import shutil
import ssl

if sys.version_info < (3,):
    from urllib2 import urlopen as url_library_urlopen  # pylint: disable=no-name-in-module,import-error
    from urllib2 import URLError as url_library_URLError  # pylint: disable=no-name-in-module,import-error
else:
    from urllib.request import urlopen as url_library_urlopen  # pylint: disable=no-name-in-module,import-error
    from urllib.error import URLError as url_library_URLError  # pylint: disable=no-name-in-module,import-error

from DIRAC import S_OK
from DIRAC.Core.Utilities.File import mkDir
from DIRAC.Core.Base.Script import Script


def __runSystemDefaults(jobID=None):
    """Creates the environment for running the job and returns the path for the
    other functions."""
    tempdir = "LHCbjob" + str(jobID) + "temp"
    os.environ["VO_LHCB_SW_DIR"] = "/cvmfs/lhcb.cern.ch"
    mkDir(tempdir)

    basepath = os.getcwd()
    return basepath + os.path.sep + tempdir + os.path.sep


def __downloadJobDescriptionXML(jobID, basepath):
    """Downloads the jobDescription.xml file into the temporary directory
    created."""
    from DIRAC.Interfaces.API.Dirac import Dirac

    jdXML = Dirac()
    jdXML.getInputSandbox(jobID, basepath)


def __modifyJobDescription(jobID, basepath, downloadinputdata):
    """Modifies the jobDescription.xml to, instead of DownloadInputData, it uses
    InputDataByProtocol."""
    if not downloadinputdata:
        from xml.etree import ElementTree as et

        archive = et.parse(basepath + "InputSandbox" + str(jobID) + os.path.sep + "jobDescription.xml")
        for element in archive.iter():
            if element.text == "DIRAC.WorkloadManagementSystem.Client.DownloadInputData":
                element.text = "DIRAC.WorkloadManagementSystem.Client.InputDataByProtocol"
                archive.write(basepath + "InputSandbox" + str(jobID) + os.path.sep + "jobDescription.xml")
                return S_OK("Job parameter changed from DownloadInputData to InputDataByProtocol.")


def __downloadPilotScripts(basepath):
    """
    Downloads the scripts necessary to configure the pilot
    """
    context = ssl._create_unverified_context()
    for fileName in [
        "dirac-pilot.py",
        "dirac-install.py",
        "pilotCommands.py",
        "pilotTools",
        "MessageSender",
        "PilotLogger.py",
        "PilotLoggerTools.py",
    ]:
        remoteFile = url_library_urlopen(
            os.path.join("https://raw.githubusercontent.com/DIRACGrid/Pilot/master/Pilot/", fileName),
            timeout=10,
            context=context,
        )
        with open(fileName, "wb") as localFile:
            localFile.write(remoteFile.read())

    remoteFile = url_library_urlopen(
        os.path.join("https://gitlab.cern.ch/lhcb-dirac/LHCbPilot/-/raw/master/LHCbPilot/LHCbPilotCommands.py"),
        timeout=10,
        context=context,
    )
    with open("LHCbPilotCommands.py", "wb") as localFile:
        localFile.write(remoteFile.read())
    remoteFile = url_library_urlopen(
        os.path.join("https://gitlab.cern.ch/lhcb-dirac/LHCbPilot/-/raw/master/LHCbPilot/LHCbPilotTools.py"),
        timeout=10,
        context=context,
    )
    with open("LHCbPilotTools.py", "wb") as localFile:
        localFile.write(remoteFile.read())


def __configurePilot(basepath):
    """Configures the pilot."""
    pilotCmd = "dirac-pilot.py -S LHCb-Production -l LHCb "
    pilotCmd += "-C dips://lhcb-conf-dirac.cern.ch:9135/Configuration/Server "
    pilotCmd += "-N ce.debug.ch -Q default -n DIRAC.JobDebugger.cern -M 1 "
    pilotCmd += "-E LHCbPilot "
    pilotCmd += "-X LHCbConfigureBasics,LHCbConfigureSite,LHCbConfigureArchitecture,LHCbConfigureCPURequirements -dd"
    out = os.system("python " + basepath + pilotCmd)
    if not out:
        directory = os.path.expanduser("~") + os.path.sep
        os.rename(directory + ".dirac.cfg", directory + ".dirac.cfg.old")
        shutil.copyfile(directory + "pilot.cfg", directory + ".dirac.cfg")
        return S_OK("Pilot successfully configured.")


#   else:
#     some DErrno message


def __runJobLocally(jobID, basepath):
    """Runs the job!"""
    from LHCbDIRAC.Interfaces.API.LHCbJob import LHCbJob

    localJob = LHCbJob(basepath + "InputSandbox" + str(jobID) + os.path.sep + "jobDescription.xml")
    localJob.setInputSandbox(os.getcwd() + "pilot.cfg")
    localJob.setConfigArgs(os.getcwd() + "pilot.cfg")
    os.chdir(basepath)
    localJob.runLocal()


@Script()
def main():

    Script.registerSwitch("D:", "Download=", "Defines data acquisition as DownloadInputData")
    Script.registerSwitch("P:", "Protocol=", "Defines data acquisition as InputDataByProtocol")
    Script.parseCommandLine(ignoreErrors=False)

    Script.setUsageMessage(
        __doc__
        + "\n".join(
            [
                "\nUsage:",
                "dirac-production-runjoblocal [Data imput mode] [job ID]" "\nArguments:",
                "  Download (Job ID): Defines data acquisition as DownloadInputData",
                "  Protocol (Job ID): Defines data acquisition as InputDataByProtocol\n",
            ]
        )
    )

    _downloadinputdata = False
    _jobID = None

    for switch in Script.getUnprocessedSwitches():
        if switch[0] in ("D", "Download"):
            _downloadinputdata = True
            _jobID = switch[1]
        if switch[0] in ("P", "Protocol"):
            _downloadinputdata = False
            _jobID = switch[1]

    usedDir = os.path.expanduser("~") + os.path.sep
    try:
        _path = __runSystemDefaults(_jobID)

        __downloadJobDescriptionXML(_jobID, _path)

        __modifyJobDescription(_jobID, _path, _downloadinputdata)

        __downloadPilotScripts(_path)

        __configurePilot(_path)

        __runJobLocally(_jobID, _path)

    finally:
        os.chdir(usedDir)
        os.rename(usedDir + ".dirac.cfg.old", usedDir + ".dirac.cfg")


if __name__ == "__main__":
    main()
