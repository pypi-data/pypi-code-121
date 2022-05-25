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
"""
  Execute a (list of) commands taking arguments from a file.
  Usage:
      dirac-loop [File] Command [Command2...] [option|cfgfile]

  Arguments:
     File: File containing the strings to be appended to the command (default /dev/stdin)
           If the arguments are BK paths, the script reduces the paths merging event and file types
           (use --NoMerge to disable)
     Command: Command to execute (separate with spaces)
              If command terminates with ", a " is appended after the argument
              If the command contains the string @arg@,
                it is replaced by the argument rather than the argument appended
              If the command itself is dirac-loop, then the first occurrence only of @arg@ is replaced,
              which allows recursive calls
"""
import os
import tempfile
import subprocess
from collections import defaultdict


from DIRAC.Core.Base.Script import Script
from DIRAC.Core.Utilities.List import breakListIntoChunks


def reduceArgs(noMerge, arguments, maxList=20):
    """
    If the arguments look like BK paths (start with /LHCb or /MC), try to
    reduce the list of BK paths by merging event types or file types into a
    list.

    :param bool: if set, do not merge arguments if BK paths
    :param list arguments: list of arguments
    :param int maxList: maximum number of event/file types to put in a resulting merged argument
    """
    if noMerge:
        return arguments
    others = []
    placeHolder = "@@"
    for item in [-1, -2]:
        reducedDict = defaultdict(set)
        for path in arguments:
            path = path.strip()
            if path.startswith("/LHCb") or path.startswith("/MC"):
                parsed = path.split("/")
                val = parsed[item]
                parsed[item] = placeHolder
                holderPath = "/".join(parsed)
                reducedDict[holderPath].add(val)
            else:
                others.append(path)
        # Don't allow list of event or file types too long
        arguments = []
        for holderPath, values in reducedDict.items():
            for chunk in breakListIntoChunks(sorted(values), maxList):
                arguments.append(holderPath.replace(placeHolder, ",".join(chunk)))
    # Now sort out the conditions
    conditions = {}
    finalArgs = [arg for arg in arguments if not arg.startswith("/LHCb")]
    for path in [arg for arg in arguments if arg.startswith("/LHCb")]:
        parsed = path.split("/")
        cond = parsed[3]
        parsed[3] = ""
        conditions.setdefault("/".join(parsed), []).append((path, cond))
    for newPath, condTuple in conditions.items():
        if len(condTuple) != 2:
            finalArgs += [path for (path, _c) in condTuple]
        else:
            if len(set(["-".join(cond.split("-")[0:2])])) == 1:
                finalArgs.append(newPath)
            else:
                finalArgs += [path for (path, _c) in condTuple]

    return sorted(others + finalArgs)


@Script()
def main():
    from DIRAC import gLogger, exit

    Script.registerSwitch("", "NoMerge", "If set, do not merge arguments if BK paths")
    Script.registerSwitch("", "Items=", "Alternative way of passing list of arguments")
    Script.registerSwitch("", "NoParse", "Consider the full lines are arguments and not only the first word")
    Script.registerSwitch("", "Path", "Look for a path in the lines")
    Script.registerSwitch("", "Terse", "Do not print the command executed")
    Script.registerSwitch("", "Last", "Execute with same items as previous call")
    Script.registerSwitch("", "ShowLast", "Show last items used")
    Script.setUsageMessage("\n".join([__doc__]))
    Script.parseCommandLine(ignoreErrors=True)
    args = Script.getPositionalArgs()

    noMerge = False
    noParse = False
    terse = False
    arguments = []
    path = False
    last = False
    showLast = False
    lastFile = os.path.join(tempfile.gettempdir(), "%d.lastLoops" % os.getppid())
    for switch, val in Script.getUnprocessedSwitches():
        if switch == "NoMerge":
            noMerge = True
        elif switch == "NoParse":
            noParse = True
        elif switch == "Items":
            arguments = val.split(",")
        elif switch == "Terse":
            terse = True
        elif switch == "Path":
            path = True
        elif switch == "Last":
            last = True
        elif switch == "ShowLast":
            showLast = True
            last = True

    if len(args) < 1:
        Script.showHelp(exitCode=1)

    if not arguments:
        if os.path.exists(args[0]):
            oFile = args.pop(0)
        elif last:
            oFile = lastFile
        else:
            oFile = "/dev/stdin"
        with open(oFile, "r") as fd:
            arguments = fd.read().split("\n")
        if showLast:
            gLogger.notice("Last items used:", "\n" + "\n".join(arguments))
            exit(0)

    commands = args

    argList = []
    for arg in arguments:
        if not arg.strip():
            continue
        if path:
            # Look for a path in the line
            # "Real Data" is an exception in BK path (i.e. with space in it)... BKQuery understands without a space
            #    hence for simplicity here, remove the space to allow split() to work ;-)
            words = arg.replace("”", '"').replace("“", '"').replace("Real Data", "RealData").split()
            arg = None
            for word in words:
                if word.startswith("/") or ":/" in word or '"/' in word or "'/" in word:
                    arg = word
                    break
        # If the argument is between quotes, take what is between the quotes
        if not arg:
            continue
        if "'/" in arg:
            arg = arg.split("'")[1]
        elif '"/' in arg:
            arg = arg.split('"')[1]
        elif noParse:
            # Consider the whole line is the argument
            pass
        else:
            # Take the first word
            arg = arg.strip().split()[0]
        # Escape any space left
        if arg:
            argList.append(arg.replace(" ", r"\ "))

    # Persitify items for later use
    if not last and argList:
        with open(lastFile, "wt") as tmpFile:
            tmpFile.write("\n".join(argList))

    for arg in reduceArgs(noMerge, argList):
        if arg:
            for command in commands:
                if "@arg@" in command:
                    cmd = command.replace("@arg@", arg, 1) if "dirac-loop" in command else command.replace("@arg@", arg)
                elif command[-1] in ('"', "'"):
                    cmd = command + arg.replace(r"\ ", " ") + command[-1]
                else:
                    cmd = command + " " + arg
                if not terse:
                    gLogger.notice("======= %s =========" % cmd)
                try:
                    output = subprocess.check_output(cmd.encode(), stderr=subprocess.STDOUT, shell=True).decode()
                    gLogger.notice(output[:-1] if terse else output)
                except subprocess.CalledProcessError as e:
                    gLogger.error("Error calling command, return code %d\n" % e.returncode, e.output)


if __name__ == "__main__":
    main()
