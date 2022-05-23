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
"""Bookkeeping utilities."""
from DIRAC import gLogger, S_ERROR

from DIRAC.FrameworkSystem.Client.NotificationClient import NotificationClient


_IGNORE_PARAMETERS = ["ReplicaFlag", "Visible", "MethodName"]

# The following parameters can not used to build the query, it requires at least one more parameter.
_ONE = ["FileType", "ProcessingPass", "EventType", "DataQuality", "ConfigName", "ConfigVersion", "ConditionDescription"]

# Two parameter in the list not enough to build the query.
_TWO = ["ConfigName", "ConfigVersion", "ConditionDescription", "EventType", "ProcessingPass", "FileType", "DataQuality"]


def enoughParams(in_dict):
    """Dirty method to check the query parameters and make sure the queries have
    enough parameters."""
    checkingDict = in_dict.copy()
    if not checkingDict:
        return False

    for param in _IGNORE_PARAMETERS:
        if param in checkingDict:
            checkingDict.pop(param)

    if not checkingDict:
        return False

    if len(checkingDict) == 1:
        if not set(checkingDict) - set(_ONE):
            return False

    if len(checkingDict) == 2:
        if not set(checkingDict) - set(_TWO):
            return False
    return True


def checkEnoughBKArguments(func):
    """The decorator used to check the parameters of a given dictionary
    (BkQuery)."""

    def checkMethodArguments(self, *args, **kwargs):
        """This is used to check the conditions of a given query.

        We assume a dictionary can not be empty and it has more than one
        element, if we do not take into account the replica flag and the
        visibility flag
        """

        if args:
            arguments = args[0]
            if not enoughParams(arguments):
                if isinstance(func, staticmethod):
                    if hasattr(func, "__func__"):
                        funcName = func.__func__.func_name
                    else:
                        # we may do not know the type of the method
                        funcName = repr(func)
                else:
                    funcName = func.func_name

                res = self.getRemoteCredentials()
                userName = res.get("username", "UNKNOWN")
                address = self.email
                subject = "%s method!" % funcName
                body = (
                    "%s user has not provided enough input parameters! \n \
                the input parameters:%s "
                    % (userName, str(arguments))
                )
                NotificationClient().sendMail(address, subject, body, "lhcb-bookkeeping@cern.ch")
                gLogger.error("Got you: %s ---> %s" % (userName, str(arguments)))
                if self.forceExecution:  # we can force to execute the methods even the user does not
                    # provide enough parameter
                    result = func(self, *args)
                    return result
                else:
                    return S_ERROR("Provide more parameters %s" % str(arguments))  # TODO: use errno.EINVAL
            else:
                result = func(self, *args)
                return result
        else:
            result = func(self, *args)
            return result

    return checkMethodArguments
