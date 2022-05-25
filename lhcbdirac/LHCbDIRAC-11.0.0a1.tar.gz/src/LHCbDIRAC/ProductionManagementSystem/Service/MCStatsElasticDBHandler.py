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
""" DIRAC service that expose access for MCStatsElasticDBs (several ElasticSearch DBs)
"""
import six

from DIRAC import S_OK
from DIRAC.Core.DISET.RequestHandler import RequestHandler
from LHCbDIRAC.ProductionManagementSystem.DB.ElasticApplicationSummaryDB import ElasticApplicationSummaryDB
from LHCbDIRAC.ProductionManagementSystem.DB.ElasticMCBooleLogErrorsDB import ElasticMCBooleLogErrorsDB
from LHCbDIRAC.ProductionManagementSystem.DB.ElasticMCGaussLogErrorsDB import ElasticMCGaussLogErrorsDB
from LHCbDIRAC.ProductionManagementSystem.DB.ElasticPrMonDB import ElasticPrMonDB


class MCStatsElasticDBHandler(RequestHandler):
    """Tiny service for setting/getting/removing data from ElasticSearch MCStats DBs"""

    @classmethod
    def initializeHandler(cls, serviceInfoDict):
        elasticApplicationSummaryDB = ElasticApplicationSummaryDB()
        elasticMCBooleLogErrorsDB = ElasticMCBooleLogErrorsDB()
        elasticMCGaussLogErrorsDB = ElasticMCGaussLogErrorsDB()
        elasticPrMonDB = ElasticPrMonDB()

        cls.db = {
            "XMLSummary": elasticApplicationSummaryDB,
            "booleErrors": elasticMCBooleLogErrorsDB,
            "gaussErrors": elasticMCGaussLogErrorsDB,
            "prMon": elasticPrMonDB,
        }

        return S_OK()

    types_set = [six.string_types, dict]

    def export_set(self, typeName, data):

        self.log.debug("Called set() with typeName = %s, data = %s" % (typeName, str(data)))
        return self.db[typeName].set(data)

    types_get = [six.string_types, int]

    def export_get(self, typeName, productionID):

        self.log.debug("Called get() with typeName = %s, productionID = %d" % (typeName, productionID))
        return self.db[typeName].get(productionID)

    types_remove = [six.string_types, int]

    def export_remove(self, typeName, productionID):

        self.log.debug("Called remove() with typeName = %s, productionID = %d" % (typeName, productionID))
        return self.db[typeName].remove(productionID)
