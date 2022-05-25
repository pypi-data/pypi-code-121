###############################################################################
# (c) Copyright 2021 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "LICENSE".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
"""Provides access to Analysis Productions specific functionality

For more information see :py:mod:`.AnalysisProductionsClient`.
"""
from datetime import datetime
from itertools import chain

from DIRAC import gConfig, gLogger
from DIRAC.Core.Tornado.Server.TornadoService import TornadoService
from DIRAC.Core.Security.Properties import PRODUCTION_MANAGEMENT
from DIRAC.Core.Utilities.ReturnValues import returnValueOrRaise, convertToReturnValue
from DIRAC.DataManagementSystem.Client.DataManager import DataManager
from DIRAC.Resources.Storage.StorageElement import StorageElement
from LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient import BookkeepingClient
from LHCbDIRAC.TransformationSystem.Client.TransformationClient import TransformationClient
from LHCbDIRAC.ProductionManagementSystem.DB.AnalysisProductionsDB import AnalysisProductionsDB

optDate = (type(None), datetime)
optString = (type(None), str)

sLog = gLogger.getSubLogger(__name__)
sLog._setOption("tornadoComponent", "ProductionManagement/TornadoAnalysisProduction")


class TornadoAnalysisProductionsHandler(TornadoService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def initializeHandler(cls, serviceInfoDict):
        """initialize handler"""
        cls._db = AnalysisProductionsDB(parentLogger=cls.log)

    types_listAnalyses = [optDate]

    @convertToReturnValue
    def export_listAnalyses(self, at_time):
        """See :meth:`~.AnalysisProductionsClient.listAnalyses`"""
        return self._db.listAnalyses(at_time=at_time)

    types_getProductions = [optString, optString, optString, optString, optString, bool, bool, bool, optDate]

    @convertToReturnValue
    def export_getProductions(
        self, wg, analysis, version, name, state, with_lfns, with_pfns, with_transformations, at_time
    ):
        """See :meth:`~.AnalysisProductionsClient.getProductions`"""
        if (analysis or name or version) and wg is None:
            raise TypeError("wg must be specified when providing an analysis name or sample name/version")
        if with_pfns and not with_lfns:
            raise TypeError("with_pfns cannot be used without with_lfns")
        results = self._db.getProductions(
            wg=wg, analysis=analysis, version=version, name=name, state=state, at_time=at_time
        )
        return _queryToResults(results, with_lfns, with_pfns, with_transformations)

    types_getArchivedRequests = [optString, bool, bool, bool]

    @convertToReturnValue
    def export_getArchivedRequests(self, state, with_lfns, with_pfns, with_transformations):
        """See :meth:`~.AnalysisProductionsClient.getArchivedRequests`"""
        if with_pfns and not with_lfns:
            raise TypeError("with_pfns cannot be used without with_lfns")
        results = self._db.getArchivedRequests(state=state)
        return _queryToResults(results, with_lfns, with_pfns, with_transformations)

    types_getTags = [optString, optString, optDate]

    @convertToReturnValue
    def export_getTags(self, wg, analysis, at_time):
        """See :meth:`~.AnalysisProductionsClient.getTags`"""
        return self._db.getTags(wg, analysis, at_time=at_time)

    types_getKnownAutoTags = []

    @convertToReturnValue
    def export_getKnownAutoTags(self):
        """See :meth:`~.AnalysisProductionsClient.getKnownAutoTags`"""
        return list(self._db.getKnownAutoTags())

    # types_registerRequest = [list]
    # auth should be PRODUCTION_MANAGEMENT!
    # @convertToReturnValue
    # def export_registerRequest(self, requests):
    #     return self._db.registerRequest(requests)

    types_registerTransformations = [dict]

    @convertToReturnValue
    def export_registerTransformations(self, transforms):
        """See :meth:`~.AnalysisProductionsClient.registerTransformations`"""
        transforms = {int(k): v for k, v in transforms.items()}
        return self._db.registerTransformations(transforms)

    types_deregisterTransformations = [dict]

    @convertToReturnValue
    def export_deregisterTransformations(self, tIDs):
        """See :meth:`~.AnalysisProductionsClient.deregisterTransformations`"""
        tIDs = {int(k): v for k, v in tIDs.items()}
        return self._db.deregisterTransformations(tIDs)

    types_registerRequests = [list]

    @convertToReturnValue
    def export_registerRequests(self, requests):
        """See :meth:`~.AnalysisProductionsClient.registerRequests`"""
        results = self._db.registerRequests(requests)
        return _queryToResults(results, with_lfns=False, with_pfns=False, with_transformations=False)

    # types_registerSamples = [list]
    # auth should be PRODUCTION_MANAGEMENT!
    # @convertToReturnValue
    # def export_registerSamples(self, samples):
    #   """See :meth:`~.AnalysisProductionsClient.registerSamples`"""

    types_archiveSamples = [list]

    @convertToReturnValue
    def export_archiveSamples(self, sample_ids):
        """See :meth:`~.AnalysisProductionsClient.archiveSamples`"""
        return self._db.archiveSamples(sample_ids)

    types_setState = [dict]

    @convertToReturnValue
    def export_setState(self, newState):
        """See :meth:`~.AnalysisProductionsClient.setState`"""
        return self._db.setState(newState)

    types_setTags = [dict, dict]

    @convertToReturnValue
    def export_setTags(self, oldTags, newTags):
        """See :meth:`~.AnalysisProductionsClient.setTags`"""
        return self._db.setTags(oldTags, newTags)


def _queryToResults(results, with_lfns, with_pfns, with_transformations):
    """Convert a query of Request or AP objects to a JSON compatible object"""
    p2tID = {
        result["request_id"]: {tInfo["id"]: tInfo["used"] for tInfo in result["transformations"]} for result in results
    }

    if with_lfns:
        lfns = _getOutputLFNs(p2tID)
        if with_pfns:
            replicas = _getReplicas(list(chain(*lfns.values())))

        for result in results:
            result["lfns"] = {} if with_pfns else []
            result["total_bytes"] = 0
            if with_pfns:
                result["available_bytes"] = 0
            for tInfo in result["transformations"]:
                for lfn, lfnMeta in lfns.get(tInfo["id"], {}).items():
                    result["total_bytes"] += lfnMeta["FileSize"]
                    if not with_pfns:
                        result["lfns"].append(lfn)
                    elif lfn in replicas["Failed"]:
                        result["lfns"][lfn] = []
                        sLog.warn(
                            "Failed to get replicas for Analysis Production LFN",
                            "%s in rID=%s tID=%s: %s"
                            % (lfn, result["request_id"], tInfo["id"], replicas["Failed"][lfn]),
                        )
                    else:
                        result["lfns"][lfn] = [
                            pfn
                            for pfn in replicas["Successful"][lfn].values()
                            # Ignore entries with the value True as these are at unsupported SEs
                            if isinstance(pfn, str)
                        ]
                        if result["lfns"][lfn]:
                            result["available_bytes"] += lfnMeta["FileSize"]

    if with_transformations:
        tIDs = list(set(chain(*p2tID.values())))
        if tIDs:
            tClient = TransformationClient()
            retVal = tClient.getTransformations(
                condDict={"TransformationID": tIDs},
                limit=10000,
                columns=["TransformationID", "Status"],
            )
            extraTransInfos = {t["TransformationID"]: t for t in returnValueOrRaise(retVal)}
            for tInfo in chain(*(r["transformations"] for r in results)):
                tInfo["status"] = extraTransInfos[tInfo["id"]]["Status"]
    else:
        for result in results:
            del result["transformations"]

    return results


def _getOutputLFNs(pID2tID):
    sLog.info("Getting output LFNs")
    retVal = BookkeepingClient().getProductionFilesBulk(
        [tID for tIDs in pID2tID.values() for tID, used in tIDs.items() if used],
        "ALL",
        "ALL",
    )
    lfns = {}
    for tID, lfnMetadata in returnValueOrRaise(retVal).items():
        lfns[int(tID)] = {lfn: meta for lfn, meta in lfnMetadata.items() if meta["GotReplica"].lower().startswith("y")}
    return lfns


def _getReplicas(lfns):
    sLog.info("Getting replicas for", f"{len(lfns)} LFNs")
    replicas = returnValueOrRaise(DataManager().getReplicas(lfns, diskOnly=True, getUrl=False))
    for se in gConfig.getValue("/Resources/Sites/LCG/LCG.CERN.cern/SE", []):
        seLFNs = {lfn for lfn, replicaInfo in replicas["Successful"].items() if se in replicaInfo}
        if not seLFNs:
            continue
        sLog.info("Getting PFNs for", f"{len(seLFNs)} LFNs at {se}")
        result = returnValueOrRaise(StorageElement(se).getURL(list(seLFNs), protocol="root"))
        if result["Failed"]:
            raise NotImplementedError(result["Failed"])
        for lfn, pfn in result["Successful"].items():
            replicas["Successful"][lfn][se] = pfn
    return replicas
