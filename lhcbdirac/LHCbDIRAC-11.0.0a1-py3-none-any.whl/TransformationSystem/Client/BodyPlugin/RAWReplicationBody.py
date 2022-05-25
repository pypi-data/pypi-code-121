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


class RAWReplicationBody(BaseBody):
    """
    This body is to be used for the RAW replication of the full stream:

    * The file is originally in CERN-DAQ-EXPORT
    * We replicate it to CERN-RAW (waiting for the file to be archived)
    * We send the removal signal to the online
    * We then replicate to the chosen Tier 1 buffer (CPUforRAW shares).
    * If the chosen tape (RAW shares) is on the same site as the buffer
      (80% of the time), we replicate it from the buffer.
      Otherwise we can do it in parallel, from CERN-DAQ-EXPORT
    * Finally, we remove the replicas
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
            lfns = task["InputData"].split(",")

        req = Request()

        # Replicate first to CERN-RAW
        repCernRAW = self._createOperation("ReplicateAndRegister", lfns, "CERN-RAW")
        req.addOperation(repCernRAW)

        # Remove from Online
        onlineRemoval = self._createOperation("PhysicalRemoval", lfns, "OnlineRunDB")
        req.addOperation(onlineRemoval)

        # Now look at the target SEs
        # We expect one "Site-BUFFER" SE and one "Site-RAW" SE
        targetSEs = task["TargetSE"].split(";")

        # If we have two targetSEs
        # (we should always so far, maybe not for turbo)
        if len(targetSEs) == 2:
            # Order them to have the buffer first
            bufferSE, rawSE = sorted(targetSEs, key=lambda se: "-BUFFER" in se, reverse=True)

            # Here, we can just rely on naming convention, and the fact
            # that the site always appears first in the SE names

            diskAndTapeSameSite = bufferSE.split("-")[0] == rawSE.split("-")[0]

            # If the buffer and raw SEs are on the same site,
            # do the transfer in two steps to maximise LAN transfer
            # over WAN
            if diskAndTapeSameSite:

                # First replicate to disk
                repBuffer = self._createOperation("ReplicateAndRegister", lfns, bufferSE)
                req.addOperation(repBuffer)

                # Then replicate to tape from disk
                repTape = self._createOperation("ReplicateAndRegister", lfns, rawSE, sourceSE=bufferSE)
                req.addOperation(repTape)

            # Otherwise, do both replication from EOS
            else:
                # One operation for both replication
                repBufferAndTape = self._createOperation("ReplicateAndRegister", lfns, task["TargetSE"])
                req.addOperation(repBufferAndTape)

        # If there is only one SE (like for the Turbo stream?) or more than 2 (?!)
        # do only one operation
        else:
            repBufferAndTape = self._createOperation("ReplicateAndRegister", lfns, task["TargetSE"])
            req.addOperation(repBufferAndTape)

        # Finally, remove the replicas from CERN-DAQ-EXPORT
        daqExportRemoval = self._createOperation("RemoveReplica", lfns, "CERN-DAQ-EXPORT")
        req.addOperation(daqExportRemoval)

        return req
