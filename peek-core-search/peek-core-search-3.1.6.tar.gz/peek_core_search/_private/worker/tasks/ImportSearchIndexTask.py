import logging
from collections import namedtuple
from datetime import datetime
from typing import List

import pytz
from sqlalchemy import select

from peek_core_search._private.storage.SearchIndex import SearchIndex
from peek_core_search._private.storage.SearchIndexCompilerQueue import (
    SearchIndexCompilerQueue,
)
from peek_core_search._private.worker.tasks.KeywordSplitter import (
    splitFullKeywords,
    splitPartialKeywords,
)
from peek_core_search._private.worker.tasks._CalcChunkKey import makeSearchIndexChunkKey
from peek_plugin_base.worker import CeleryDbConn

logger = logging.getLogger(__name__)

ObjectToIndexTuple = namedtuple(
    "ObjectToIndexTuple", ["id", "fullKwProps", "partialKwProps"]
)


def removeObjectIdsFromSearchIndex(deletedObjectIds: List[int]) -> None:
    pass


def reindexSearchObject(conn, objectsToIndex: List[ObjectToIndexTuple]) -> None:
    """Reindex Search Object

    :param conn:
    :param objectsToIndex: Object To Index
    :returns:
    """

    logger.debug("Starting to index %s SearchIndex", len(objectsToIndex))

    searchIndexTable = SearchIndex.__table__
    queueTable = SearchIndexCompilerQueue.__table__

    startTime = datetime.now(pytz.utc)

    newSearchIndexes = []
    objectIds = []
    searchIndexChunksToQueue = set()

    for objectToIndex in objectsToIndex:
        newSearchIndexes.extend(_indexObject(objectToIndex))
        objectIds.append(objectToIndex.id)

    newIdGen = CeleryDbConn.prefetchDeclarativeIds(SearchIndex, len(newSearchIndexes))
    for newSearchIndex in newSearchIndexes:
        newSearchIndex.id = next(newIdGen)
        searchIndexChunksToQueue.add(newSearchIndex.chunkKey)

    results = conn.execute(
        select(
            columns=[searchIndexTable.c.chunkKey],
            whereclause=searchIndexTable.c.objectId.in_(objectIds),
        )
    )

    for result in results:
        searchIndexChunksToQueue.add(result.chunkKey)

    if objectIds:
        conn.execute(
            searchIndexTable.delete(searchIndexTable.c.objectId.in_(objectIds))
        )

    if newSearchIndexes:
        logger.debug("Inserting %s SearchIndex", len(newSearchIndexes))
        inserts = [o.tupleToSqlaBulkInsertDict() for o in newSearchIndexes]
        conn.execute(searchIndexTable.insert(), inserts)

    if searchIndexChunksToQueue:
        conn.execute(
            queueTable.insert(), [dict(chunkKey=k) for k in searchIndexChunksToQueue]
        )

    logger.info(
        "Inserted %s SearchIndex keywords in %s",
        len(newSearchIndexes),
        (datetime.now(pytz.utc) - startTime),
    )


# stopwords = set()  # nltk.corpus.stopwords.words('english'))
# stopwords.update(list(string.punctuation))
#
# from nltk import PorterStemmer
#
# stemmer = PorterStemmer()


# from nltk.stem import WordNetLemmatizer
#
# lemmatizer = WordNetLemmatizer()


def _indexObject(objectToIndex: ObjectToIndexTuple) -> List[SearchIndex]:
    """Index Object

    This method creates  the "SearchIndex" objects to insert into the DB.

    Because our data is not news articles, we can skip some of the advanced
    natural language processing (NLP)

    We're going to be indexing things like unique IDs, job titles, and equipment names.
    We may add exclusions for nuisance words later on.

    """
    searchIndexes = []

    for propKey, text in objectToIndex.fullKwProps.items():
        for token in splitFullKeywords(text):
            searchIndexes.append(
                SearchIndex(
                    chunkKey=makeSearchIndexChunkKey(token),
                    keyword=token,
                    propertyName=propKey,
                    objectId=objectToIndex.id,
                )
            )

    for propKey, text in objectToIndex.partialKwProps.items():
        for token in splitPartialKeywords(text):
            searchIndexes.append(
                SearchIndex(
                    chunkKey=makeSearchIndexChunkKey(token),
                    keyword=token,
                    propertyName=propKey,
                    objectId=objectToIndex.id,
                )
            )

    return searchIndexes


# if __name__ == '__main__':
#     objectToIndex = ObjectToIndexTuple(
#         id=1,
#         props={
#             'key': 'COMP3453453J',
#             'alias': 'AB1345XXX',
#             'name': 'Hello, this is tokenising, strings string, child children'
#         }
#     )
#     print(_indexObject(objectToIndex))
