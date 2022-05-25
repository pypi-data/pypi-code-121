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
"""TransformationAgent is and LHCb class just for overwriting some of the DIRAC
methods."""

from DIRAC import gLogger, S_OK, S_ERROR
from DIRAC.ResourceStatusSystem.Client.ResourceManagementClient import ResourceManagementClient
from DIRAC.TransformationSystem.Agent.TransformationAgent import TransformationAgent as DIRACTransformationAgent

from LHCbDIRAC.TransformationSystem.Client.TransformationClient import TransformationClient
from LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient import BookkeepingClient

AGENT_NAME = "Transformation/LHCbTransformationAgent"


class TransformationAgent(DIRACTransformationAgent):
    """Extends base class."""

    def initialize(self):
        """LHCb defaults."""
        DIRACTransformationAgent.initialize(self)

        self.pluginLocation = self.am_getOption(
            "PluginLocation", "LHCbDIRAC.TransformationSystem.Agent.TransformationPlugin"
        )
        self.workDirectory = self.am_getWorkDirectory()
        self.debug = self.am_getOption("verbosePlugin", False)

        return S_OK()

    def _getClients(self):
        """returns the clients used in the threads."""
        res = DIRACTransformationAgent._getClients(self)

        threadTransformationClient = TransformationClient()
        threadRMClient = ResourceManagementClient()
        threadBkk = BookkeepingClient()

        res.update(
            {
                "TransformationClient": threadTransformationClient,
                "ResourceManagementClient": threadRMClient,
                "BookkeepingClient": threadBkk,
            }
        )

        return res

    def __generatePluginObject(self, plugin, clients):
        """Generates the plugin object."""
        try:
            plugModule = __import__(self.pluginLocation, globals(), locals(), ["TransformationPlugin"])
        except ImportError as x:
            gLogger.exception("%s.__generatePluginObject: Failed to import 'TransformationPlugin'" % AGENT_NAME, "", x)
            return S_ERROR()
        try:
            oPlugin = getattr(plugModule, "TransformationPlugin")(
                "%s" % plugin,
                dataManager=clients["DataManager"],
                transClient=clients["TransformationClient"],
                bkClient=clients["BookkeepingClient"],
                rmClient=clients["ResourceManagementClient"],
            )
        except Exception as x:  # pylint: disable=broad-except
            gLogger.exception("%s.__generatePluginObject: Failed to create %s()." % (AGENT_NAME, plugin), "", x)
            return S_ERROR()
        oPlugin.workDirectory = self.workDirectory
        oPlugin.pluginCallback = self.pluginCallback
        if self.debug:
            oPlugin.setDebug()
        return S_OK(oPlugin)
