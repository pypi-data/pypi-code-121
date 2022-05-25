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
"""Utilities to parse the XML Generator Logs."""
import io
import ast
import json
import six
import xmltodict


def counterJson(listCounters):
    """returns a dictionary containing counters
    :param list listCounters: list containing all the counter nodes
    """
    dictCounters = dict()
    if isinstance(listCounters, dict):
        listCounters = [listCounters]
    for counter in listCounters:
        dictCounters[counter["@name"]] = int(counter["value"])
    return dictCounters


def efficiencyJson(listEfficiencies):
    """returns a dictionary containing efficiencies
    :param list listEfficiencies: list containing all the efficiency nodes
    """
    dictEfficiencies = dict()
    if isinstance(listEfficiencies, dict):
        listEfficiencies = [listEfficiencies]
    for efficiency in listEfficiencies:
        dictEfficiencies[efficiency["@name"]] = {
            "after": int(efficiency["after"]),
            "before": int(efficiency["before"]),
            "error": float(efficiency["error"]),
            "value": float(efficiency["value"]),
        }
    return dictEfficiencies


def fractionJson(listFractions):
    """returns a dictionary containing fractions
    :param list listFractions: list containing all the fraction nodes
    """
    dictFractions = dict()
    if isinstance(listFractions, dict):
        listFractions = [listFractions]
    for fraction in listFractions:
        dictFractions[fraction["@name"]] = {
            "number": int(fraction["number"]),
            "error": float(fraction["error"]),
            "value": float(fraction["value"]),
        }
    return dictFractions


def crossSectionJson(listCrossSections):
    """returns a dictionary containing cross sections
    :param list listCrossSections: list containing all the cross section nodes
    """
    dictCrossSections = dict()
    if isinstance(listCrossSections, dict):
        listCrossSections = [listCrossSections]
    for crossSection in listCrossSections:
        dictCrossSections[crossSection["description"][1:-1]] = {
            "ID": int(crossSection["@id"]),
            "generated": int(crossSection["generated"]),
            "value": float(crossSection["value"]),
        }
    return dictCrossSections


def methodGeneratorJson(listMethods, listGenerators, numberEventTypes):
    """returns a dictionary containing the generator for each method
    :param list listMethods: list containing all the methods
    :param list listGenerators: list containing all the generators
    :param int numberEventTypes: number of event types in the generator log
    """
    dictMethods = dict()
    if numberEventTypes > 1:
        for i, method in enumerate(listMethods):
            dictMethods[method] = listGenerators[i]
    else:
        dictMethods[listMethods] = listGenerators
    return dictMethods


class GeneratorLog(object):
    def __init__(self):
        pass

    def generatorLogJson(self, fileName):
        """converts the xml Generator Log into json format"""
        dictElements = dict()
        dictGenerator = dict()

        with io.open("GeneratorLog.xml", "r") as fp:
            fileLines = fp.readlines()

        fileLines = fileLines[fileLines.index("<generatorCounters>\n") : fileLines.index("</generatorCounters>\n") + 1]
        xmlText = "".join(fileLines)
        numberEventTypes = xmlText.count("<eventType>")
        if numberEventTypes > 1:
            # Taking the first set of nodes
            xmlText = (
                xmlText.split("<eventType>")[0]
                + "<eventType>"
                + xmlText.split("<eventType>")[1]
                + "<method>"
                + xmlText.split("<eventType>")[-1].split("<method>", 1)[-1]
            )  # noqa
        xmlText = xmlText.replace("-nan", "-1")
        dicto = xmltodict.parse(xmlText)
        jsonData = ast.literal_eval(json.dumps(dicto))

        listCounters = jsonData["generatorCounters"].get("counter", [])
        listEfficiencies = jsonData["generatorCounters"].get("efficiency", [])
        listFractions = jsonData["generatorCounters"].get("fraction", [])
        listCrossSections = jsonData["generatorCounters"].get("crosssection", [])
        listMethods = jsonData["generatorCounters"]["method"]
        listGenerators = jsonData["generatorCounters"]["generator"]

        dictElements["counter"] = counterJson(listCounters)
        dictElements["efficiency"] = efficiencyJson(listEfficiencies)
        dictElements["fraction"] = fractionJson(listFractions)
        dictElements["crossSection"] = crossSectionJson(listCrossSections)
        dictElements["method"] = methodGeneratorJson(listMethods, listGenerators, numberEventTypes)

        dictGenerator["generatorCounters"] = dictElements

        with io.open(fileName, "w", encoding="utf-8") as fp:
            fp.write(six.text_type(json.dumps(dictGenerator, indent=2)))

        return dictGenerator
