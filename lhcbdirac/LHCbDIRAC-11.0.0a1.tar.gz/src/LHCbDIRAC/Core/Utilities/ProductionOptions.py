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
"""Production options is a utility to return options for projects based on
current LHCb software versions.

This is used by the production API to create production workflows but
also provides lists of options files for test jobs.
"""
import re
from DIRAC import S_OK, gLogger

gLogger = gLogger.getSubLogger("ProductionOptions")


def getModuleOptions(
    applicationName, numberOfEvents, inputDataOptions, extraOptions="", runNumber=0, firstEventNumber=1, jobType=""
):
    """Return the standard options for a Gaudi application project to be used at
    run time by the workflow modules.

    The input data options field is a python list (output of
    getInputDataOptions() below). The runNumber and firstEventNumber only
    apply in the Gauss case and when the job type is not 'user'.
    """
    optionsLines = []
    optionsLines.append("\n\n#////////////////////////////////////////////")
    optionsLines.append("# Dynamically generated options in a gaudirun job\n")
    if applicationName.lower() == "davinci" or applicationName.lower() == "lhcb":
        optionsLines.append("from Gaudi.Configuration import *")
    else:
        optionsLines.append("from %s.Configuration import *" % applicationName)

    if extraOptions:
        for opt in extraOptions.split(";"):
            if opt:
                optionsLines.append(opt)

    if inputDataOptions:
        optionsLines += inputDataOptions

    if applicationName.lower() == "gauss" and not jobType.lower() == "user":
        optionsLines.append('GaussGen = GenInit("GaussGen")')
        optionsLines.append("GaussGen.RunNumber = %s" % (runNumber))
        optionsLines.append("GaussGen.FirstEventNumber = %s" % (firstEventNumber))

    if numberOfEvents != 0:
        optionsLines.append("ApplicationMgr().EvtMax = %d" % (numberOfEvents))

    finalLines = "\n".join(optionsLines) + "\n"
    return S_OK(finalLines)


def getDataOptions(applicationName, inputDataList, inputDataType, poolXMLCatalogName):
    """Given a list of input data and a specified input data type this function
    will return the correctly formatted EventSelector options for Gaudi
    applications specified by name.

    The options are returned as a python list.
    """
    options = []
    if inputDataList:
        gLogger.info(
            "Formatting options for %s: %s LFN(s) of type %s" % (applicationName, len(inputDataList), inputDataType)
        )

        inputDataOpt = getEventSelectorInput(inputDataList, inputDataType)["Value"]
        evtSelOpt = """EventSelector().Input=[%s];\n""" % (inputDataOpt)
        options.append(evtSelOpt)

    poolOpt = """\nFileCatalog().Catalogs= ["xmlcatalog_file:%s"]\n""" % (poolXMLCatalogName)
    options.append(poolOpt)
    return S_OK(options)


def getEventSelectorInput(inputDataList, inputDataType):
    """Returns the correctly formatted event selector options for accessing input
    data using Gaudi applications."""
    inputDataFiles = []
    for lfn in inputDataList:
        lfn = lfn.replace("LFN:", "").replace("lfn:", "")
        if inputDataType == "MDF":
            inputDataFiles.append(""" "DATAFILE='LFN:%s' SVC='LHCb::MDFSelector'", """ % (lfn))
        elif inputDataType in ("ETC", "SETC", "FETC"):
            cmd = "COLLECTION='TagCreator/EventTuple' DATAFILE='LFN:%s' " % (lfn)
            cmd += "TYP='POOL_ROOT' SEL='(StrippingGlobal==1)' OPT='READ'"
            inputDataFiles.append(""" %s """ % cmd)
        elif inputDataType == "RDST":
            if re.search("rdst$", lfn):
                inputDataFiles.append(""" "DATAFILE='LFN:%s' TYP='POOL_ROOTTREE' OPT='READ'", """ % (lfn))
            else:
                gLogger.info("Ignoring file %s for step with input data type %s" % (lfn, inputDataType))
        else:
            inputDataFiles.append(""" "DATAFILE='LFN:%s' TYP='POOL_ROOTTREE' OPT='READ'", """ % (lfn))

    inputDataOpt = "\n".join(inputDataFiles)[:-2]
    return S_OK(inputDataOpt)
