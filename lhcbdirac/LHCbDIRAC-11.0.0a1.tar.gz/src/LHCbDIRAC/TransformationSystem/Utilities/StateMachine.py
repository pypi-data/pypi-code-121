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
"""Transformation Files state machine (LHCb specific)"""
from DIRAC.ResourceStatusSystem.PolicySystem.StateMachine import State
from LHCbDIRAC.ProductionManagementSystem.Utilities.StateMachine import LHCbStateMachine


class TransformationFilesStateMachine(LHCbStateMachine):
    """Implementation of the state machine for the TransformationFiles."""

    def __init__(self, state):
        """c'tor Defines the state machine transactions."""

        super(TransformationFilesStateMachine, self).__init__(state)

        self.states = {
            "Unused-inherited": State(
                13, ["Unused", "Processed-inherited", "MaxReset-inherited"], defState="Unused-inherited"
            ),
            "Assigned-inherited": State(
                12, ["Unused", "Processed-inherited", "MaxReset-inherited"], defState="Assigned-inherited"
            ),
            "MaxReset-inherited": State(11, ["Unused"], defState="MaxReset-inherited"),
            "Processed-inherited": State(10),  # final state
            "Moved": State(9),  # final state
            "Removed": State(8),  # final state
            "MissingInFC": State(7),  # final state
            "NotProcessed": State(6, ["Unused"], defState="NotProcessed"),
            "ProbInFC": State(5),  # final state
            "MaxReset": State(4, ["Removed", "Moved", "Problematic"], defState="MaxReset"),
            "Problematic": State(3, ["Removed", "Unused"], defState="Problematic"),
            "Processed": State(2),  # final state
            "Assigned": State(1, ["Unused", "Processed", "MaxReset", "Problematic"], defState="Assigned"),
            "Unused": State(
                0,
                ["Assigned", "MissingInFC", "ProbInFC", "Problematic", "Removed", "NotProcessed", "Processed", "Moved"],
                defState="Unused",
            ),
        }
