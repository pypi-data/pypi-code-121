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
"""Client for accessing data about Analysis Productions

Overview of concepts
--------------------

The basic objects stored for Analysis Productions are::

                  ┌─────────────┐
                  │ Publication │
                  └──────┬──────┘
                         *
                         │
                         1
  ┌─────────┐        ┌───┴────┐        ┌──────┐
  │ Request ├1──────*┤ Sample ├1──────*┤ User │
  └────┬────┘        └───┬────┘        └──────┘
       1                 1
       │                 │
       *                 *
  ┌────┴────┐         ┌──┴──┐
  │ AutoTag │         │ Tag │
  └─────────┘         └─────┘

* **Request**:
    A *Request* in the :py:mod:`.AnalysisProductionsDB` corresponds request in
    the :py:mod:`.ProductionRequestDB` with the type ``AnalysisProduction``.
    Each processed *Request* corresponds to 2 or more *Transformations* from
    the :py:mod:`.TransformationSystem` and the output LFNs are found by
    querying the Bookkeeping.
* **Sample**:
    A *Sample* wraps around a *Request* to allow a single sample to be reused.
    It can be uniquely identified by a ``WG``, ``analysis``, ``name`` and
    ``version`` where ``name`` comes from the original ``info.yaml`` file that
    was used to submit the production and ``version`` is the version of the tag
    in the ``AnalysisProductions`` data-package.
* **Tag**:
    A *Tag* is a `key` and `value` that can be used to query for a specific
    *Sample*. These can be manually defined by a _User_ to apply analysis specific
    metadata to a sample.
* **AutoTag**:
    Similar to a *Tag* how ever these are automatically computed from the
    *Bookkeeping* and applies to the underlying *Request* object. The keys of
    *AutoTags* are reserved and cannot be used by *Tags*.
* **User**:
    The nickname of the person who is able to modify and *Archive* a specific *Sample*.
* **Publication**:
    Denote that this was used for an LHCb result and the data for the underlying
    *Request* should be permanently preserved.

Archiving samples
-----------------

Arching a *Sample* is a way of denoting that is no longer useful. Typically
because it has been superseded be another *Sample*. When all child *Samples*
of a *Request* have been archived it is an indication that the data of the
*Request* can be permanently deleted.

Time travel
-----------

Most methods have an optional ``at_time`` argument which can be used to query
the database at a specific point in the past. This allows for the database to
continue to be chaged over time and while still allowing for high quality
analysis preservation.

Populating the database
-----------------------

The database is populated automatically by the :py:mod:`.APSyncAgent`.

Legacy considerations
---------------------

Prior to the creation of the ``AnalysisProductions`` data-package, the
``WG/CharmConfig`` and ``WG/CharmWGProd`` were used to automatically submit
production requests. Samples from this system were manually imported and are
mostly the same as those submitted by ``AnalysisProductions`` except the
``version`` of the production is of the form ``vXrYpZ (PackageName)``.

API Reference
-------------
"""
from typing import Any, Optional as Opt
from datetime import datetime

from DIRAC.Core.Base.Client import Client, createClient


@createClient("ProductionManagement/AnalysisProductions")
class AnalysisProductionsClient(Client):
    """Provides access to the data stored in the Analysis Productions database.

    This class wraps all the RPC calls to default parameters to be injected.
    """

    def __init__(self, url=None, **kwargs):
        super(AnalysisProductionsClient, self).__init__(**kwargs)
        self.setServer("ProductionManagement/AnalysisProductions")
        if url:
            self.setServer(url)

    def listAnalyses(self, *, at_time: Opt[datetime] = None):
        """Return the mapping of known WGs to analyses

        :param at_time: The datetime at which this query should be ran, defaults to now
        :returns: `dict` mapping the WG name to a list of analyses
        """
        return self.executeRPC(at_time, call="listAnalyses")

    def getProductions(
        self,
        *,
        wg: Opt[str] = None,
        analysis: Opt[str] = None,
        version: Opt[str] = None,
        name: Opt[str] = None,
        state: Opt[str] = None,
        with_lfns: bool = True,
        with_pfns: bool = True,
        with_transformations: bool = False,
        at_time: Opt[datetime] = None,
    ):
        """Return the list of productions for a specific analysis

        :param wg: The WG to which the analysis belongs
        :param analysis: The name of the analysis
        :param state: The state of the underlying request
        :param version: The version of the data package to include
        :param state: The name of the sample
        :param with_lfns: Include LFNs in the output, default True
        :param with_pfns: Include PFNs in the output, default True
        :param with_transformations: Include transformation info in the output, default False
        :param at_time: The datetime at which this query should be ran, defaults to now
        :returns: A dictionary of name -> version -> requestID
        """
        return self.executeRPC(
            wg,
            analysis,
            version,
            name,
            state,
            with_lfns,
            with_pfns,
            with_transformations,
            at_time,
            call="getProductions",
        )

    def getArchivedRequests(
        self,
        *,
        state: Opt[str] = None,
        with_lfns: bool = False,
        with_pfns: bool = False,
        with_transformations: bool = False,
    ):
        """Return the list of requests which are no longer used for analysis

        :param state: The state of the underlying request
        :param with_lfns: Include LFNs in the output, default False
        :param with_pfns: Include PFNs in the output, default False
        :param with_transformations: Include transformation info in the output, default False
        :returns: A dictionary of name -> version -> requestID
        """
        return self.executeRPC(state, with_lfns, with_pfns, with_transformations, call="getArchivedRequests")

    def getTags(self, *, wg: Opt[str] = None, analysis: Opt[str] = None, at_time: Opt[datetime] = None):
        """Return the list of productions for a specific analysis

        :param wg: The WG to which the analysis belongs
        :param analysis: The name of the analysis
        :param at_time: The datetime at which this query should be ran, defaults to now
        :returns: A dictionary of name -> version -> requestID
        """
        return self.executeRPC(wg, analysis, at_time, call="getTags")

    def getKnownAutoTags(self):
        """Return a list of all known automatic tag names"""
        return self.executeRPC(call="getKnownAutoTags")

    def setState(self, newState: dict[int, dict[str, Any]]):
        """Update the state of requests in the Analysis Productions database

        :param newState: Dictionary of the form {requestID: {"state" : "newState", "progress": 0.5}}}
        :returns: S_OK() || S_ERROR()
        """
        return self.executeRPC(newState, call="setState")

    def registerTransformations(self, transformations: dict[int, list[dict]]):
        """Update the state of requests in the Analysis Productions database

        :param transformations: Dictionary of the form {requestID: [tInfo, tInfo, ...]}}
        :returns: S_OK() || S_ERROR()
        """
        return self.executeRPC(transformations, call="registerTransformations")

    def deregisterTransformations(self, tIDs: dict[int, list[int]]):
        """Deregister the some transformations associated with a request

        :param tIDs: Dictionary of the form {requestID: [tID, tID, ...]}}
        :returns: S_OK() || S_ERROR()
        """
        return self.executeRPC(tIDs, call="deregisterTransformations")

    def registerRequests(self, requests):
        """Add a new production to the database

        :param requests: List of dictionaries
        :returns: S_OK() || S_ERROR()
        """
        return self.executeRPC(requests, call="registerRequests")

    def registerSamples(self, samples):
        """Add a new production to the database

        :param samples: List of dictionaries
        :returns: S_OK() || S_ERROR()
        """
        return self.executeRPC(samples, call="registerSamples")

    def archiveSamples(self, samples):
        """Archive an analysis Sample

        :param samples: List of sample IDs
        :returns: S_OK() || S_ERROR()
        """
        return self.executeRPC(samples, call="archiveSamples")
