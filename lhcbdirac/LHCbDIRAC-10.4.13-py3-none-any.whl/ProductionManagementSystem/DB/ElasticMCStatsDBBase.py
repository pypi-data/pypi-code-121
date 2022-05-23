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
    This module interacts with one ES index: "ElasticMCLogErrors",

    Here we define a mapping which is taken from a list of log errors.
"""
from DIRAC import S_OK, S_ERROR
from DIRAC.Core.Base.ElasticDB import ElasticDB


class ElasticMCStatsDBBase(ElasticDB):
    def set(self, data):
        """
        Inserts data into ElasticJobParametersDB index

        :param self: self reference
        :param str value: data to be inserted

        :returns: S_OK/S_ERROR as result of indexing
        """

        self.log.debug(
            self.__class__.__name__,
            ".set(): inserting data in %s:%s" % (self.indexName, data),  # pylint: disable=no-member
        )

        result = self.index(
            self.indexName,  # pylint: disable=no-member
            body=data,
            docID=str(data["ProductionID"]) + "_" + str(data["JobID"]),
        )
        if not result["OK"]:
            self.log.error("ERROR: Couldn't insert data", result["Message"])
        return result

    def get(self, productionID):
        """Get docs per productionID. Basically here only for tests, right now

        :param self: self reference
        :param int productionID: production ID

        :return: dict with all docs
        """

        self.log.debug(self.__class__.__name__ + ".get(): Getting for production %s" % str(productionID))

        resultList = []

        """ the following should be equivalent to
    {
      "query": {
        "bool": {
          "filter": {  # no scoring
            "term": {"ProductionID": productionID}  # term level query, does not pass through the analyzer
          }
        }
      }
    }
    """

        s = self.dslSearch.query("bool", filter=self._Q("term", ProductionID=productionID))  # pylint: disable=no-member

        res = s.execute()

        for hit in res:
            hitDict = {}
            for name in hit:
                hitDict[name] = getattr(hit, name)
            resultList.append(hitDict)

        return S_OK(resultList)

    def remove(self, productionID):
        """Remove docs per productionID. Basically here only for tests, right now

        :param self: self reference
        :param int productionID: production ID

        :return: S_OK/S_ERROR
        """

        self.log.debug(self.__class__.__name__ + ".remove(): Removing documents of production %s" % str(productionID))

        """ the following should be equivalent to
    {
      "query": {
        "bool": {
          "filter": {  # no scoring
            "term": {"ProductionID": productionID}  # term level query, does not pass through the analyzer
          }
        }
      }
    }
    """

        s = self.dslSearch.query("bool", filter=self._Q("term", ProductionID=productionID))  # pylint: disable=no-member
        try:
            s.delete()
        except Exception as e:
            self.log.exception()
            return S_ERROR(repr(e))

        return S_OK()
