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
"""
    This module implements the default behavior for the FTS3Agent for TPC and source SE selection
"""
import random
import itertools
import re
from DIRAC import S_OK, S_ERROR
from DIRAC.DataManagementSystem.Utilities.DMSHelpers import DMSHelpers
from DIRAC.DataManagementSystem.private.FTS3Plugins.DefaultFTS3Plugin import DefaultFTS3Plugin
from DIRAC.Resources.Storage.StorageElement import StorageElement


class LHCbFTS3Plugin(DefaultFTS3Plugin):
    @staticmethod
    def _isCERNEOSCTATransfer(ftsJob=None, sourceSEName=None, destSEName=None, **kwargs):
        """Check if the transfer involves both CERN EOS and CTA"""
        try:
            if not sourceSEName:
                sourceSEName = ftsJob.sourceSE
            if not destSEName:
                destSEName = ftsJob.targetSE

            srcSE = StorageElement(sourceSEName)
            srcBaseSEName = srcSE.options.get("BaseSE")
            dstSE = StorageElement(destSEName)
            dstBaseSEName = dstSE.options.get("BaseSE")

            if (srcBaseSEName, dstBaseSEName) in list(
                itertools.product(("CERN-EOS", "CERN-CTA", "CERN-CTA-DATACHALLENGE"), repeat=2)
            ):
                return True

        except Exception:
            pass

        return False

    def selectTPCProtocols(self, ftsJob=None, sourceSEName=None, destSEName=None, **kwargs):
        """Specialised TPC selection"""

        # If the transfer involves both CERN EOS and CTA, return root as TPC
        if self._isCERNEOSCTATransfer(ftsJob=ftsJob, sourceSEName=sourceSEName, destSEName=destSEName, **kwargs):
            return ["root"]

        return super(LHCbFTS3Plugin, self).selectTPCProtocols(
            ftsJob=ftsJob, sourceSEName=sourceSEName, destSEName=destSEName, **kwargs
        )

    def selectSourceSE(self, ftsFile, replicaDict, allowedSources):
        """
        This is basically a copy/paste of the parent method, with the exception
        of prefering local staging.
        """

        allowedSourcesSet = set(allowedSources) if allowedSources else set()

        # If we have a restriction, apply it, otherwise take all the replicas
        allowedReplicaSource = (set(replicaDict) & allowedSourcesSet) if allowedSourcesSet else replicaDict

        # If we have a replica at the same site as the destination
        # use that one
        # This is mostly done in order to favor local staging
        #
        # We go with the naive assumption that the site name
        # is always the first part of the SE name, separated
        # by either a - or a _ (like `_MC-DST`)
        # (I know there are "proper tools" for checking if a SE is on the same site
        # but since we are in the sheltered LHCb only environment, I can do that
        # sort of optimization)
        targetSite = re.split("-|_", ftsFile.targetSE)[0]
        sameSiteSE = [srcSE for srcSE in allowedReplicaSource if targetSite in srcSE]
        if sameSiteSE:
            allowedReplicaSource = sameSiteSE

        randSource = random.choice(list(allowedReplicaSource))  # one has to convert to list
        return randSource

    def inferFTSActivity(self, ftsOperation, rmsRequest, rmsOperation):
        """
        Tries to infer the FTS Activity
        """

        ### Data Challenge activity
        # All the tests with data challenges are done
        # on SE with '-DC-' in their name
        targetSEs = rmsOperation.targetSEList
        if any("-DC-" in se for se in targetSEs):
            return "Data Challenge"

        return super(LHCbFTS3Plugin, self).inferFTSActivity(ftsOperation, rmsRequest, rmsOperation)
