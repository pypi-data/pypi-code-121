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
""" Module containing a front-end to the ElasticSearch-based ElasticMCGaussLogErrorsDB.

    Here we define a mapping which is taken from a list of log errors.
"""
from DIRAC import gConfig
from DIRAC.ConfigurationSystem.Client.PathFinder import getDatabaseSection
from DIRAC.ConfigurationSystem.Client.Helpers import CSGlobals
from LHCbDIRAC.ProductionManagementSystem.DB.ElasticMCStatsDBBase import ElasticMCStatsDBBase

name = "ElasticMCBooleLogErrorsDB"

mapping = {
    "properties": {
        "wmsID": {"type": "long"},
        "ProductionID": {"type": "integer"},
        "JobID": {"type": "integer"},
        "ERROR": {"type": "short"},
        "WARNING": {"type": "short"},
        "FATAL": {"type": "short"},
    }
}


class ElasticMCBooleLogErrorsDB(ElasticMCStatsDBBase):
    def __init__(self):
        """Standard Constructor"""

        section = getDatabaseSection("ProductionManagement", "ElasticMCBooleLogErrorsDB")
        indexPrefix = gConfig.getValue("%s/IndexPrefix" % section, CSGlobals.getSetup()).lower()

        # Connecting to the ES cluster
        super(ElasticMCBooleLogErrorsDB, self).__init__(
            name, "ProductionManagement/ElasticMCBooleLogErrorsDB", indexPrefix
        )

        self.indexName = "%s_%s" % (self.getIndexPrefix(), name.lower())
        # Verifying if the index is there, and if not create it
        if not self.client.indices.exists(self.indexName):
            result = self.createIndex(self.indexName, mapping, period=None)
            if not result["OK"]:
                self.log.error(result["Message"])
                raise RuntimeError(result["Message"])
            self.log.always("Index created:", self.indexName)

        self.dslSearch = self._Search(self.indexName)
