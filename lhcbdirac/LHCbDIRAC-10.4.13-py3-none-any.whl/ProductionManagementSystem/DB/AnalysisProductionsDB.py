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
"""Database class for storing information about Analysis Productions

For more information on the meaning of the various objects see :py:mod:`.AnalysisProductionsClient`.

Tables are defined using SQLAlchemy and imported from :py:mod:`.AnalysisProductionsObjects`.
Example usage of this class can be found in `Test_AnalysisProductionsDB.py`.
"""
import functools
from collections import defaultdict
from contextlib import contextmanager
from copy import deepcopy

from sqlalchemy import create_engine, func, or_, tuple_, select
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from DIRAC.ConfigurationSystem.Client.Utilities import getDBParameters
from DIRAC.Core.Base.DIRACDB import DIRACDB
from DIRAC.Core.Utilities.ReturnValues import returnValueOrRaise

from LHCbDIRAC.ProductionManagementSystem.DB.AnalysisProductionsObjects import (
    Base,
    AnalysisSample as AP,
    AutoTag,
    Tag,
    Request,
    User,
)


def inject_session(func):
    """Decorator to inject the session into a class method

    Decorator to start a SQLAlchemy Session and inject it in the wrapped function
    as a keyword argument.
    """

    @functools.wraps(func)
    def new_func(self, *args, **kwargs):
        if "session" in kwargs:
            raise NotImplementedError("session cannot be passed through the inject_session decorator")
        with self.session as session:
            return func(self, *args, **kwargs, session=session)

    return new_func


class AnalysisProductionsDB(DIRACDB):
    __engineCache = {}

    def __init__(self, *, url=None):
        self.fullname = self.__class__.__name__
        super().__init__()
        if url is None:
            param = returnValueOrRaise(getDBParameters("ProductionManagement/AnalysisProductionsDB"))
            url = f"mysql://{param['User']}:{param['Password']}@{param['Host']}:{param['Port']}/{param['DBName']}"
        self.setURL(url)

    def setURL(self, url):
        if url not in self.__engineCache or ":memory:" in url:
            engine = create_engine(
                url, pool_recycle=3600, echo_pool=True, echo=self.log.getLevel() == "DEBUG", future=True
            )
            Base.metadata.create_all(engine)
            self.__engineCache[url] = engine
        self.engine = self.__engineCache[url]

    @property
    @contextmanager
    def session(self):
        with Session(self.engine, future=True) as session, session.begin():
            yield session

    @inject_session
    def listAnalyses(self, *, at_time=None, session: Session):
        query = _filterForTime(session.query(AP.wg, AP.analysis).distinct(), AP, at_time)
        result = defaultdict(list)
        for wg, analysis in query:
            result[wg].append(analysis)
        return dict(result)

    @inject_session
    def getProductions(
        self, *, wg=None, analysis=None, version=None, name=None, state=None, at_time=None, session: Session
    ):
        query = session.query(AP)
        query = query.filter(*_buildCondition(wg, analysis, name, version))
        if state is not None:
            query = query.filter(AP.state == state)
        query = _filterForTime(query, AP, at_time)
        return [result.toDict() for result in query]

    @inject_session
    def getArchivedRequests(self, *, state=None, session: Session):
        sq = session.query(AP.request_id).filter(AP.validity_end.is_(None)).distinct().subquery()
        query = session.query(Request).filter(~Request.request_id.in_(select(sq)))
        if state is not None:
            query = query.filter(AP.state == state)
        return [result.toDict() for result in query]

    @inject_session
    def getTags(self, wg, analysis, *, at_time=None, session: Session):
        return _getTags(session, wg=wg, analysis=analysis, at_time=at_time)

    @inject_session
    def getKnownAutoTags(self, *, session) -> set:
        return _getKnownAutoTags(session)

    # @inject_session
    # def registerRequest(self, requests, *, session: Session):
    #     for request in requests:
    #         session.add(AP(**request))

    @inject_session
    def registerTransformations(self, transforms: dict[int, list[dict]], *, session: Session):
        if not transforms:
            raise ValueError("No transforms passed")
        transforms = deepcopy(transforms)
        for request in session.query(Request).filter(Request.request_id.in_(transforms)):
            knownTransforms = {t["id"] for t in request.extra_info["transformations"]}
            for transform in transforms.pop(request.request_id):
                if transform["id"] in knownTransforms:
                    raise ValueError(f"Transformation is already known {transform['id']}")
                # TODO: Validate the transform object
                request.extra_info["transformations"].append(transform)
                # By default SQLAlchemy doesn't detect changes in JSON columns when using the ORM
                # Ideally this should be fixed in the database definition but flagging manually is
                # good enough for now
                flag_modified(request, "extra_info")
        if transforms:
            raise ValueError(f"Did not find requests for IDs: {list(transforms)}")

    @inject_session
    def deregisterTransformations(self, tIDs: dict[int, list[int]], *, session: Session):
        """See :meth:`~.AnalysisProductionsClient.registerTransformations`"""
        if not tIDs:
            raise ValueError("No transform IDs passed")
        tIDs = deepcopy(tIDs)
        query = session.query(Request).filter(Request.request_id.in_(tIDs))
        for request in query:
            for tID in tIDs.pop(request.request_id):
                for i, transform in enumerate(request.extra_info["transformations"]):
                    if transform["id"] == tID:
                        request.extra_info["transformations"].pop(i)
                        break
                else:
                    raise ValueError(f"Transformation {tID} is not known")
                flag_modified(request, "extra_info")
        if tIDs:
            raise ValueError(f"Did not find requests for IDs: {list(tIDs)}")

    def registerRequests(self, requests: list[dict]):
        request_ids = {r["request_id"] for r in requests}
        with self.session as session:
            known_ids = {i for i, in session.query(AP.request_id).filter(AP.request_id.in_(request_ids))}
            if known_ids:
                raise ValueError(f"Already registered requests: {known_ids!r}")

            for r in requests:
                self.log.info(
                    "Registering Analysis Production request",
                    f"{r['wg']} {r['analysis']} {r['version']} {r['request_id']} {r['name']}",
                )
                sample = AP(
                    request_id=r["request_id"],
                    name=r["name"],
                    version=r["version"],
                    wg=r["wg"],
                    analysis=r["analysis"],
                    validity_start=r["validity_start"],
                    extra_info=r["extra_info"],
                    auto_tags=[AutoTag(name=x["name"], value=x["value"]) for x in r["auto_tags"]],
                )
                sample.owners = [User(username=x["username"]) for x in r["owners"]]
                session.add(sample)

        with self.session as session:
            query = session.query(AP)
            query = query.filter(AP.request_id.in_(request_ids))
            return [result.toDict() for result in query]

    @inject_session
    def archiveSamples(self, sample_ids: list[int], *, session: Session):
        self.log.info("Archiving Analysis Productions", ",".join(map(str, sample_ids)))
        query = session.query(AP.sample_id)
        query = query.filter(AP.sample_id.in_(sample_ids))
        known_sample_ids = {i for i, in query}
        if len(known_sample_ids) != len(sample_ids):
            raise ValueError(f"Unknown sample IDs passed {known_sample_ids - set(sample_ids)!r}")
        query = query.filter(AP.validity_end.is_(None))
        known_sample_ids = {i for i, in query}
        if len(known_sample_ids) != len(sample_ids):
            raise ValueError(f"Some samples have already been archived {known_sample_ids - set(sample_ids)!r}")
        query = session.query(AP).filter(AP.sample_id.in_(sample_ids))
        query.update({"validity_end": func.now()})

    @inject_session
    def setState(self, newState: dict[str, dict], *, session: Session):
        for request_id, updateDict in newState.items():
            query = session.query(Request).filter(Request.request_id == request_id)
            rowsUpdated = query.update({getattr(Request, k): v for k, v in updateDict.items()})
            if rowsUpdated != 1:
                raise ValueError(
                    f"Failed to update Request({request_id}) with {updateDict!r}, {rowsUpdated} matching rows found"
                )

    @inject_session
    def setTags(self, oldTags: dict[int, dict[str, str]], newTags: dict[int, dict[str, str]], *, session: Session):
        if set(oldTags) != set(newTags):
            raise ValueError("oldTags and newTags must contain the same keys")
        # Tags should always be lowercase in the database
        oldTags = {i: {str(k).lower(): str(v).lower() for k, v in x.items()} for i, x in oldTags.items()}
        newLengths = {i: len(x) for i, x in newTags.items()}
        newTags = {i: {str(k).lower(): str(v).lower() for k, v in x.items()} for i, x in newTags.items()}
        if newLengths != {i: len(x) for i, x in newTags.items()}:
            raise ValueError("newTags contains duplicate keys when converted to lowercase")

        # Compute what needs to be changed, while also ensuring the auto tags aren't touched
        knownAutoTags = _getKnownAutoTags(session)
        toRemove = []
        toAdd = []
        for sample_id, old in oldTags.items():
            new = newTags[sample_id]
            removed_tags = set(old) - set(new)
            modified_tags = {k: new[k] for k in set(new) & set(old) if new[k] != old[k]}
            added_tags = {k: new[k] for k in set(new) - set(old)}
            # Ensure that the automatic tags aren't being modifed
            if modifiedAutoTags := {*removed_tags, *modified_tags, *added_tags} & knownAutoTags:
                raise ValueError(f"Cannot modify AutoTags {modifiedAutoTags}")
            # Tags are modified by being removed and re-added allow for time-travel
            toRemove += [(sample_id, k) for k in {*removed_tags, *modified_tags}]
            toAdd += [(sample_id, k, v) for k, v in {**added_tags, **modified_tags}.items()]

        latestOldTags = _getTags(session, sample_ids=oldTags)
        if oldTags != latestOldTags:
            raise ValueError("oldTags is out of date")

        # Remove the old tags
        query = _filterForTime(session.query(Tag), Tag, at_time=None)
        query = query.filter(tuple_(Tag.sample_id, Tag.name).in_(toRemove))
        query.update({"validity_end": func.now()})
        # Add the new tag values
        for sample_id, name, value in toAdd:
            session.add(Tag(sample_id=sample_id, name=name, value=value))


def _getKnownAutoTags(session: Session):
    return {name for name, in session.query(AutoTag.name).distinct()}


def _getTags(session, *, wg=None, analysis=None, at_time=None, sample_ids=None):
    results = defaultdict(dict)
    # Get the automatic tags
    query = session.query(AP.sample_id, AutoTag.name, AutoTag.value)
    query = query.filter(AP.request_id == AutoTag.request_id)
    if sample_ids:
        query = query.filter(AP.sample_id.in_(sample_ids))
    query = query.filter(*_buildCondition(wg, analysis))
    query = _filterForTime(query, AP, at_time)
    for sampleID, name, value in query:
        results[sampleID][name] = value
    # Get the manual tags
    query = session.query(AP.sample_id, Tag.name, Tag.value)
    query = query.filter(AP.sample_id == Tag.sample_id)
    if sample_ids:
        query = query.filter(AP.sample_id.in_(sample_ids))
    if wg is not None:
        query = query.filter(*_buildCondition(wg, analysis))
    query = _filterForTime(query, AP, at_time)
    query = _filterForTime(query, Tag, at_time)
    for sampleID, name, value in query:
        results[sampleID][name] = value
    return dict(results)


def _filterForTime(query, obj, at_time):
    if at_time is None:
        return query.filter(obj.validity_end.is_(None))
    else:
        return query.filter(
            obj.validity_start <= at_time,
            or_(obj.validity_end.is_(None), at_time < obj.validity_end),
        )


def _buildCondition(wg, analysis=None, name=None, version=None):
    """Build a SQLAlchemy query for the AnalysisProductions table"""
    if wg is not None:
        yield func.lower(AP.wg) == func.lower(wg)
    if analysis is not None:
        yield func.lower(AP.analysis) == func.lower(analysis)
    if name is not None:
        yield func.lower(AP.name) == func.lower(name)
    if version is not None:
        yield AP.version == version
