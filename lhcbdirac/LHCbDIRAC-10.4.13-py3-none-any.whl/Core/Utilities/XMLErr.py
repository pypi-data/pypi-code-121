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
"""Takes an xmlSummary along with its IDs and creates a JSON file containing
all the counters in the xmlSummary."""
import json
import xml.etree.ElementTree as ET
from DIRAC import gLogger, S_ERROR, S_OK


def readXMLfile(xmlFile, jobID, prodID, wmsID, jsonFileName="errors_xmlSummary.json"):
    """The main execution function.

    :param str xmlFile: the name of the XML file
    :param str jobID: the job ID of the data
    :param str prodID: the production ID of the data
    :param str wmsID: the wms ID of the data
    """
    res = extractRoot(xmlFile)
    if not res["OK"]:
        return res
    root = res["Value"]
    res = extractData(root, jobID, prodID, wmsID)
    if not res["OK"]:
        return res
    jsonData = res["Value"]
    gLogger.notice("Attempting to read %s and put save it as %s" % (xmlFile, jsonFileName))
    createJSONfile(jsonData, jsonFileName)
    return S_OK()


##############################################


def extractRoot(xmlFile):
    """Takes the root element in the XML file.

    :param str xmlFile: the name of the XML file
    """
    try:
        gLogger.notice("Extracting the tree from the XML file %s" % xmlFile)
        tree = ET.parse(xmlFile)
    except Exception as inst:
        gLogger.error("ERROR: Cannot extract tree from XML file %s" % xmlFile)
        return S_ERROR(inst)
    return S_OK(tree.getroot())


##############################################


def extractData(root, jobID, prodID, wmsID):
    """Takes the root of the XML file and the ids of the job, and converts the
    json file from the XML file.

    :param str jobID: the job ID
    :param str prodID: the production ID
    :param str wmsID: the wms ID
    """
    gLogger.notice("Extracting data from the root of the XML file")
    idDict = {}
    idDict["JobID"] = jobID
    idDict["ProductionID"] = prodID
    idDict["wmsID"] = wmsID

    tempDict = {}
    result = {}

    if root.iter("counter") is None:
        return S_ERROR("ERROR: No counters in XML file!")
    for counter in root.iter("counter"):
        try:
            counterValue = int(counter.text)
        except ValueError as inst:
            return S_ERROR(str(inst))
        tempDict[counter.attrib["name"]] = counterValue

    # Checks if dict is empty (empty dicts evaluate to False)
    if not tempDict:
        gLogger.warn("WARNING: XML file is empty")

    result["Counters"] = tempDict
    result["Counters"]["ID"] = idDict
    return S_OK(json.dumps(result, indent=2))


##############################################


def createJSONfile(jsonData, jsonFileName):
    """Creates a JSON file given a string containing the data.

    :param str jsonData: the string that contains the data
    :param str jsonFileName: the name of the resulting JSON file
    """
    with open(jsonFileName, "w") as f:
        gLogger.notice("Writing the XML file to JSON file %s" % jsonFileName)
        f.write(jsonData)


# The file is run as following:
# readXMLfile(xmlFileName.xml, jobID, prodID, wmsID, jsonFileName.json)
