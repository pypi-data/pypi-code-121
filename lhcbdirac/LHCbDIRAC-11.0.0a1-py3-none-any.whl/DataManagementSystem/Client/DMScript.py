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
"""DMScript is a class that creates default switches for DM scripts, decodes
them and sets flags The module also provides a function for printing pretty
results from DMS queries."""
import os
import six
import sys
import time
import tempfile

import DIRAC
from DIRAC import gLogger, gConfig
from DIRAC.Core.Base.Script import Script
from DIRAC.DataManagementSystem.Utilities.DMSHelpers import resolveSEGroup

from LHCbDIRAC.BookkeepingSystem.Client.BKQuery import BKQuery
from LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient import BookkeepingClient


def __printDictionary(dictionary, offset=0, shift=0, empty="Empty directory", depth=9999):
    """Dictionary pretty printing."""
    key_max = 0
    value_max = 0
    for key, value in dictionary.items():
        key_max = max(key_max, len(str(key)))
        value_max = max(value_max, len(str(value)))
    center = key_max + offset
    newOffset = offset + (shift if shift else key_max)
    for key in sorted(dictionary):
        value = dictionary[key]
        if isinstance(value, dict):
            if not depth:
                value = list(value)
            elif value != {}:
                gLogger.notice("%s%s : " % (offset * " ", key))
                __printDictionary(value, offset=newOffset, shift=shift, empty=empty, depth=depth - 1)
            elif key not in ("Failed", "Successful"):
                gLogger.notice("%s%s : %s" % (offset * " ", key, empty))
        if isinstance(value, (list, set)):
            if not value:
                gLogger.notice("%s%s : %s" % (offset * " ", key, "[]"))
            else:
                gLogger.notice("%s%s : " % (offset * " ", key))
                for val in sorted(value):
                    gLogger.notice("%s%s" % (newOffset * " ", val))
        elif not isinstance(value, dict):
            # In case value contains \n, indent the lines
            toPrint = str(value).split("\n")
            gLogger.notice("%s : %s" % (str(key).rjust(center), toPrint.pop(0)))
            for line in toPrint:
                gLogger.notice((center + 3) * " " + line)


def printDMResult(result, shift=4, empty="Empty directory", script=None, depth=999, offset=0):
    """Printing results returned with 'Successful' and 'Failed' items."""
    if not script:
        script = Script.scriptName
    try:
        if result["OK"]:
            __printDictionary(result["Value"], offset=offset, shift=shift, empty=empty, depth=depth)
            if result["Value"].get("Failed"):
                return 1
            return 0
        gLogger.notice("Error in %s :" % script, result["Message"])
        return 2
    except Exception as e:  # pylint: disable=broad-except
        gLogger.notice("Exception while printing results in %s - Results:" % script, repr(e))
        gLogger.notice(result)
        return 2


class ProgressBar(object):
    """This object prints a title and a progress bar on stderr."""

    def __init__(self, items, width=None, title=None, chunk=None, step=None, interactive=None, log=None):
        """

        :param items: Number of items to enumerate
        :type items: integer
        :param width: width in co.lumns of the progress bar
        :type width: int
        :param title: Title of the progress bar
        :type title: string
        :param chunk: incremental value by which the counter is incremented (in number of items)
        :type chunk: int
        :param step: frequency at which the bar is updated
        :type step: int
        :param interactive: if False, no printout
        :type interactive: boolean
        """
        if title is None:
            title = ""
        else:
            title += " "
        if width is None:
            width = 50
        if chunk is None:
            chunk = 1
        if step is None:
            step = 1
        if interactive is None:
            interactive = True
        self._log = log if not interactive else None
        self._step = step
        self._width = width
        self._loopNumber = 0
        self._itemCounter = 0
        self._items = items
        self._chunk = chunk
        self._startTime = time.time()
        self._progress = 0
        self._showBar = bool(items > chunk) and bool(items > step) and interactive and sys.stderr.isatty()
        self._interactive = interactive
        self._title = title
        self._backspace = 0
        self._writeTitle()

    def _writeTitle(self):
        """Write the progress bar title to stderr."""
        if not self._interactive:
            return
        if self._showBar:
            sys.stderr.write("%s|%s|" % (self._title, self._width * " "))
            self._backspace = self._width + 1
        else:
            sys.stderr.write(self._title)
        sys.stderr.flush()

    def loop(self, increment=True):
        """Called at each iteration of the loop If the iteration modulo "step" is
        0, update the bar Increment the counter of items by "chunk"."""
        if not self._interactive:
            return
        showBar = self._showBar and (self._loopNumber % self._step) == 0
        fraction = min(float(self._itemCounter) / float(self._items), 1.0)
        if increment:
            self._loopNumber += 1
            self._itemCounter += self._chunk
        else:
            showBar = self._showBar
        if showBar:
            progress = int(round(self._width * fraction))
            elapsed = time.time() - self._startTime
            if elapsed > 30.0 and fraction:
                rest = int(elapsed * (1 - fraction) / fraction)
                estimate = " (%d seconds left)" % rest
            else:
                estimate = ""
            blockBlue = "\033[46m"
            endblock = "\033[0m"
            sys.stderr.write(
                "%s%s%s| %5.1f%%%s\033[K"
                % (
                    self._backspace * "\b",
                    blockBlue + (progress - self._progress) * " " + endblock,
                    (self._width - progress) * " ",
                    100.0 * fraction,
                    estimate,
                )
            )
            self._backspace = self._width + 8 - progress + len(estimate)
            self._progress = progress
            sys.stderr.flush()

    def endLoop(self, message=None, timing=True):
        """Closes the progress bar, printing a message and/or the timing since the
        bar was created."""
        if message is None:
            message = "completed"
        timingMsg = " in %.1f seconds" % (time.time() - self._startTime)
        if not self._interactive:
            # Print out message if defined
            if self._log:
                self._log("%s %s %s" % (self._title, message, timingMsg))
            return
        if self._showBar:
            sys.stderr.write("%s\033[K: %s" % ((self._progress + self._backspace + 1) * "\b", message))
        if timing:
            if not self._showBar:
                sys.stderr.write(": %s" % message)
            sys.stderr.write(timingMsg)
        sys.stderr.write("\n")
        sys.stderr.flush()

    def comment(self, message, optMsg=""):
        """Print a comment."""
        fullMsg = "\n" + message + " %s" % optMsg if optMsg else ""
        gLogger.notice(fullMsg)
        self._writeTitle()
        self.loop(increment=False)


class DMScript(object):
    """DMScript is a class that creates default switches for DM scripts, decodes
    them and sets flags."""

    def __init__(self):
        """c'tor."""
        self.bkClient = BookkeepingClient()
        self.exceptFileTypes = []
        self.bkClientQuery = None
        self.bkClientQueryDict = {}
        self.options = {}
        self.lastFile = os.path.join(tempfile.gettempdir(), "%d.lastLFNs" % os.getppid())
        self.setLastFile = False
        self.voName = None

    def __voName(self):
        """Returns the name of the VO."""
        if self.voName is None:
            self.voName = gConfig.getValue("/DIRAC/VirtualOrganization", "")
        gLogger.verbose("VO", self.voName)
        return self.voName

    def registerDMSwitches(self):
        """Register switches related to data management, including BK."""
        self.registerBKSwitches()
        self.registerNamespaceSwitches()
        self.registerSiteSwitches()
        self.registerFileSwitches()

    def registerBKSwitches(self):
        """Register switches related to bookkeeping."""
        # BK query switches
        Script.registerSwitch("B:", "BKQuery=", "   Bookkeeping query path", self.setBKQuery)
        Script.registerSwitch(
            "f:",
            "FileType=",
            "   File type (comma separated list, to be used with --Production) [All]",
            self.setFileType,
        )
        Script.registerSwitch(
            "", "ExceptFileType=", "   Exclude the (list of) file types when all are requested", self.setExceptFileTypes
        )
        Script.registerSwitch("", "EventType=", "   Event type", self.setEventType)
        Script.registerSwitch("r:", "Runs=", "   Run or range of runs (r1:r2)", self.setRuns)
        Script.registerSwitch(
            "P:", "Productions=", "   Production ID to search (comma separated list)", self.setProductions
        )
        Script.registerSwitch("", "DQFlags=", "   DQ flag used in query", self.setDQFlags)
        Script.registerSwitch("", "StartDate=", "   Start date for the BK query", self.setStartDate)
        Script.registerSwitch("", "EndDate=", "   End date for the BK query", self.setEndDate)
        Script.registerSwitch("", "Visibility=", "   Required visibility (Yes, No, All) [Yes]", self.setVisibility)
        Script.registerSwitch("", "ReplicaFlag=", "   Required replica flag (Yes, No, All) [Yes]", self.setReplicaFlag)
        Script.registerSwitch("", "TCK=", "   Get files with a given TCK", self.setTCK)

    def registerNamespaceSwitches(self, action="search [ALL]"):
        """Register namespace switches."""
        Script.registerSwitch("D:", "Directory=", "   Directory to " + action, self.setDirectory)

    def registerSiteSwitches(self):
        """SE switches."""
        Script.registerSwitch("g:", "Sites=", "  Sites to consider [ALL] (comma separated list)", self.setSites)
        Script.registerSwitch("S:", "SEs=", "  SEs to consider [ALL] (comma separated list)", self.setSEs)

    def registerFileSwitches(self):
        """File switches."""
        Script.registerSwitch("", "File=", "File containing list of LFNs", self.setLFNsFromFile)
        Script.registerSwitch("l:", "LFNs=", "List of LFNs (comma separated)", self.setLFNs)
        Script.registerSwitch("", "Terminal", "LFNs are entered from stdin (--File /dev/stdin)", self.setLFNsFromTerm)
        Script.registerSwitch("", "LastLFNs", "Use last set of LFNs", self.setLFNsFromLast)

    def registerJobsSwitches(self):
        """Job switches."""
        Script.registerSwitch("", "File=", "File containing list of DIRAC jobIds", self.setJobidsFromFile)
        Script.registerSwitch("j:", "DIRACJobids=", "List of DIRAC Jobids (comma separated)", self.setJobids)
        Script.registerSwitch(
            "", "Terminal", "DIRAC Jobids are entered from stdin (--File /dev/stdin)", self.setJobidsFromTerm
        )

    def setProductions(self, arg):
        """Parse production numbers."""
        prods = []
        if arg.upper() == "ALL":
            self.options["Productions"] = arg
            return DIRAC.S_OK()
        try:
            for prod in arg.split(","):
                if prod.find(":") > 0:
                    pr = prod.split(":")
                    for i in range(int(pr[0]), int(pr[1]) + 1):
                        prods.append(i)
                else:
                    prods.append(prod)
            self.options["Productions"] = [int(prod) for prod in prods]
        except ValueError as e:
            gLogger.error("Invalid production switch value: %s" % arg, repr(e))
            self.options["Productions"] = ["Invalid"]
            return DIRAC.S_ERROR()
        return DIRAC.S_OK()

    def setStartDate(self, arg):
        """Setter."""
        self.options["StartDate"] = arg
        return DIRAC.S_OK()

    def setEndDate(self, arg):
        """Setter."""
        self.options["EndDate"] = arg
        return DIRAC.S_OK()

    def setFileType(self, arg):
        """Setter."""
        fileTypes = arg.split(",")
        self.options["FileType"] = fileTypes
        return DIRAC.S_OK()

    def setEventType(self, arg):
        """Setter."""
        eventTypes = arg.split(",")
        self.options["EventType"] = eventTypes
        return DIRAC.S_OK()

    def setExceptFileTypes(self, arg):
        """Setter."""
        self.exceptFileTypes += arg.split(",")
        return DIRAC.S_OK()

    def setBKQuery(self, arg):
        """Setter."""
        # BKQuery could either be a BK path or a file path that contains the BK items
        self.bkClientQuery = None
        self.bkClientQueryDict = {}
        self.options["BKPath"] = arg
        return DIRAC.S_OK()

    def setRuns(self, arg):
        """Setter."""
        self.options["Runs"] = arg
        return DIRAC.S_OK()

    def setDQFlags(self, arg):
        """Setter."""
        dqFlags = arg.split(",")
        self.options["DQFlags"] = dqFlags
        return DIRAC.S_OK()

    def setTCK(self, arg):
        """Setter."""
        tcks = arg.split(",")
        self.options["TCK"] = tcks
        return DIRAC.S_OK()

    def setVisibility(self, arg):
        """Setter."""
        if arg.lower() in ("yes", "no", "all"):
            self.options["Visibility"] = arg
        else:
            gLogger.error("Unknown visibility flag: %s" % arg)
            return DIRAC.exit(1)
        return DIRAC.S_OK()

    def setReplicaFlag(self, arg):
        """Setter."""
        if arg.lower() in ("yes", "no", "all"):
            self.options["ReplicaFlag"] = arg
        else:
            gLogger.error("Unknown replica flag: %s" % arg)
            return DIRAC.exit(1)
        return DIRAC.S_OK()

    def setDirectory(self, arg):
        """Setter."""
        if os.path.exists(arg) and not os.path.isdir(arg):
            with open(arg, "rt") as inFile:
                directories = [line.split()[0] for line in inFile.read().splitlines() if line.strip()]
        else:
            directories = arg.split(",")
        self.options.setdefault("Directory", set()).update(directories)
        return DIRAC.S_OK()

    def setSites(self, arg):
        """Setter."""
        from DIRAC.DataManagementSystem.Utilities.DMSHelpers import DMSHelpers

        try:
            siteShortNames = DMSHelpers().getShortSiteNames(withStorage=False, tier=(0, 1))
        except AttributeError:
            siteShortNames = {
                "CERN": "LCG.CERN.cern",
                "CNAF": "LCG.CNAF.it",
                "GRIDKA": "LCG.GRIDKA.de",
                "NIKHEF": "LCG.NIKHEF.nl",
                "SARA": "LCG.SARA.nl",
                "PIC": "LCG.PIC.es",
                "RAL": "LCG.RAL.uk",
                "IN2P3": "LCG.IN2P3.fr",
                "RRCKI": "LCG.RRCKI.ru",
            }
        sites = arg.split(",")
        self.options["Sites"] = [siteShortNames.get(site.upper(), site) for site in sites]
        return DIRAC.S_OK()

    def setSEs(self, arg):
        """Setter."""
        self.options["SEs"] = arg.split(",")
        return DIRAC.S_OK()

    def setLFNs(self, arg):
        """Setter."""
        if arg:
            self.options.setdefault("LFNs", set()).update(arg.split(","))
        return DIRAC.S_OK()

    def setLFNsFromTerm(self, arg=None):
        """Setter."""
        return self.setLFNsFromFile(arg)

    def getLFNsFromList(self, lfns, directories=False):
        """Returns a list of LFNs from a list of strings LFNs start with the last
        occurence of /<vo>/ in the file name and ends with a set of delimiters If
        directories is True, only normalized directories (ending with a "/" are
        returned."""
        if isinstance(lfns, six.string_types):
            lfnList = lfns.strip().split(",")
        elif isinstance(lfns, (list, set, dict)):
            lfnList = [lfn.strip() for lfn1 in lfns for lfn in lfn1.split(",")]
        else:
            gLogger.error("getLFNsFromList: invalid type %s" % type(lfns))
            return []
        vo = self.__voName()
        if vo:
            vo = "/%s" % vo
            lfnList = [x.split("LFN:")[-1].strip() for x in lfnList]
            for sep in ('"', ",", "'", ":", "(", ")", ";", "|"):
                lfnList = [x.replace(sep, " ") for x in lfnList]
            lfnList = [vo + lfn.split(vo)[-1].split()[0] if vo in lfn else lfn if lfn == vo else "" for lfn in lfnList]
            lfnList = [lfn.split("?")[0] for lfn in lfnList]
            lfnList = (
                [lfn for lfn in lfnList if lfn.endswith("/")]
                if directories
                else [lfn for lfn in lfnList if not lfn.endswith("/")]
            )
        return sorted(lfn for lfn in set(lfnList) if lfn)

    @staticmethod
    def getJobIDsFromList(jobids):
        """it returns a list of jobids using a string."""
        jobidsList = []
        if isinstance(jobids, six.string_types):
            jobidsList = jobids.split(",")
        elif isinstance(jobids, list):
            jobidsList = [jobid for jobid1 in jobids for jobid in jobid1.split(",")]
        jobidsList = [jobid for jobid in jobidsList if jobid]
        return jobidsList

    def setLFNsFromLast(self, _val):
        """Setter when --Last is used."""
        if os.path.exists(self.lastFile):
            return self.setLFNsFromFile(self.lastFile)
        gLogger.fatal("Last file %s does not exist" % self.lastFile)
        DIRAC.exit(2)

    def setLFNsFromFile(self, arg):
        """Reads the content of a file or from stdin (in which case a temporary
        file will be created) LFNs are not parsed at this stage."""
        if isinstance(arg, six.string_types) and arg.lower() == "last":
            arg = self.lastFile
        # Make a list of files
        if isinstance(arg, six.string_types):
            files = arg.split(",")
        elif isinstance(arg, list):
            files = arg
        elif not arg:
            files = [arg]
        nfiles = 0
        for fName in files:
            try:
                with open(fName if fName else "/dev/stdin", "rt") as inFile:
                    lfns = inFile.read().splitlines()
                nfiles += len(lfns)
            except (EOFError, IOError):
                lfns = fName.split(",")
            self.options.setdefault("LFNs", set()).update(lfns)
        if nfiles:
            self.setLastFile = arg if arg else "term"
        return DIRAC.S_OK()

    def getOptions(self):
        """Returns all options."""
        return self.options

    def getOption(self, switch, default=None):
        """Get a specific items set by the setters."""
        if switch == "SEs":
            # SEs have to be resolved recursively using StorageElementGroups
            return resolveSEGroup(self.options.get(switch, default))
        value = self.options.get(switch, default)
        if switch in ("LFNs", "Directory"):
            # Special case for getting LFNs or directories: parse the option
            if value == default and switch == "Directory":
                value = self.options.get("LFNs", default)
            if not value:
                if not sys.stdin.isatty():
                    # If the input file is a pipe, no need to specify it
                    self.setLFNsFromTerm()
                    value = self.options.get("LFNs", default)
            if value:
                # Parse the LFNs out of the "LFNs" option list
                value = self.getLFNsFromList(value, directories=switch == "Directory")
            if value and self.setLastFile and switch == "LFNs":
                # Storethe list of LFNs in a temporary file
                gLogger.always("Got %d LFNs" % len(value))
                if self.setLastFile != self.lastFile:
                    self.setLastFile = False
                    with open(self.lastFile, "wt") as tmpFile:
                        tmpFile.write("\n".join(sorted(value)))
        if isinstance(value, set):
            # Return a sorted list from a set
            value = sorted(value)
        return value

    def getBKQuery(self, visible=None):
        """Returns a BKQuery object from the requested BK information."""
        mandatoryKeys = {
            ("ConfigName", "ConfigVersion"),
            "Production",
            ("FileType", "RunNumber"),
            ("FileType", "StartRun"),
        }
        if self.bkClientQuery:
            return self.bkClientQuery
        if self.bkClientQueryDict:
            self.bkClientQuery = BKQuery(self.bkClientQueryDict)
        else:
            visible = self.options.get("Visibility", "Yes") if visible is None else visible
            bkPath = self.options.get("BKPath")
            prods = self.options.get("Productions")
            runs = self.options.get("Runs")
            fileTypes = self.options.get("FileType")
            eventTypes = self.options.get("EventType")
            self.bkClientQuery = BKQuery(
                bkQuery=bkPath, prods=prods, runs=runs, fileTypes=fileTypes, eventTypes=eventTypes, visible=visible
            )
        bkQueryDict = self.bkClientQuery.getQueryDict()
        found = False
        for key in mandatoryKeys:
            if isinstance(key, six.string_types) and key in bkQueryDict:
                found = True
                break
            elif isinstance(key, (list, tuple)) and not set(key) - set(bkQueryDict):
                found = True
                break
        if not found:
            self.bkClientQuery = None
            return None
        # Add extra requirements
        self.bkClientQuery.setExceptFileTypes(self.exceptFileTypes)
        if "DQFlags" in self.options:
            self.bkClientQuery.setDQFlag(self.options["DQFlags"])
        if "StartDate" in self.options:
            self.bkClientQuery.setOption("StartDate", self.options["StartDate"])
        if "EndDate" in self.options:
            self.bkClientQuery.setOption("EndDate", self.options["EndDate"])
        if "ReplicaFlag" in self.options:
            self.bkClientQuery.setOption("ReplicaFlag", self.options["ReplicaFlag"])
        if "TCK" in self.options:
            self.bkClientQuery.setOption("TCK", self.options["TCK"])
        return self.bkClientQuery

    def getRequestID(self, prod=None):
        """Get the request ID for a single production."""
        from DIRAC.TransformationSystem.Client.TransformationClient import TransformationClient

        if not prod:
            prod = self.options.get("Productions", [])
        requestID = None
        if isinstance(prod, six.string_types):
            prods = [prod]
        else:
            prods = prod
        if len(prods) == 1 and str(prods[0]).upper() != "ALL":
            res = TransformationClient().getTransformation(prods[0])
            if res["OK"]:
                requestID = int(res["Value"]["TransformationFamily"])
        return requestID

    def setJobidsFromFile(self, arg):
        """It fill a list with DIRAC jobids read from a file
        NOTE: The file format is equivalent to the file format when the content is
        a list of LFNs."""
        try:
            with open(arg if arg else "/dev/stdin", "rt") as inFile:
                jobids = self.getJobIDsFromList(inFile.read().splitlines())
        except IOError as error:
            gLogger.exception("Reading jobids from a file is failed with exception:", repr(error))
            jobids = self.getJobIDsFromList(arg)
        self.options.setdefault("JobIDs", set()).update(jobids)
        return DIRAC.S_OK()

    def setJobids(self, arg):
        """It fill a list with DIRAC Jobids."""
        if arg:
            self.options.setdefault("JobIDs", set()).update(self.getJobIDsFromList(arg))
        return DIRAC.S_OK()

    def setJobidsFromTerm(self):
        """It is used to fill a list with jobids."""
        return self.setJobidsFromFile(None)
