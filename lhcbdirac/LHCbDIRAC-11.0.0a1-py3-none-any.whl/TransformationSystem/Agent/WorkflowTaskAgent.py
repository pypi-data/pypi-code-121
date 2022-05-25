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
:mod:  WorkflowTaskAgent

.. module:  WorkflowTaskAgent

:synopsis:  Extension of the DIRAC WorkflowTaskAgent, to use LHCb clients.
"""

from DIRAC.ConfigurationSystem.Client.Helpers.Operations import Operations
from DIRAC.TransformationSystem.Agent.WorkflowTaskAgent import WorkflowTaskAgent as DIRACWorkflowTaskAgent

from LHCbDIRAC.Interfaces.API.LHCbJob import LHCbJob
from LHCbDIRAC.TransformationSystem.Client.TaskManager import LHCbWorkflowTasks
from LHCbDIRAC.TransformationSystem.Client.TransformationClient import TransformationClient

AGENT_NAME = "Transformation/WorkflowTaskAgent"


class WorkflowTaskAgent(DIRACWorkflowTaskAgent):
    """An AgentModule class to submit workflow tasks."""

    def __init__(self, *args, **kwargs):
        """c'tor."""
        DIRACWorkflowTaskAgent.__init__(self, *args, **kwargs)

    def _getClients(self):
        """LHCb clients."""
        res = DIRACWorkflowTaskAgent._getClients(self)

        outputDataModule = Operations().getValue(
            "Transformations/OutputDataModule", "LHCbDIRAC.Core.Utilities.OutputDataPolicy"
        )

        threadTransformationClient = TransformationClient()
        threadTaskManager = LHCbWorkflowTasks(outputDataModule=outputDataModule, jobClass=LHCbJob)
        res.update({"TransformationClient": threadTransformationClient, "TaskManager": threadTaskManager})
        return res
