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
""" Module containing a front-end to the ElasticSearch-based ElasticPrMonDB.
"""

from DIRAC import gConfig
from DIRAC.ConfigurationSystem.Client.PathFinder import getDatabaseSection
from DIRAC.ConfigurationSystem.Client.Helpers import CSGlobals
from LHCbDIRAC.ProductionManagementSystem.DB.ElasticMCStatsDBBase import ElasticMCStatsDBBase

name = "ElasticPrMonDB"

mapping = {
    "properties": {
        "wmsID": {"type": "long"},
        "ProductionID": {"type": "integer"},
        "JobID": {"type": "integer"},
        "Avg": {
            "properties": {
                "nprocs": {"type": "float"},
                "nthreads": {"type": "float"},
                "pss": {"type": "float"},
                "rchar": {"type": "float"},
                "read_bytes": {"type": "float"},
                "rss": {"type": "float"},
                "rx_bytes": {"type": "float"},
                "rx_packets": {"type": "float"},
                "swap": {"type": "float"},
                "tx_bytes": {"type": "float"},
                "tx_packets": {"type": "float"},
                "vmem": {"type": "float"},
                "wchar": {"type": "float"},
                "write_bytes": {"type": "float"},
            }
        },
        "Max": {
            "properties": {
                "nprocs": {"type": "integer"},
                "nthreads": {"type": "integer"},
                "pss": {"type": "long"},
                "rchar": {"type": "long"},
                "read_bytes": {"type": "long"},
                "rss": {"type": "long"},
                "rx_bytes": {"type": "long"},
                "rx_packets": {"type": "long"},
                "swap": {"type": "integer"},
                "tx_bytes": {"type": "long"},
                "tx_packets": {"type": "long"},
                "vmem": {"type": "long"},
                "wchar": {"type": "long"},
                "write_bytes": {"type": "long"},
                "stime": {"type": "integer"},
                "utime": {"type": "integer"},
                "wtime": {"type": "integer"},
            }
        },
        "HW": {
            "properties": {
                "cpu": {
                    "properties": {
                        "CPUs": {"type": "integer"},
                        "CoresPerSocket": {"type": "integer"},
                        "ModelName": {"type": "text"},
                        "Sockets": {"type": "integer"},
                        "ThreadsPerCore": {"type": "integer"},
                    }
                },
                "mem": {"properties": {"MemTotal": {"type": "long"}}},
            }
        },
    }
}


class ElasticPrMonDB(ElasticMCStatsDBBase):
    def __init__(self):
        """Standard Constructor"""

        section = getDatabaseSection("ProductionManagement", "ElasticPrMonDB")
        indexPrefix = gConfig.getValue("%s/IndexPrefix" % section, CSGlobals.getSetup()).lower()

        # Connecting to the ES cluster
        super(ElasticPrMonDB, self).__init__(name, "ProductionManagement/ElasticPrMonDB", indexPrefix)

        self.indexName = "%s_%s" % (self.getIndexPrefix(), name.lower())
        # Verifying if the index is there, and if not create it
        if not self.client.indices.exists(self.indexName):
            result = self.createIndex(self.indexName, mapping, period=None)
            if not result["OK"]:
                self.log.error(result["Message"])
                raise RuntimeError(result["Message"])
            self.log.always("Index created:", self.indexName)

        self.dslSearch = self._Search(self.indexName)
