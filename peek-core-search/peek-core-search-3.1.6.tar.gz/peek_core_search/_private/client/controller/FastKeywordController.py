""" Fast Graph DB

This module stores a memory resident model of a graph network.

"""
import logging
from collections import defaultdict
from datetime import datetime
from typing import Optional, List, Dict, Iterable, Set

import pytz
import json
from twisted.internet.defer import inlineCallbacks, Deferred
from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.Payload import Payload
from vortex.TupleAction import TupleActionABC
from vortex.handler.TupleActionProcessor import TupleActionProcessorDelegateABC

from peek_core_search._private.client.controller.SearchIndexCacheController import (
    SearchIndexCacheController,
)
from peek_core_search._private.client.controller.SearchObjectCacheController import (
    SearchObjectCacheController,
)
from peek_core_search._private.storage.EncodedSearchIndexChunk import (
    EncodedSearchIndexChunk,
)
from peek_core_search._private.tuples.KeywordAutoCompleteTupleAction import (
    KeywordAutoCompleteTupleAction,
)
from peek_core_search._private.tuples.search_object.SearchResultObjectTuple import (
    SearchResultObjectTuple,
)
from peek_core_search._private.worker.tasks.KeywordSplitter import (
    splitPartialKeywords,
    splitFullKeywords,
    _splitFullTokens,
)
from peek_core_search._private.worker.tasks._CalcChunkKey import makeSearchIndexChunkKey

logger = logging.getLogger(__name__)


class FastKeywordController(TupleActionProcessorDelegateABC):
    def __init__(
        self,
        objectCacheController: SearchObjectCacheController,
        indexCacheController: SearchIndexCacheController,
    ):
        self._objectCacheController = objectCacheController
        self._indexCacheController = indexCacheController
        self._objectIdsByKeywordByPropertyKeyByChunkKey: Dict[
            str, Dict[str, Dict[str, List[int]]]
        ] = {}

    def shutdown(self):
        self._objectCacheController = None
        self._indexCacheController = None
        self._objectIdsByKeywordByPropertyKeyByChunkKey = {}

    @inlineCallbacks
    def processTupleAction(self, tupleAction: TupleActionABC) -> Deferred:
        assert isinstance(
            tupleAction, KeywordAutoCompleteTupleAction
        ), "Tuple is not a KeywordAutoCompleteTupleAction"

        startTime = datetime.now(pytz.utc)

        objectIds = yield self._getObjectIdsForSearchString(
            tupleAction.searchString, tupleAction.propertyName
        )

        results = yield self._objectCacheController.getObjects(
            tupleAction.objectTypeId, objectIds
        )

        results = yield self._filterObjectsForSearchString(
            results, tupleAction.searchString, tupleAction.propertyName
        )

        logger.debug(
            "Completed search for |%s|, returning %s objects, in %s",
            tupleAction.searchString,
            len(results),
            (datetime.now(pytz.utc) - startTime),
        )

        return results

    @deferToThreadWrapWithLogger(logger)
    def _filterObjectsForSearchString(
        self,
        results: List[SearchResultObjectTuple],
        searchString: str,
        propertyName: Optional[str],
    ) -> Deferred:
        """Filter Objects For Search String

        STAGE 2 of the search.

        This method filters the loaded objects to ensure we have full matches.

        :param results:
        :param searchString:
        :param propertyName:
        :return:
        """

        noFulls = lambda t: not t.endswith("$")

        # Get the partial tokens, and match them
        tokens = set(filter(noFulls, splitPartialKeywords(searchString)))

        def filterResult(result: SearchResultObjectTuple) -> bool:
            props = result.properties
            if propertyName:
                props = (
                    {propertyName: props[propertyName]} if propertyName in props else {}
                )

            allPropVals = " ".join(props.values())
            theseTokens = set(filter(noFulls, splitPartialKeywords(allPropVals)))
            return bool(tokens & theseTokens)

        return list(filter(filterResult, results))

    @deferToThreadWrapWithLogger(logger)
    def _getObjectIdsForSearchString(
        self, searchString: str, propertyName: Optional[str]
    ) -> Deferred:
        """Get ObjectIds For Search String

        STAGE 1 of the search.

        This method loads all of the search objects that match the search strings.

        This will load in some false matches, they are filtered out in
        _filterObjectsForSearchString

        Searching is complex because we don't know if we're looking for a full
        or partial tokenizing.

        :rtype List[int]

        """
        logger.debug("Started search with string |%s|", searchString)

        # ---------------
        # Search for fulls
        fullTokens = splitFullKeywords(searchString)

        logger.debug("Searching for full tokens |%s|", fullTokens)

        # Now lookup any remaining keywords, if any
        resultsByFullKw = self._getObjectIdsForTokensBlocking(fullTokens, propertyName)
        resultsByFullKw = {k: v for k, v in resultsByFullKw.items() if v}

        logger.debug("Found results for full tokens |%s|", set(resultsByFullKw))

        # ---------------
        # Search for partials
        partialTokens = splitPartialKeywords(searchString)
        logger.debug("Searching for partial tokens |%s|", partialTokens)

        # Now lookup any remaining keywords, if any
        resultsByPartialKw = self._getObjectIdsForTokensBlocking(
            partialTokens, propertyName
        )
        resultsByPartialKw = {k: v for k, v in resultsByPartialKw.items() if v}

        logger.debug("Found results for partial tokens |%s|", set(resultsByPartialKw))

        # ---------------
        # Process the results

        # Merge partial kw results with full kw results.
        resultsByKw = self._mergePartialAndFullMatches(
            searchString, resultsByFullKw, resultsByPartialKw
        )

        logger.debug("Merged tokens |%s|", set(resultsByKw))

        # Now, return the ObjectIDs that exist in all keyword lookups
        objectIdsUnion = self._setIntersectFilterIndexResults(resultsByKw)

        # Limit to 50 and return
        return list(objectIdsUnion)[:50]

    def _mergePartialAndFullMatches(
        self,
        searchString: str,
        resultsByFullKw: Dict[str, List[int]],
        resultsByPartialKw: Dict[str, List[int]],
    ) -> Dict[str, List[int]]:
        """ Merge Partial """

        # Copy this, because we want to modify it and don't want to affect other logic
        resultsByPartialKw = resultsByPartialKw.copy()
        resultsByPartialKwSet = set(resultsByPartialKw)

        mergedResultsByKw = {}

        for fullKw, fullObjectIds in resultsByFullKw.items():
            # Merge in full
            fullKw = fullKw.strip("^$")
            existing = mergedResultsByKw.get(fullKw.strip("^$"), list())

            # Include the fulls
            existing.extend(fullObjectIds)

            mergedResultsByKw[fullKw] = existing

        tokens = _splitFullTokens(searchString)
        for token in tokens:
            token = token.strip("^$")
            existing = mergedResultsByKw.get(token.strip("^$"), list())
            partialKws = splitPartialKeywords(token)

            if not partialKws <= resultsByPartialKwSet:
                continue

            # Union all
            objectIdsForToken = set(resultsByPartialKw[partialKws.pop()])
            while partialKws:
                objectIdsForToken &= set(resultsByPartialKw[partialKws.pop()])

            existing.extend(list(objectIdsForToken))

            mergedResultsByKw[token] = existing

        return mergedResultsByKw

    def _setIntersectFilterIndexResults(
        self, objectIdsByKw: Dict[str, List[int]]
    ) -> Set[int]:

        if not objectIdsByKw:
            return set()

        keys = set(objectIdsByKw)
        twoCharTokens_ = set([t for t in keys if len(t) == 2])
        keys -= twoCharTokens_

        # Now, return the ObjectIDs that exist in all keyword lookups
        if keys:
            objectIdsUnion = set(objectIdsByKw[keys.pop()])
        else:
            objectIdsUnion = set(objectIdsByKw[twoCharTokens_.pop()])

        while keys:
            objectIdsUnion &= set(objectIdsByKw[keys.pop()])

        # Optionally, include two char tokens, if any exist.
        # The goal of this is to NOT show zero results if a two letter token doesn't match
        while twoCharTokens_:
            objectIdsUnionNoTwoChars = objectIdsUnion & set(
                objectIdsByKw[twoCharTokens_.pop()]
            )
            if objectIdsUnionNoTwoChars:
                objectIdsUnion = objectIdsUnionNoTwoChars

        return objectIdsUnion

    def _getObjectIdsForTokensBlocking(
        self, tokens: Iterable[str], propertyName: Optional[str]
    ) -> Dict[str, List[int]]:
        # Create the structure to hold the IDs, for a match, we need an object id to be
        # in every row.
        results = {kw: [] for kw in tokens}

        # Figure out which keywords are in which chunk keys
        keywordsByChunkKey = defaultdict(list)
        for kw in tokens:
            keywordsByChunkKey[makeSearchIndexChunkKey(kw)].append(kw)

        # Iterate through each of the chunks we need
        for chunkKey, keywordsInThisChunk in keywordsByChunkKey.items():
            objectIdsByKeywordByPropertyKey = (
                self._objectIdsByKeywordByPropertyKeyByChunkKey.get(chunkKey)
            )

            if not objectIdsByKeywordByPropertyKey:
                logger.debug("No SearchIndex chunk exists with chunkKey |%s|", chunkKey)
                continue

            # Get the keywords for the property we're searching for
            objectIdsByKeywordListOfDicts = []
            if propertyName is None:
                # All property keys
                objectIdsByKeywordListOfDicts = objectIdsByKeywordByPropertyKey.values()

            elif propertyName in objectIdsByKeywordByPropertyKey:
                # A specific property key
                objectIdsByKeywordListOfDicts = [
                    objectIdsByKeywordByPropertyKey[propertyName]
                ]

            # Iterate through each of the property keys, this isn't a big list
            for objectIdsByKeyword in objectIdsByKeywordListOfDicts:
                for kw in keywordsInThisChunk:
                    if kw in objectIdsByKeyword:
                        results[kw] += objectIdsByKeyword[kw]

        return results

    @inlineCallbacks
    def notifyOfUpdate(self, chunkKeys: List[str]):
        """Notify of Segment Updates

        This method is called by the client.SearchIndexCacheController when it receives
         updates from the server.

        """
        for chunkKey in chunkKeys:
            encodedChunkTuple = self._indexCacheController.encodedChunk(chunkKey)
            yield self._unpackKeywordsFromChunk(encodedChunkTuple)

    @deferToThreadWrapWithLogger(logger)
    def _unpackKeywordsFromChunk(self, chunk: EncodedSearchIndexChunk) -> None:

        chunkDataTuples = Payload().fromEncodedPayload(chunk.encodedData).tuples

        chunkData: Dict[str, Dict[str, List[int]]] = defaultdict(dict)

        for data in chunkDataTuples:
            keyword = data[EncodedSearchIndexChunk.ENCODED_DATA_KEYWORD_NUM]
            propertyName = data[EncodedSearchIndexChunk.ENCODED_DATA_PROPERTY_MAME_NUM]
            objectIdsJson = data[
                EncodedSearchIndexChunk.ENCODED_DATA_OBJECT_IDS_JSON_INDEX
            ]
            chunkData[propertyName][keyword] = json.loads(objectIdsJson)

        self._objectIdsByKeywordByPropertyKeyByChunkKey[chunk.chunkKey] = chunkData
