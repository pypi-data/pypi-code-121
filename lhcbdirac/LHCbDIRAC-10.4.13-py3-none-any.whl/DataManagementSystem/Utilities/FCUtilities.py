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
"""This modules contains utility functions for LHCb DM."""
import os
import six
from DIRAC import S_OK, S_ERROR, gLogger
from DIRAC.Resources.Catalog.FileCatalogClient import FileCatalogClient


def chown(directories, user=None, group=None, mode=None, recursive=False, ndirs=None, fcClient=None):
    """This method may change the user, group or mode of a directory and apply it
    recursively if required."""
    if ndirs is None:
        ndirs = 0
    if not directories:
        return S_OK(ndirs)
    if isinstance(directories, six.string_types):
        directories = directories.split(",")
    if fcClient is None:
        fcClient = FileCatalogClient()
    timeout = 3600 if recursive else 10 * len(directories)
    if user is not None:
        res = fcClient.changePathOwner(dict.fromkeys(directories, user), recursive=recursive, timeout=timeout)
        if not res["OK"]:
            res["Action"] = "changePathOwner"
            return res
    if group is not None:
        res = fcClient.changePathGroup(dict.fromkeys(directories, group), recursive=recursive, timeout=timeout)
        if not res["OK"]:
            res["Action"] = "changePathGroup"
            return res
    if mode is not None:
        res = fcClient.changePathMode(dict.fromkeys(directories, mode), recursive=recursive, timeout=timeout)
        if not res["OK"]:
            res["Action"] = "changePathMode"
            return res

    ndirs += len(directories)
    return S_OK(ndirs)


def createUserDirectory(user):
    """This functions creates (if not existing) a user directory in the DFC."""
    dfc = FileCatalogClient()
    initial = user[0]
    baseDir = os.path.join("/lhcb", "user", initial, user)
    if dfc.isDirectory(baseDir).get("Value", {}).get("Successful", {}).get(baseDir):
        return S_ERROR("User directory already existing")
    gLogger.info("Creating directory", baseDir)
    res = dfc.createDirectory(baseDir)
    if not res["OK"]:
        return res
    gLogger.info("Setting ownership of directory", baseDir)
    return chown(baseDir, user, group="lhcb_user", mode=0o755, recursive=False, fcClient=dfc)
