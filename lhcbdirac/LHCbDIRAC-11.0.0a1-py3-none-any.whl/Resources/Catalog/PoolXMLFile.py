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
"""Interacts with pool xml catalog."""
from DIRAC.Resources.Catalog.PoolXMLCatalog import PoolXMLCatalog
from DIRAC.Resources.Catalog.PoolXMLFile import _getPoolCatalogs


def getOutputType(outputs, inputs, directory=""):
    """This function searches the directory for POOL XML catalog files and
    extracts the type of the pfn.

    If not found, inherits from the type of the inputs
    """

    if not isinstance(outputs, list):
        outputs = [outputs]

    catalog = PoolXMLCatalog(_getPoolCatalogs(directory))

    # inputs - by lfn
    generatedIn = False
    typeFileIn = []
    for fname in inputs:
        try:
            tFileIn = str(catalog.getTypeByPfn(str(list(catalog.getPfnsByLfn(fname)["Replicas"].values())[0])))
        except KeyError:
            tFileIn = None
        if not tFileIn:
            generatedIn = True
        else:
            typeFileIn.append(tFileIn)

    if generatedIn and inputs:
        raise ValueError("Could not find Type for inputs")

    # outputs - by pfn
    pfnTypesOut = {}
    for fname in outputs:
        tFileOut = str(catalog.getTypeByPfn(fname))
        if not tFileOut:
            if typeFileIn:
                tFileOut = typeFileIn[0]
            else:
                tFileOut = "ROOT"
        pfnTypesOut[fname] = tFileOut

    return pfnTypesOut
