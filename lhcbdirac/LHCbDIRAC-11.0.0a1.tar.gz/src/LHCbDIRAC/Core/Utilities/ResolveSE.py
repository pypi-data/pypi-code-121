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
"""Resolve SE takes the workflow SE description and returns the list of
destination storage elements for uploading an output file."""
from random import shuffle

from DIRAC import gLogger, gConfig
from DIRAC.Core.Utilities.SiteSEMapping import getSEsForSite
from DIRAC.DataManagementSystem.Utilities.DMSHelpers import resolveSEGroup


def _setLocalFirst(seList, localSEs):
    """return a shuffled list of SEs from seList, localSEs being first."""
    local = [se for se in seList if se in localSEs]
    remote = [se for se in seList if se not in localSEs]
    shuffle(local)
    shuffle(remote)
    return local + remote


def getDestinationSEList(outputSE, site, outputmode="Any", run=None):
    """Evaluate the output SE list from a workflow and return the concrete list
    of SEs to upload output data."""
    if outputmode.lower() not in ("any", "local", "run"):
        raise RuntimeError("Unexpected outputmode")

    if outputmode.lower() == "run":
        gLogger.verbose("Output mode set to 'run', thus ignoring site parameter")
        if not run:
            raise RuntimeError("Expected runNumber")
        try:
            run = int(run)
        except ValueError as ve:
            raise RuntimeError("Expected runNumber as a number: %s" % ve)

        gLogger.debug("RunNumber = %d" % run)
        from LHCbDIRAC.TransformationSystem.Client.TransformationClient import TransformationClient

        runDestination = TransformationClient().getDestinationForRun(run)
        if not runDestination["OK"] or run not in runDestination["Value"]:
            raise RuntimeError(
                "Issue getting destinationForRun (%d): " % run + runDestination.get("Message", "unknown run")
            )
        site = runDestination["Value"][run]
        gLogger.verbose("Site set to %s for run %d" % (site, run))
        outputmode = "Local"

    # Add output SE defined in the job description
    gLogger.info("Resolving workflow output SE description: %s" % outputSE)

    # Check if the SE is defined explicitly for the site
    prefix = site.split(".")[0]
    country = site.split(".")[-1]
    # Concrete SE name
    result = gConfig.getOptions("/Resources/StorageElements/" + outputSE)
    if result["OK"]:
        gLogger.info("Found concrete SE %s" % outputSE)
        return [outputSE]

    # Get local SEs
    localSEs = getSEsForSite(site)
    if not localSEs["OK"]:
        raise RuntimeError(localSEs["Message"])
    localSEs = localSEs["Value"]
    gLogger.verbose("Local SE list is: %s" % (localSEs))

    # There is an alias defined for this Site
    associatedSEs = gConfig.getValue("/Resources/Sites/%s/%s/AssociatedSEs/%s" % (prefix, site, outputSE), [])
    if associatedSEs:
        associatedSEs = _setLocalFirst(associatedSEs, localSEs)
        gLogger.info("Found associated SE %s for site %s" % (associatedSEs, site))
        return associatedSEs

    groupSEs = resolveSEGroup(outputSE)
    if not groupSEs:
        raise RuntimeError("Failed to resolve SE " + outputSE)
    gLogger.verbose("Group SE list is: %s" % (groupSEs))

    # Find a local SE or an SE considered as local because the country is associated to it
    if outputmode.lower() == "local":
        # First, check if one SE in the group is local
        for se in localSEs:
            if se in groupSEs:
                gLogger.info("Found eligible local SE: %s" % (se))
                return [se]

        # Final check for country associated SE
        assignedCountry = country
        while True:
            # check if country is already one with associated SEs
            section = "/Resources/Countries/%s/AssociatedSEs/%s" % (assignedCountry, outputSE)
            associatedSEs = gConfig.getValue(section, [])
            if associatedSEs:
                associatedSEs = _setLocalFirst(associatedSEs, localSEs)
                gLogger.info("Found associated SEs %s in %s" % (associatedSEs, section))
                return associatedSEs

            gLogger.verbose("/Resources/Countries/%s/AssignedTo" % assignedCountry)
            opt = gConfig.getOption("/Resources/Countries/%s/AssignedTo" % assignedCountry)
            if opt["OK"] and opt["Value"]:
                assignedCountry = opt["Value"]
            else:
                # No associated SE and no assigned country, give up
                raise RuntimeError(
                    "Could not establish associated SE nor assigned country for country %s" % assignedCountry
                )

    # For collective Any and All modes return the whole group
    # Make sure that local SEs are passing first
    orderedSEs = _setLocalFirst(groupSEs, localSEs)
    gLogger.info("Found SEs, local first: %s" % orderedSEs)
    return orderedSEs
