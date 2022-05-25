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
"""Utilities used by LHCb TS scripts."""
import six
from DIRAC import gLogger
from DIRAC.Core.Base.Script import Script
from LHCbDIRAC.TransformationSystem.Client.TransformationClient import TransformationClient


def _getTransformationID(transName):
    """Check that a transformation exists and return its ID or None if it doesn't
    exist.

    :param transName: name or ID of a transformation
    :type transName: int,long or string

    :return : transformation ID or None if it doesn't exist
    """
    testName = transName
    trClient = TransformationClient()
    # We can try out a long range of indices, as when the transformation is not found, it returns None
    for ind in range(1, 100):
        result = trClient.getTransformation(testName)
        if not result["OK"]:
            # Transformation doesn't exist
            break
        status = result["Value"]["Status"]
        # If the status is still compatible, accept
        if status in ("Active", "Idle", "New", "Stopped", "Completed"):
            return result["Value"]["TransformationID"]
        # If transformationID was given, return error
        if isinstance(transName, six.integer_types) or transName.isdigit():
            gLogger.error("Transformation in incorrect status", "%s, status %s" % (str(testName), status))
            return False
        # Transformation name given, try out adding an index
        testName = "%s-%d" % (transName, ind)
    return None


def getTransformations(args):
    """Parse the arguments of the script and generates a list of
    transformations."""
    transList = []
    if len(args):
        ids = args[0].split(",")
        try:
            for transID in ids:
                rr = transID.split(":")
                if len(rr) > 1:
                    for i in range(int(rr[0]), int(rr[1]) + 1):
                        tid = _getTransformationID(i)
                        if tid is not None:
                            transList.append(tid)
                else:
                    tid = _getTransformationID(rr[0])
                    if tid:
                        transList.append(tid)
                    elif tid is None:
                        gLogger.error("Transformation not found", rr[0])
        except Exception as e:
            gLogger.exception("Invalid transformation", lException=e)
            transList = []
    return transList
