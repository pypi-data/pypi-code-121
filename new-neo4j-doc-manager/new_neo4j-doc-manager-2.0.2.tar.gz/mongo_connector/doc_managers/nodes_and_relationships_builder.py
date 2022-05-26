# -*- coding: utf-8 -*-
# @Time    : 2022/4/28 下午2:54
# @Author  : kyq
# @Software: PyCharm

import re
import logging

from bson.objectid import ObjectId
from py2neo import Graph,NodeMatcher
from mongo_connector.compat import u

LOG = logging.getLogger(__name__)


class NodesAndRelationshipsBuilder(object):
    def __init__(self, doc,doc_id):
        self.query_nodes = {}
        self.parameters = {}
        self.relationships_query = {}
        self.explicit_ids = {}
        self.cast_list = []
        self.director_list = []
        self.writer_list = []
        self.other_postion_list = []
        self.doc_id = doc_id
        self.build_nodes_query(doc,doc_id)

    def build_nodes_query(self, document,id):
        self.parameters = {'_id': id}
        for key in document.keys():
            if key != '_class':
                # TODO: handle arrays of ObjectIds
                if document[key] is None:
                    continue
                elif self.is_json_array(document[key]):
                    for json in self.format_params(document[key]):
                        if key == 'cast':
                            query = "CREATE (:Actor {parameters})"
                            query_nodes = {query:json}
                            self.cast_list.append(query_nodes)
                        elif key == 'director':
                            query = "CREATE (:Actor {parameters})"
                            query_nodes = {query: json}
                            self.director_list.append(query_nodes)
                        # elif key == 'writer':
                        #     query = "CREATE (:Actor {parameters})"
                        #     query_nodes = {query: json}
                        #     self.writer_list.append(query_nodes)
                        else:
                            query = "CREATE (:Actor {parameters})"
                            query_nodes = {query: json}
                            self.other_postion_list.append(query_nodes)
                else:
                    self.parameters.update({key: self.format_params(document[key])})




    def format_params(self, params):
        if (type(params) is list):
            return list(filter(None, params))
        return params

    def build_node_with_objectid_reference(self, root_type, key, doc_id, document_key):
        if document_key is None:
            return

        parameters = {'_id': u(document_key)}
        statement = "MERGE (d:Document {{_id: {{parameters}}._id}})"
        self.query_nodes.update({statement: {"parameters": parameters}})
        self.build_relationships_query(root_type, 'Document', doc_id, document_key)  # FIXME: missing doc_type

    def is_dict(self, doc_key):
        return (type(doc_key) is dict)

    def is_reference(self, key):
        return (re.search(r"_id$", key))

    def is_multimensional_array(self, doc_key):
        return ((type(doc_key) is list) and (doc_key) and (type(doc_key[0]) is list))

    def is_objectid(selfself, doc_key):
        return isinstance(doc_key, ObjectId)

    def flatenned_property(self, key, doc_key):
        parameters = {}
        flattened_list = doc_key
        if ((type(flattened_list[0]) is list) and (flattened_list[0])):
            inner_list = flattened_list[0]
            if (type(inner_list[0]) is list):
                flattened_list = [val for sublist in flattened_list for val in sublist]
                self.flatenned_property(key, flattened_list)
            else:
                for element in flattened_list:
                    element_key = key + str(flattened_list.index(element))
                    parameters.update({element_key: element})
        return parameters

    def is_json_array(self, doc_key):
        return ((type(doc_key) is list) and (doc_key) and (type(doc_key[0]) is dict))

    def build_relationships_query(self, main_type, node_type, doc_id, explicit_id):
        relationship_type = main_type + "_" + node_type
        statement = "MATCH (a:`{main_type}`), (b:`{node_type}`) WHERE a._id={{doc_id}} AND b._id ={{explicit_id}} CREATE (a)-[r:`{relationship_type}`]->(b)".format(
            main_type=main_type, node_type=node_type, relationship_type=relationship_type)
        params = {"doc_id": doc_id, "explicit_id": explicit_id}
        self.relationships_query.update({statement: params})


    def creat_relationship(id, doubanid, a):
        doubanId = "{" + "doubanId:'{}'".format(id) + "}"
        director_doubanId = "{" + "doubanId:'{}'".format(doubanid) + "}"
        statement = 'MATCH (director{a}), (actor{b}) CREATE (director)-[r:Acted_in {c}]->(actor)'.format(a=director_doubanId, b=doubanId, c=a)
        return statement