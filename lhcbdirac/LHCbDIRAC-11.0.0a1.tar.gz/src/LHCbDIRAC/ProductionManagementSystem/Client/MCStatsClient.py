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
"""Module holding MCStatsClient class."""
from DIRAC.Core.Base.Client import Client, createClient


@createClient("ProductionManagement/MCStatsElasticDB")
class MCStatsClient(Client):
    """Client for MCStatsElasticDB"""

    def __init__(self, **kwargs):
        """simple constructor."""

        super(MCStatsClient, self).__init__(**kwargs)
        self.setServer("ProductionManagement/MCStatsElasticDB")

    def set(self, typeName, data):
        """set some data in a certain type.

        :params str typeName: type name (e.g. 'gaussErrors')
        :params dict data: dictionary inserted

        :returns: S_OK/S_ERROR
        """
        return self._getRPC().set(typeName, data)

    def get(self, typeName, productionID):
        """get per Job ID.

        :params str typeName: type name (e.g. 'gaussErrors')
        :params int productionID: production ID
        """
        return self._getRPC().get(typeName, productionID)

    def remove(self, typeName, productionID):
        """remove data for productionID.

        :params str typeName: type name (e.g. 'gaussErrors')
        :params int productionID: production ID
        """
        return self._getRPC().remove(typeName, productionID)
