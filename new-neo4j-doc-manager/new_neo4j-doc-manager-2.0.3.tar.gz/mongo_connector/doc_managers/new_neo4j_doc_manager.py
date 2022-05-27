# -*- coding: utf-8 -*-
# @Time    : 2022/4/24 上午11:08
# @Author  : kyq
# @Software: PyCharm


import base64
import logging
import os
import os.path as path, sys

import bson.json_util

from mongo_connector.doc_managers.nodes_and_relationships_builder import NodesAndRelationshipsBuilder
from mongo_connector.doc_managers.nodes_and_relationships_updater import NodesAndRelationshipsUpdater

from py2neo import Graph,NodeMatcher

from mongo_connector.compat import u
from mongo_connector.constants import (DEFAULT_COMMIT_INTERVAL,DEFAULT_MAX_BULK)
from mongo_connector.util import exception_wrapper, retry_until_ok
from mongo_connector.doc_managers.doc_manager_base import DocManagerBase
from mongo_connector.doc_managers.formatters import DefaultDocumentFormatter



LOG = logging.getLogger(__name__)


class DocManager(DocManagerBase):
    """
    Neo4j implementation for the DocManager. Receives documents and
    communicates with Neo4j Server.
    """

    def __init__(self, url, auto_commit_interval=DEFAULT_COMMIT_INTERVAL,
                 unique_key='_id', chunk_size=DEFAULT_MAX_BULK, **kwargs):
        # self.graph = Graph('http://127.0.0.1:7474/db/data')
        self.graph = Graph(url)
        self.auto_commit_interval = auto_commit_interval
        self.unique_key = unique_key
        self.chunk_size = chunk_size
        self._formatter = DefaultDocumentFormatter()
        self.kwargs = kwargs.get("clientOptions")
        self.actor = []
        self.director = []

    def stop(self):
        """Stop the auto-commit thread."""
        self.auto_commit_interval = None

    def upsert(self, doc,namespace,timestamp):
        """Inserts a document into Neo4j."""
        doc_id = u(doc.pop("_id"))
        doc = self._formatter.format_document(doc)
        builder = NodesAndRelationshipsBuilder(doc,doc_id)
        tx = self.graph.begin()
        for other_actor in builder.other_postion_list:
            for statement in other_actor.keys():
                doubanId = other_actor[statement]['doubanId']
                ret = self.nodeExist(doubanId)
                if ret == False:
                    tx.run(statement, {"parameters": other_actor[statement]})
                else:
                    pass

        for director in builder.director_list:
            for statement in director.keys():
                doubanId = director[statement]['doubanId']
                ret = self.nodeExist(doubanId)
                if ret == False:
                    tx.run(statement, {"parameters": director[statement]})
                else:
                    self.director.append(ret)

        for cast in builder.cast_list:
            for statement in cast.keys():
                doubanId = cast[statement]['doubanId']
                ret = self.nodeExist(doubanId)
                if ret == False:
                    if cast not in builder.director_list and cast not in builder.other_postion_list:
                        tx.run(statement, {"parameters": cast[statement]})
                else:
                    self.actor.append(ret)

        for director_ in builder.director_list:
            for director in director_.keys():
                for actor_ in builder.cast_list:
                    for actor in actor_.keys():
                        id = director_[director]['doubanId']
                        id_ = actor_[actor]['doubanId']
                        program_id = builder.parameters['programId']
                        type = "{" + " program_id:{},count:1".format([program_id]) + "}"
                        tx.run(self.creat_relationship(id, id_, type,program_id))

        tx.commit()

    def update(self, document_id, update_spec, namespace, timestamp):
        pass

    def remove(self, document_id, namespace, timestamp):
        """Removes a document from Neo4j."""
        pass

    def search(self, start_ts, end_ts):
        pass

    def get_last_doc(self):
        """Get the most recently modified node from Neo4j.
        This method is used to help define a time window within which documents
        may be in conflict after a MongoDB rollback.
        """
        LOG.error("Commit")

    def commit(self):
        LOG.error("Commit")

    def handle_command(self, doc, namespace, timestamp):
        db = namespace.split('.', 1)[0]

    def nodeExist(self, doubanId):
        matcher = NodeMatcher(self.graph)
        m = matcher.match().where(doubanId=doubanId).first()
        if m is None:
            return False
        else:
            return m

    def creat_relationship(self,id, doubanid, a,program_id):
        doubanId = "{" + "doubanId:'{}'".format(id) + "}"
        a=a
        director_doubanId = "{" + "doubanId:'{}'".format(doubanid) + "}"
        statement = 'MATCH (n{a}),(n1{b}),p=(n)-[r:Director_Actor]-(n1)  return r.count'.format(a=doubanId, b=director_doubanId)
        count = self.graph.begin().run(statement).data()
        if count != []:
            statement = 'MATCH (n{a}),(n1{b}),p=(n)-[r:Director_Actor]-(n1)  return r.program_id'.format(a=doubanId,b=director_doubanId)
            programId = self.graph.begin().run(statement).data()
            program_id = program_id
            programId_ = programId[0]['r.program_id']
            if program_id in programId_:
                count = count[0]['r.count']
            else:
                count = count[0]['r.count'] + 1
            programId_.append(program_id)
            statement = 'MATCH (n{a}),(n1{b}),p=(n)-[r:Director_Actor]-(n1) set r.count={c}, r.program_id={d} return r'.format(
                a=doubanId, b=director_doubanId, c=count, d=list(set(programId_)))
        else:
            statement = 'MATCH (director{a}), (actor{b}) CREATE (director)-[r:Director_Actor {c}]->(actor)'.format(a=director_doubanId, b=doubanId, c=a)
        return statement

    # def creat_relationship1(self,id, doubanid, a):
    #     doubanId = "{" + "doubanId:'{}'".format(id) + "}"
    #     director_doubanId = "{" + "doubanId:'{}'".format(doubanid) + "}"
    #     statement = 'MATCH (actor{a}), (director{b}) CREATE (actor)-[r:Actor_Director {c}]->(director)'.format(a=director_doubanId, b=doubanId, c=a)
    #     return statement
