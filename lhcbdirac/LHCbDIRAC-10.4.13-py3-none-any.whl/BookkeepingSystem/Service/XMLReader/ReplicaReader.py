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
"""It stores the replica."""
from LHCbDIRAC.BookkeepingSystem.Service.XMLReader.Replica.Replica import Replica
from LHCbDIRAC.BookkeepingSystem.Service.XMLReader.Replica.ReplicaParam import ReplicaParam
from DIRAC import gLogger


class ReplicaReader(object):
    @staticmethod
    def readReplica(doc, filename):
        """reads the replica information."""
        gLogger.debug("Reading Replica from" + str(filename))
        replica = Replica()
        replica.name = filename  # full path

        replicaElements = doc.getElementsByTagName("Replica")

        for node in replicaElements:
            param = ReplicaParam()

            outputfile = node.getAttributeNode("File")
            if outputfile:
                param.file = outputfile.value
            else:
                gLogger.warn("Missing the <file> tag in replica xml file")

            name = node.getAttributeNode("Name")
            if name:
                param.name = name.value
            else:
                gLogger.warn("Missing the <name> tag in replica xml file")

            location = node.getAttributeNode("Location")
            if location:
                param.location = location.value
            else:
                gLogger.warn("Missing the <location> tag in replica xml file")

            se = node.getAttributeNode("SE")
            if se:
                param.se = se.value
            else:
                gLogger.warn("Missing the <SE> tag in replica xml file")

            action = node.getAttributeNode("Action")
            if action:
                param.action = action.value
            else:
                gLogger.warn("Missing the <Action> tag in replica xml file")

            replica.addParam(param)
            gLogger.info("Replica Reading finished successfully")

        return replica
