###############################################################################
# (c) Copyright 2021 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
from DIRAC.RequestManagementSystem.Client.Request import Request
from DIRAC.RequestManagementSystem.Client.Operation import Operation
from DIRAC.RequestManagementSystem.Client.File import File

from DIRAC.TransformationSystem.Client.BodyPlugin.BaseBody import BaseBody


class DataChallengeReplicationBody(BaseBody):
    """
    This body is to be used for the Data challenge, and will be
    changed regularly

    * The file is originally in CERN-DAQ-EXPORT
    * We replicate it to CERN-DC-RAW (waiting for the file to be archived)
    * We then replicate to the chosen Tier 1 disk (DataChallenge shares).
    * We replicate it from the Tier1-disk to the Tier1-Tape
    * Finally, we remove the replica on the Tier1-Disk
    """

    # This is needed to know how to serialize the object
    _attrToSerialize = []

    @staticmethod
    def _createOperation(operationType, lfns, targetSE, sourceSE=None):
        """
        Generate an Operation object of the given Type, with the
        specified targetSE and sourceSE. Associate to it File objects
        from the lfns list

        :param str operationType: Type of the operation (RemoveReplica, ReplicateAndRegister, etc)
        :param list lfns: list of LFNs on which to perform the operation
        :param str targetSE: SE name(s) targeted by the ops
        :param str sourceSE: SE name of the source
        """
        newOp = Operation()
        newOp.Type = operationType
        newOp.TargetSE = targetSE
        if sourceSE:
            newOp.SourceSE = sourceSE
        for lfn in lfns:
            opFile = File()
            opFile.LFN = lfn
            newOp.addFile(opFile)
        return newOp

    def taskToRequest(self, taskID, task, transID):
        """
        Create the request object from the task Dict


        """

        if isinstance(task["InputData"], list):
            lfns = task["InputData"]
        elif isinstance(task["InputData"], str):
            lfns = task["InputData"].split(";")

        req = Request()

        # Replicate first to CERN-DC-RAW
        repCernRAW = self._createOperation("ReplicateAndRegister", lfns, "CERN-DC-RAW")
        req.addOperation(repCernRAW)

        # Now look at the target SEs
        # We expect one "Site-BUFFER" SE and one "Site-RAW" SE
        targetSEs = task["TargetSE"].split(",")

        # Order them to have the buffer first
        bufferSE, rawSE = sorted(targetSEs, key=lambda se: "-BUFFER" in se, reverse=True)

        # First replicate to disk
        repBuffer = self._createOperation("ReplicateAndRegister", lfns, bufferSE)
        req.addOperation(repBuffer)

        # Then replicate to tape from disk
        repTape = self._createOperation("ReplicateAndRegister", lfns, rawSE, sourceSE=bufferSE)
        req.addOperation(repTape)

        # Finally, remove the replicas from Tier1-Disk
        daqExportRemoval = self._createOperation("RemoveReplica", lfns, bufferSE)
        req.addOperation(daqExportRemoval)

        return req
