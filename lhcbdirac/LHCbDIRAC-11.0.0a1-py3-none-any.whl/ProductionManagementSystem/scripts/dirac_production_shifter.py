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
"""dirac-production-shifter.

Script for the production shifter.

Print a summary of the requests in the system ( and their productions ).
The following switches and options are provided.

- requestState  : request state(s)
   [ Accepted, Active, BK Check, BK OK, Cancelled, Done, New, PPG OK, Rejected,
     Submitted, Tech OK ]
- requestType   : request type(s)
   [ Reconstruction, Simulation, Stripping, Stripping (Moore), Swimming, WGProduction ]
- requestID     : request ID(s)
- simCondition  : simulation condition(s) ( e.g. Beam4000GeV-VeloClosed-MagDown )
- proPath       : proPath(s) ( e.g. Reco13 )
- eventType     : eventType(s) ( e.g. 90000000 )
- sort          : sort requests using the keywords [RequestID,RequestState,RequestType,
                  SimCondition,ProPath,EventType]
- groupMerge    : group all merge productions in one line
- omitMerge     : omit all merge production
- noFiles       : do not request file information
"""

from datetime import datetime
import sys

from DIRAC import exit as DIRACExit
from DIRAC.Core.Base.Script import Script


def doParse():
    """Function that contains all the switches definition and isolates the rest
    of the module from parseCommandLine."""

    # Switch description
    Script.registerSwitch("i:", "requestID=", "ID of the request")
    Script.registerSwitch("r:", "requestState=", "request state(s)")
    Script.registerSwitch("t:", "requestType=", "request type(s)")
    Script.registerSwitch("m:", "simCondition=", "simulation condition(s)")
    Script.registerSwitch("p:", "proPath=", "proPath(s)")
    Script.registerSwitch("e:", "eventType=", "eventType(s)")
    Script.registerSwitch("z:", "sort=", "sort requests")
    Script.registerSwitch("g", "groupMerge", "group merge productions")
    Script.registerSwitch("x", "omitMerge", "omit all merge productions")
    Script.registerSwitch("n", "noFiles", "do not show file information")
    Script.registerSwitch("f", "hot", "shows hot production only")
    # Set script help message
    Script.setUsageMessage(
        __doc__
        + "\n".join(
            [
                "\nArguments:",
                "  requestID (string): csv ID(s) of the request, if used other switches are ignored",
                '  requestState (string): csv states, being "Active" by default',
                '  requestType (string): csv types, being "Stripping,Reconstruction" by default',
                "  simCondition (string): csv conditions, being None by default",
                "  proPath (string): csv paths, being None by default",
                "  eventType (string): csv events, being None by default",
                "  sortKey(string) : requests sort key [RequestID,RequestState,RequestType,\
                 SimCondition,ProPath,EventType]",
                "  groupMerge: group merge productions in one line",
                "  omitMerge: omit merge productions on summary",
                "  noFiles: do not report file status\n",
            ]
        )
    )

    # Get switches and options from command line
    Script.parseCommandLine()

    params = {
        "RequestID": None,
        "RequestState": "Active",
        "RequestType": "Stripping,Reconstruction",
        "SimCondition": None,
        "ProPath": None,
        "EventType": None,
    }

    mergeAction, noFiles, sortKey = None, False, "RequestID"

    for switch in Script.getUnprocessedSwitches():

        if switch[0].lower() in ("i", "requestid"):
            params["RequestID"] = switch[1]
        elif switch[0].lower() in ("r", "requeststate"):
            params["RequestState"] = switch[1]
        elif switch[0].lower() in ("t", "requesttype"):
            params["RequestType"] = switch[1]
        elif switch[0].lower() in ("m", "simcondition"):
            params["SimCondition"] = switch[1]
        elif switch[0].lower() in ("p", "propath"):
            params["ProPath"] = switch[1]
        elif switch[0].lower() in ("e", "eventtype"):
            params["EventType"] = switch[1]
        elif switch[0].lower() in ("z", "sort"):
            sortKey = switch[1]
        elif switch[0].lower() in ("g", "groupmerge"):
            mergeAction = "group"
        elif switch[0].lower() in ("x", "omitmerge"):
            mergeAction = "omit"
        elif switch[0].lower() in ("n", "nofiles"):
            noFiles = True
        elif switch[0].lower() in ("f", "hot"):
            mergeAction = "hot"
            params["RequestState"] = "Active,Idle"

    return params, mergeAction, noFiles, sortKey


def getRequests(parsedInput, sortKey):
    """Gets the requests from the database using the filters given by the
    user."""
    from LHCbDIRAC.ProductionManagementSystem.Client.ProductionRequestClient import ProductionRequestClient

    reqClient = ProductionRequestClient()

    for key, value in parsedInput.items():
        if value is None:
            del parsedInput[key]

    if "RequestID" in parsedInput:
        parsedInput = {"RequestID": parsedInput["RequestID"]}

    requests = reqClient.getProductionRequestList(0, "RequestID", "DESC", 0, 0, parsedInput)
    if not requests["OK"]:
        print(requests["Message"])
        return

    requests = requests["Value"]["Rows"]

    sortedRequests = sorted(requests, key=lambda k: k[sortKey])

    parsedRequests = []

    for request in sortedRequests:

        parsedRequests.append(
            {
                "requestID": request["RequestID"],
                "requestState": request["RequestState"],
                "requestName": request["RequestName"],
                "requestType": request["RequestType"],
                "proPath": request["ProPath"],
                "simCondition": request["SimCondition"],
                "eventType": request["EventType"],
            }
        )

    return parsedRequests


def getTransformations(transClient, requestID, noFiles):
    """Given a requestID, returns all its transformations."""
    transformations = transClient.getTransformations({"TransformationFamily": requestID})
    if not transformations["OK"]:
        print(transformations["Message"])
        return

    transformations = transformations["Value"]

    parsedTransformations = {}

    for transformation in transformations:

        transformationID = transformation["TransformationID"]

        if not noFiles:
            transformationFiles = getFiles(transClient, transformationID)
        else:
            transformationFiles = {}

        parsedTransformations[transformationID] = {
            "transformationStatus": transformation["Status"],
            "transformationType": transformation["Type"],
            "transformationFiles": transformationFiles,
        }

    return parsedTransformations


def getFiles(transClient, transformationID):
    """Given a transformationID, returns the status of their files."""
    from DIRAC.TransformationSystem.Client.TransformationClient import TransformationClient

    ts = TransformationClient()

    filesDict = {
        "Total": 0,
        "Processed": 0,
        "Running": 0,
        "Failed": 0,
        "Path": "Empty",
        "Hot": 0,
    }

    files = ts.getTransformationFilesSummaryWeb({"TransformationID": transformationID}, [], 0, 1000000)
    # This gets the interesting values
    recordsResult = ts.getTransformationSummaryWeb({"TransformationID": transformationID}, [], 0, 1000000)
    if not recordsResult["OK"]:
        print("TransID %s: %s" % (transformationID, recordsResult["Message"]))
        filesDict["Total"] = -1
        return filesDict
    records = recordsResult["Value"]
    parameters = records["ParameterNames"]
    moreValues = dict(zip(parameters, records["Records"][0]))
    path = ts.getTransformationParameters(transformationID, ["DetailedInfo"])

    if not path["OK"]:
        print("TransID %s: %s" % (transformationID, path["Message"]))
        filesDict["Total"] = -1
        return filesDict
    path = path["Value"]
    path = path.split("BK Browsing Paths:\n", 1)[1]

    if not files["OK"]:
        print("TransID %s: %s" % (transformationID, files["Message"]))
        filesDict["Total"] = -1
        return filesDict
    files = files["Value"]

    # This shows the interesting values
    filesDict["Total"] = files["TotalRecords"]
    filesDict["Running"] = moreValues["Jobs_Running"]
    filesDict["Failed"] = moreValues["Jobs_Failed"]
    filesDict["Done"] = moreValues["Jobs_Done"]
    filesDict["Waiting"] = moreValues["Jobs_Waiting"]
    filesDict["Files_Processed"] = moreValues["Files_Processed"]
    filesDict["Hot"] = moreValues["Hot"]
    filesDict["Path"] = path

    if filesDict["Total"]:
        filesDict.update(files["Extras"])

    return filesDict


def printSelection(parsedInput, mergeAction, noFiles, sortKey):
    """Prints header with selection parameters used to filter requests, plus some
    extra options to narrow summary."""

    if parsedInput["RequestID"] is not None:
        parsedInput = {"RequestID": parsedInput["RequestID"]}

    print("\n")
    print("-" * 60)
    print("                REQUESTS at %s" % datetime.now().replace(microsecond=0))
    print("-" * 60)

    print("  Selection parameters:")

    for key, value in parsedInput.items():
        print("    %s : %s" % (key.ljust(25, " "), value))

    print("  Display parameters:")
    print("    display merge transformations: %s" % ((1 and mergeAction) or "all"))
    print("    get files information        : %s" % (not noFiles))
    print("    sort key                     : %s" % (sortKey))

    print("-" * 60)
    print("\n")

    printNow()


def printResults(request, mergeAction):
    """Given a dictionary with requests, it prints the content on a human
    readable way.

    If mergeAction is given and different than None, it can omit all merge
    transformations from the summary or group all them together in one
    line if the value is group.
    """
    # infoTuple = (request['requestID'], request['requestState'], request['requestType'][:4],
    #             request['proPath'], request['simCondition'], request['eventType'])
    # infoTuple = (request['requestID'], request['requestState'])

    # print 'Req. No (%d) [%s][%s/%s][%s/%s]' % infoTuple
    # print '\tTransID\tStatus\t\tType\t\t\t\tCompleted\tTotal Files\t\tRunning\t\tFailed\t\tHot '

    groupedMerge = {
        "Merged": 0,
        "Total": 0,
        "Processed": 0,
        "Running": 0,
        "Failed": 0,
        "Path": "Empty",
        "Hot": 0,
        "Done": 0,
        "Waiting": 0,
        "Files_Processed": 0,
    }

    for transformationID, transformation in request["transformations"].items():
        filesMsg = ""

        filesDict = transformation["transformationFiles"]

        # Using switch noFiles
        if filesDict == {}:
            printTransformation(request["requestID"], transformationID, transformation, filesDict, True)
            continue

        if mergeAction == "omit" and transformation["transformationType"] in ["Merge", "MCMerge"]:
            continue

        if mergeAction == "group" and transformation["transformationType"] in ["Merge", "MCMerge"]:

            groupedMerge["Merged"] += 1
            if groupedMerge["Merged"] == 1:
                groupedMerge["Path"] = filesDict["Path"]
            elif groupedMerge["Path"] != filesDict["Path"]:
                groupedMerge["Path"] = "Multiple"

            if filesDict["Total"] > 0:

                groupedMerge["Processed"] += filesDict["Processed"]
                groupedMerge["Total"] += filesDict["Total"]
                groupedMerge["Running"] += filesDict["Running"]
                groupedMerge["Failed"] += filesDict["Failed"]
                groupedMerge["Hot"] += filesDict["Hot"]
                groupedMerge["Done"] += filesDict["Done"]
                groupedMerge["Waiting"] += filesDict["Waiting"]
                groupedMerge["Files_Processed"] += filesDict["Files_Processed"]

            continue

        # prints only the HOT production
        if mergeAction == "hot":
            if filesDict["Total"] > 0 and filesDict["Hot"] == 1:

                printTransformation(request["requestID"], transformationID, transformation, filesDict)

            continue

        printTransformation(request["requestID"], transformationID, transformation, filesDict)

    if mergeAction == "group" and groupedMerge["Merged"]:

        if groupedMerge["Merged"] > 1:
            groupMsg = "%s merge prod(s) grouped" % groupedMerge["Merged"]
            printTransformation(request["requestID"], None, None, groupedMerge, groupMsg=groupMsg)
        else:
            printTransformation(request["requestID"], transformationID, transformation, groupedMerge)

    printNow()


def printTransformation(requestID, transformationID, transformation, filesDict, noFiles=False, groupMsg=None):
    """Prints transformation information.

    :param requestID:
    :param transformationID:
    :param transformation: dict with keys transformationStatus and transformationType
    :param filesDict: dict with following keys: Processed, Total, Done, Running, Waiting, Failed, Hot
    :param noFiles: when set to True skips printout information about files
    :param groupMsg: when set to a string will replace transformationID,
      transformationType and transformationStatus in the printout. In this case
      transformationID and transformation can be set to None.
    """
    if not noFiles and filesDict["Path"] is not None:
        print("BK Browsing Path: [%s]" % filesDict["Path"])
    if noFiles:
        filesMsg = ""
    elif filesDict["Total"] == -1:
        filesMsg = "..Internal error.."
    elif filesDict["Total"] == 0:
        filesMsg = "..No files at all.."
    else:
        try:
            try:
                _processed = (float(filesDict["Processed"]) / float(filesDict["Total"])) * 100
            except ZeroDivisionError:
                _processed = 0
            if groupMsg is None:
                if filesDict["Hot"] == 1:
                    filesDict["Hot"] = "Hot"
                else:
                    filesDict["Hot"] = "No"
            filesMsg = "%.2f%%\t\t(%d)\t\t%d\t%d\t%d\t%d\t%s" % (
                _processed,
                filesDict["Total"],
                filesDict["Done"],
                filesDict["Running"],
                filesDict["Waiting"],
                filesDict["Failed"],
                filesDict["Hot"],
            )
        except KeyError:
            print("No files processed")
    if groupMsg is not None:
        msgTuple = (("%d\t%s\t\t" % (requestID, groupMsg)).ljust(40, " "), filesMsg)
    else:
        msgTuple = (
            (
                "%d\t%d\t%s\t%s"
                % (
                    requestID,
                    transformationID,
                    transformation["transformationStatus"].ljust(10, " "),
                    transformation["transformationType"],
                )
            ).ljust(40, " "),
            filesMsg,
        )
    print("%s\t%s" % msgTuple)


def printRequestsInfo(requests):
    """Prints the number of requests."""

    print(" found %s requests \n" % len(requests))
    printNow()


def printNow():
    """Flush stdout, otherwhise we have to wait until the end of the script to
    have if flushed."""

    sys.stdout.flush()


@Script()
def main():
    from DIRAC.TransformationSystem.Client.TransformationClient import TransformationClient

    # Main function. Parses command line, get requests, their transformations and
    # prints summary.

    # Get input from command line
    _parsedInput, _mergeAction, _noFiles, _sortKey = doParse()
    # if _mergeAction == 'hot':
    #   _sortkey = filesDict['Path']

    # Print summary header
    printSelection(_parsedInput, _mergeAction, _noFiles, _sortKey)

    # Get requests with given filters
    _requests = getRequests(_parsedInput, _sortKey)
    if _requests is None:
        DIRACExit(2)

    # Print small information
    printRequestsInfo(_requests)

    print(
        "ReqID\tTransID\tStatus\tType\t\t\t\tCompleted\tTotal Files\tDone\tRunning\tWaiting\tFailed\tHot\n", "=" * 150
    )

    # Initialized here to avoid multiple initializations due to the for-loop
    transformationClient = TransformationClient()

    # Print summary per request
    for _request in _requests:
        _requestID = _request["requestID"]

        _transformations = getTransformations(transformationClient, _requestID, _noFiles)
        _request["transformations"] = _transformations

        printResults(_request, _mergeAction)

    # And that's all folks.
    DIRACExit(0)


if __name__ == "__main__":
    main()
