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
"""Reads .log-files and outputs summary of counters as a .json-file and a
.html-file."""
import os
import json

from distutils.version import LooseVersion  # pylint:disable=import-error,no-name-in-module

from DIRAC import gLogger, S_OK, S_ERROR


def readLogFile(logFile, project, version, appConfigVersion, jobID, prodID, wmsID, name="errors.json"):
    """The script that runs everything.

    :param str logFile: the name of the logfile
    :param str project: the project string of the file
    :param str version: the versio of the project
    :param str jobID: the JobID
    :param str prodID: the production ID
    :param str wmsID: the wmsID
    :param str name: the name of the output json file, standardised to 'errors.json'
    """
    logString = ""
    fullPathFileName = pickStringFile(project, version, appConfigVersion)
    dictTotal = []
    dictG4Errors = dict()
    dictG4ErrorsCount = dict()

    if fullPathFileName is None or not os.path.exists(fullPathFileName) or os.stat(fullPathFileName)[6] == 0:
        gLogger.warn("STRINGFILE %s is empty" % fullPathFileName)

    readErrorDict(fullPathFileName, dictG4Errors)

    res = getLogString(logFile, logString)
    if not res["OK"]:
        gLogger.warn("Problems in reading %s" % logFile)
        return res
    logString = res["Value"]

    reversedKeys = sorted(dictG4Errors, reverse=True)

    for errorString in reversedKeys:
        dictCountDumpErrorString = dict()
        dictTemp = dict()
        ctest = logString.count(errorString)
        test = logString.find(errorString)
        array = []
        for i in range(ctest):
            start = test
            test = logString.find(errorString, start)
            alreadyFound = False
            for error in reversedKeys:
                if error == errorString:
                    break
                checke = logString[test : test + 100].find(error)
                if checke != -1:
                    alreadyFound = True
                    test = test + len(error)
                    break
            if alreadyFound:
                continue

            if test != -1:
                eventnr = ""
                runnr = ""

                eventnr_point = logString.rfind("INFO Evt", test - 5000, test)
                if eventnr_point != -1:
                    eventnr = "Evt " + logString[eventnr_point:test].split("INFO Evt")[1].strip().split(",")[0]
                    runnr = logString[eventnr_point:].split("INFO Evt")[1].strip().split(",")[1]

                if errorString.find("G4") != -1:
                    check = logString[test : test + 250].find("***")
                    if check != -1:
                        errorBase = logString[test : test + 250].split("***")[0]
                        dictCountDumpErrorString[i] = eventnr + "  " + runnr + "  -->" + errorBase

                        array.append(dict())
                        array[-1]["eventnr"] = eventnr
                        array[-1]["runnr"] = runnr

                        lengthDump = len(errorBase)
                        test = test + lengthDump
                else:
                    errorBase = logString[test : test + 250].split("\n")[0]
                    dictCountDumpErrorString[i] = eventnr + "  " + runnr + "  -->" + errorBase

                    array.append(dict())
                    array[-1]["eventnr"] = eventnr
                    array[-1]["runnr"] = runnr

                    lengthDump = len(errorBase)
                    test = test + lengthDump

                if array[-1] is not None:
                    dictTemp[errorString] = dict()
                    dictTemp[errorString] = array

        if dictTemp != {}:
            dictTotal.append(dictTemp)
        dictG4ErrorsCount[errorString] = dictCountDumpErrorString

    createJSONtable(dictTotal, name, jobID, prodID, wmsID)
    createHTMLtable(dictG4ErrorsCount, "errors.html")

    return S_OK()


################################################

#   # Due to issues in the mapping of the ES DB, this mapping
#   (which is more clear than the one below) couldn't be used.
#   # I have still saved the function here.

# def createJSONtable(dictTotal, name):

#   ids = {}
#   ids['JobID'] = JOB_ID
#   ids['ProductionID'] = PROD_ID
#   ids['TransformationID'] = TRANS_ID

#   errors = []

#   with open(name, 'w') as output:
#     for error in dictTotal:
#       newrow = {}
#       for key, value in error.items():
#         newrow['Error type'] = key
#         newrow['Counter'] = len(value)
#         newrow['Events'] = value
#       errors.append(newrow)

#     errorDict = {'Errors' : errors}

#     result = {}
#     result['ID'] = ids
#     result['Errors'] = errors
#     result = {'Log_output' : result}

#     output.write(json.dumps(result, indent = 2))
#   return

# \


def createJSONtable(dictTotal, name, jobID, prodID, wmsID):
    """Creates a JSON file out of the collection of errors listed in dictTotal.

    :param dict dictTotal: the dictionary of errors
    :param str name: the name of the JSON file
    :param str jobID: the JobID of the log
    :param str prodID: the ProductionID of the log
    :param str wmsID: the wmsID of the log
    """
    result = {}
    result["JobID"] = jobID
    result["ProductionID"] = prodID
    result["wmsID"] = wmsID

    with open(name, "w") as output:
        for error in dictTotal:
            for key, value in error.items():
                result[key] = len(value)
        json.dump(result, output, indent=2)


#####################################################


def createHTMLtable(dictG4ErrorsCount, name):
    """Creates an HTML file out of the collection of errors listed in
    dictG4ErrorsCount.

    :param dict dictG4ErrorsCount: the dictionary of errors
    :param str name: the name of the HTML file
    """
    with open(name, "w") as f:
        f.write("<HTML>\n")

        f.write("<table border=1 bordercolor=#000000 width=100% bgcolor=#BCCDFE>")
        f.write("<tr>")
        f.write("<td>ERROR TYPE</td>")
        f.write("<td>COUNTER</td>")
        f.write("<td>DUMP OF ERROR MESSAGES</td>")
        f.write("</tr>")

        orderedKeys = sorted(dictG4ErrorsCount)
        for errString in orderedKeys:
            if dictG4ErrorsCount[errString] != {}:
                f.write("<tr>")
                f.write("<td>" + errString + "</td>")
                f.write("<td>" + str(len(dictG4ErrorsCount[errString])) + "</td>")
                f.write("<td>")
                f.write("<lu>")
                for y in dictG4ErrorsCount[errString]:
                    f.write("<li>")
                    f.write(" " + dictG4ErrorsCount[errString][y] + " ")
                f.write("</lu>")
                f.write("</td>")
                f.write("</tr>")

        f.write("</table>")


#######################################################


def readErrorDict(fullPathFileName, dictName):
    """Reads errors in a stringfile and puts them in dictName.

    :param str fullPathFileName: the name of the stringfile
    :param dict dictName: the name of the dict that will insert the data in fullPathFileName
    """
    fileLines = getLines(fullPathFileName)
    for line in fileLines:
        errorString = line.split(",")[0]
        description = line.split(",")[1]
        dictName[errorString] = description


################################################


def getLines(fullPathFileName):
    """Reads lines in string file.

    :param str fullPathFileName: the name of the file to be opened and read
    """

    gLogger.notice(">>> Processed STRINGFILE -> ", fullPathFileName)
    with open(fullPathFileName, "r") as f:
        lines = f.readlines()
    return lines


################################################


def getLogString(logFile, logString):
    """Checks if the log file can be opened, and saves the text in logFile into
    logString.

    :param str logFile: the name of the logFile
    :param str logStr: the name of the variable that will save the contents of logFile
    """

    gLogger.notice("Attempting to open %s" % logFile)
    if not os.path.exists(logFile):
        gLogger.error("%s could not be found" % logFile)
        return S_ERROR()
    if os.stat(logFile)[6] == 0:
        gLogger.error("%s is empty" % logFile)
        return S_ERROR()
    with open(logFile, "r") as f:
        logString = f.read()
    gLogger.notice("Successfully read %s" % logFile)
    return S_OK(logString)


################################################


def pickStringFile(project, version, appConfigVersion):
    """Picks the string file from the current directory.

    :param str project: the project name
    :param str version: the version of the project
    :param str version: APPCONFIG version
    """

    if os.environ.get("VO_LHCB_SW_DIR"):
        sharedArea = os.environ["VO_LHCB_SW_DIR"]

        # sometimes this is wrong... so trying to correct it!
        if "lhcb" not in os.listdir(sharedArea):
            sharedArea = os.path.join(sharedArea, "lib")
            if "lhcb" not in os.listdir(sharedArea):
                gLogger.error("Current sharedArea (%s) content: " % sharedArea, os.listdir(sharedArea))
                raise RuntimeError("Can't find a sharedArea")

    else:
        sharedArea = "/cvmfs/lhcb.cern.ch/lib"

    sourceDir = os.path.join(sharedArea, "lhcb", "DBASE", "AppConfig", appConfigVersion, "errstrings")
    fileName = project + "_" + version + "_errs.txt"
    fullPathFileName = os.path.join(sourceDir, os.path.basename(fileName))
    if not os.path.exists(fullPathFileName):
        gLogger.notice("string file %s does not exist, attempting to take the most recent file ..." % fullPathFileName)
        fileList = [fn for fn in os.listdir(sourceDir) if project in fn]
        if fileList:
            versionsList = [x.replace(project + "_", "").replace("_errs.txt", "") for x in fileList]
            mostRecentVersion = sorted(versionsList, key=LooseVersion)[-1]
            fileName = project + "_" + mostRecentVersion + "_errs.txt"
            fullPathFileName = os.path.join(sourceDir, os.path.basename(fileName))
        else:
            gLogger.warn("WARNING: no string files for this project")
            return None

    return fullPathFileName


# This is a relic from the previous version of the file, I'll keep it for the while

# global LOG_STRING
# global STRING_FILE
# global FILE_OK

# LOG_FILE = sys.argv[1]
# PROJECT = sys.argv[2]
# VERSION = sys.argv[3]

# global JOB_ID
# global PROD_ID
# global TRANS_ID

# JOB_ID = sys.argv[4]
# PROD_ID = sys.argv[5]
# TRANS_ID = sys.argv[6]

# #LOG_STRING = ''
# #FILE_OK = ''
# dictG4Errors = dict()
# dictG4ErrorsCount = dict()
# STRING_FILE = pickStringFile(PROJECT, VERSION)

# if STRING_FILE is not None:
#   if os.stat(STRING_FILE)[6] != 0:
#     main(LOG_FILE)
#   else:
#     print 'WARNING: STRINGFILE %s is empty' % STRING_FILE

# The file is run as follows:
# readLogFile('Example.log', 'project', 'version', 'jobID', 'prodID', 'wmsID')
