# -*- coding: utf-8 -*-
# @Time    : 2022/4/25 下午1:00
# @Author  : kyq
# @Software: PyCharm

# id = "1234565"
# type = "{" + "type:'{}'".format(str(1)) + "}"
# doubanId = '{' + "doubanId:'{}'".format(id) + "}"
# m = "{" + "doubanId:'456736436'" + "}"
# statement = "MATCH (director:Director{a}), (actor:Actor{b}) CREATE (actor)-[r:Acted_in {c}]->(director)".format(a=m,b=doubanId,c=type)
# print(statement)
#
from py2neo import Graph
#
graph = Graph('http://192.168.3.215:7474/db/data')
# # statement =""
# tx = graph.begin()
# m = "{post:'导演'}"
# n = "{post:'演员'}"
# a = "{type:'0'}"
# tx.commit()
# statement = 'MATCH (director:Director{post:"导演"}), (actor:Actor{post:"演员"}) WHERE director._id="1234564" AND actor._id ="1234564"  CREATE  (actor)-[r:Acted_in {type:"0"}]->(director)'
# statement = 'MATCH (director{doubanId:"456736436"}), (actor{doubanId:"1234565"}) CREATE (actor)-[r:Acted_in {type:"1"}]->(director)'
# statement = "MATCH (director:Director{}), (actor:Actor{}) CREATE  (actor)-[r:Acted_in {}]->(director)".format(m,n,a)
# print(statement)
# tx.run(cypher=statement)
# tx.commit()


# def format_document(self, document):
#     def _kernel(doc):
#         for key in doc:
#             value = doc[key]
#             for new_k, new_v in self.transform_element(key, value):
#                 yield new_k, new_v
#
#     return dict(_kernel(document))


# statement = 'MATCH (n{doubanId:"1322934"}),(n1{doubanId:"1275687"}), p=(n)-[r:Director_Actor]-(n1) return r.count'
# ret = graph.begin().run(statement).data()[0]['r.count']
# print(ret)
# a = [1,2,3,4,5,6]
from mongo_connector.doc_managers.new_neo4j_doc_manager import DocManager