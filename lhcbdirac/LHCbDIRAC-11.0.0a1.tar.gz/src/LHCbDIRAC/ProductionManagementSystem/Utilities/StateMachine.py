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
"""A module defining the state machine for the Productions."""
from DIRAC import S_OK, S_ERROR, gLogger
from DIRAC.ResourceStatusSystem.PolicySystem.StateMachine import State, StateMachine


class LHCbStateMachine(StateMachine):
    """Just redefining one method."""

    def setState(self, candidateState):
        """Makes sure the state is either None or known to the machine, and that it
        is a valid state to move into.

        Final states are also checked. This is a re-definition of original
        one that wasn't making these checks
        """

        if candidateState == self.state:
            return S_OK(candidateState)

        if candidateState is None:
            self.state = candidateState
        elif candidateState in self.states:
            if not self.states[self.state].stateMap:
                gLogger.warn("Final state, won't move")
                return S_OK(self.state)
            if candidateState not in self.states[self.state].stateMap:
                gLogger.warn("Can't move from %s to %s, choosing a good one" % (self.state, candidateState))
            nextState = self.getNextState(candidateState)
            if not nextState["OK"]:
                return nextState
            nextState = nextState["Value"]
            # If the StateMachine does not accept the candidate, return error message
            self.state = nextState
        else:
            return S_ERROR("%s is not a valid state" % candidateState)

        return S_OK(nextState)


class ProductionsStateMachine(LHCbStateMachine):
    """PMS (Production Management System, not what google thinks!) implementation
    of the state machine."""

    def __init__(self, state):
        """c'tor Defines the state machine transactions."""

        super(ProductionsStateMachine, self).__init__(state)

        # Current states
        self.states = {
            "Cleaned": State(15),  # final state
            "Cleaning": State(14, ["Cleaned", "TransformationCleaned"], defState="Cleaning"),
            "Completing": State(13, ["Validating"], defState="Completing"),
            "Stopped": State(12, ["Active"], defState="Stopped"),
            "TransformationCleaned": State(16, ["Archived", "Cleaned"], defState="Archived"),
            "Archived": State(11),  # final state
            "Completed": State(10, ["TransformationCleaned", "Archived"], defState="Completed"),
            "WaitingIntegrity": State(9, ["ValidatedOutput"], defState="WaitingIntegrity"),
            "ValidatedOutput": State(8, ["Active", "Completed"], defState="ValidatedOutput"),
            "ValidatingOutput": State(7, ["Active", "ValidatedOutput", "WaitingIntegrity"], defState="ValidatedOutput"),
            "RemovedFiles": State(6, ["Completed"], defState="RemovedFiles"),
            "RemovingFiles": State(5, ["RemovedFiles"], defState="RemovingFiles"),
            "ValidatingInput": State(4, ["Active", "RemovingFiles"], defState="ValidatingInput"),
            "Flush": State(3, ["Active"], defState="Active"),
            "Idle": State(
                2,
                ["Active", "Stopped", "ValidatingInput", "ValidatingOutput", "Completed", "Cleaning", "Testing"],
                defState="Idle",
            ),
            "Active": State(
                1,
                [
                    "Flush",
                    "Idle",
                    "Stopped",
                    "Completing",
                    "ValidatingInput",
                    "ValidatingOutput",
                    "TransformationCleaned",
                ],
                defState="Flush",
            ),
            "Testing": State(17, ["Idle"], defState="Testing"),
            "New": State(0, ["Active", "Testing", "Cleaning"], defState="New"),  # initial state
        }

        # NEW states proposal
        # self.states = {
        #     'Cleaned': State(10), # final state
        #     'Cleaning': State(9, ['Cleaned']),
        #     'Completing': State(8, ['Validating', 'Cleaning'], defState = 'Validating'),
        #     'TransformationCleaned': State(16, ['Archived', 'Cleaned'], defState = 'Archived'),
        #     'Stopped': State(7, ['Active', 'Flush', 'Cleaning'], defState = 'Active'),
        #     'Archived': State(6),  # final state
        #     'Completed': State(5, ['Archived'], defState = 'Archived'),
        #     'Validating': State(4, ['Active', 'Completed', 'Cleaning'], defState = 'Completed'),
        #     # Idle to Completed? Should it be that when setting a prod to completed it actually goes to validating?
        #     'Idle': State(3, ['Active', 'Validating', 'Cleaning'], defState = 'Active'),
        #     'Flush': State(2, ['Active', 'Cleaning'], defState = 'Active'),
        #     'Active': State(1, ['Flush', 'Idle', 'Stopped', 'Completing', 'Validating', 'Cleaning'], defState = 'Flush'),
        #     'New': State(0, ['Active', 'Cleaning'], defState = 'Active')  # initial state
        # }
