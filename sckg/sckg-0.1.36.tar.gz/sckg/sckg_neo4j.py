"""
-----------------------------------------
@Author: xhj
@Email: 20212010075@fudan.edu.cn
@Created: 2022/4/13
------------------------------------------
@Modify: 2022/4/13
------------------------------------------
@Description:
"""
import os
import time
from pathlib import Path
import csv
import pickle
import math
import string
import random

from py2neo import Graph
from py2neo.cypher import Cursor
from py2neo.data import Node
import en_core_web_sm
from nltk.corpus import stopwords

from definitions import DATA_DIR
from sckg.buildtrie import Buildtrim
from sckg.constant_util import ConstantUtil


class SoftwareKGSearcher:
    def __init__(self, trie_path=None):
        self.nlp = en_core_web_sm.load()
        self.stopwords = set(stopwords.words('english'))
        if trie_path:
            self.trie: Buildtrim = Buildtrim.load(trie_path)

    def __is_stop_word(self, word):
        return True if word in self.stopwords else False

    def is_exist_concept(self, concept):
        pass

    def is_concept(self, word):
        pass

    def find_all_concept_from_sentence(self, sentence):
        """
        给一段文本，返回在KG里面出现的所有概念
        """
        concepts = []
        sentence = sentence.lower().translate(str.maketrans('', '', string.punctuation)).strip("\n")
        doc = self.nlp(sentence)
        words = []
        for token in doc:
            words.append(token.lemma_)
        # words = sentence.strip("\n").lower().split()
        for i, word in enumerate(words):
            concept = word
            if i == len(words) - 1:
                break
            for j in range(i + 1, i + 5):
                if j < len(words):
                    concept += " " + words[j]
                if self.is_concept(concept):
                    concepts.append(concept)
        for word in words:
            if not self.is_concept(word):
                continue
            concepts.append(word)
        return set(concepts)

    def find_longest_valid_concept_from_sentence(self, sentence):
        """
        给一段文本，返回在KG里面出现的有效最长概念
        """
        concepts = []
        sentence = sentence.lower().translate(str.maketrans('', '', string.punctuation)).strip("\n")
        doc = self.nlp(sentence)
        words = []
        for token in doc:
            words.append(token.lemma_)
        # words = sentence.strip("\n").lower().split()
        index = 0
        while index < len(words):
            concept = words[index]
            longest_concept = concept
            for j in range(index + 1, index + 6):
                if j < len(words):
                    concept += " " + words[j]
                    if self.is_exist_concept(concept):
                        longest_concept = concept
                        index = j
                    else:
                        break
            if self.is_concept(longest_concept):
                concepts.append(longest_concept)
            index = index + 1
        return concepts

    def find_longest_valid_concept_non_stop_words_from_sentence(self, sentence):
        """
        给一段文本，返回在KG里面出现的去除停用词的有效最长概念
        """
        concepts = []
        sentence = sentence.lower().translate(str.maketrans('', '', string.punctuation)).strip("\n")
        doc = self.nlp(sentence)
        words = []
        for token in doc:
            words.append(token.lemma_)
        print(words)
        index = 0
        while index < len(words):
            concept = words[index]
            longest_concept = concept
            for j in range(index + 1, index + 6):
                if j < len(words):
                    concept += ' ' + words[j]
                    if self.is_exist_concept(concept):
                        longest_concept = concept
                        index = j
                    else:
                        break
            if self.is_concept(longest_concept) and longest_concept not in self.stopwords:
                print(longest_concept)
                concepts.append(longest_concept)
            index = index + 1
        return concepts

    def find_longest_concept_from_sentence(self, sentence):
        """
        给一段文本，返回在KG里面出现的最长概念
        """
        concepts = []
        sentence = sentence.lower().translate(str.maketrans('', '', string.punctuation)).strip("\n")
        doc = self.nlp(sentence)
        words = []
        for token in doc:
            words.append(token.lemma_)
        # words = sentence.strip("\n").lower().split()
        index = 0
        while index < len(words):
            concept = words[index]
            longest_concept = concept
            for j in range(index + 1, index + 6):
                if j < len(words):
                    concept += " " + words[j]
                    if self.is_exist_concept(concept):
                        longest_concept = concept
                        index = j
                    else:
                        break
            if self.is_concept(longest_concept):
                concepts.append((longest_concept, 'valid'))
            else:
                concepts.append((longest_concept, 'invalid'))
            index = index + 1
        return concepts

    def find_include_prefix_concept(self, concept):
        return self.trie.tree.items(prefix=concept)


class SoftwareKGSearcherRemote(SoftwareKGSearcher):
    def __init__(self, uri, user, password, trie_path=None):
        super(SoftwareKGSearcherRemote, self).__init__(trie_path)
        self.constant = ConstantUtil()
        self.graph = Graph(uri, auth=(user, password))
        self.relation_weight = self.__construct_relation_weight()
        self.nlp = en_core_web_sm.load()

    def dumps_entity2csv(self, label, properties: list, limit_size=None):
        # TODO: dump pagerank_score next
        cypher = f'"MATCH (n:{label}) RETURN labels(n) as labels, %s"' % ','.join([f'n.{_} as {_}' for _ in properties])
        if limit_size:
            cypher = f'{cypher[:-1]} LIMIT {limit_size}"'
        cypher = 'WITH ' + cypher + ' AS query\n'
        cypher += 'CALL apoc.export.csv.query(query, "%s.csv", {})\n' % label
        cypher += 'YIELD file, source, format, nodes, properties, time, rows, batchSize, batches, done\n'
        cypher += 'RETURN file, source, format, nodes, properties, time, rows, batchSize, batches, done;'
        self.graph.run(cypher)

    def dumps_entity2json(self, label, properties: list, limit_size=None):
        cypher = f'"MATCH (n:{label}) RETURN labels(n) as labels, %s"' % ','.join([f'n.{_} as {_}' for _ in properties])
        if limit_size:
            cypher = f'{cypher[:-1]} LIMIT {limit_size}"'
        cypher = 'WITH ' + cypher + ' AS query\n'
        cypher += 'CALL apoc.export.json.query(query, "%s.json", {})\n' % label
        cypher += 'YIELD file, nodes, relationships, properties, data\n'
        cypher += 'RETURN file, nodes, relationships, properties, data;'
        self.graph.run(cypher)

    @staticmethod
    def __construct_relation_weight():
        relation_weight = {}
        with open(Path(DATA_DIR) / 'new_relation_weight_10', 'r', encoding='utf-8') as rf:
            for line in rf:
                data_line = line.split(':')
                relation_weight[data_line[0]] = data_line[1]
        return relation_weight

    def get_node_num(self):
        return self.graph.run('MATCH (n) RETURN COUNT(*)').evaluate()

    def get_relation_num(self):
        return self.graph.run('MATCH P=()-->() RETURN COUNT(*)').evaluate()

    def get_node_info_by_id(self, concept_id):
        query = f'MATCH (n:entity{{id:{concept_id}}}) RETURN n.id as id, labels(n) as labels, properties(n) as properties'
        data = self.graph.run(query).data()
        if not data:
            return None
        return data[0]

    def get_concept_by_id(self, concept_id):
        query = f'MATCH (n:entity{{id:{concept_id}}}) RETURN n.concept_name'
        cursor: Cursor = self.graph.run(query)
        return cursor.evaluate()

    def get_node_by_concept(self, concept):
        query = f'MATCH (n:entity{{concept_name:{repr(concept)}}}) RETURN n.id as id, labels(n) as labels, properties(n) as properties'
        data = self.graph.run(query).data()
        if not data:
            return None
        return data[0]

    def get_id_by_concept(self, concept):
        query = f'MATCH (n:entity{{concept_name:{repr(concept)}}}) RETURN n.id'
        cursor: Cursor = self.graph.run(query)
        return cursor.evaluate()

    def is_exist_concept(self, concept):
        query = f'MATCH (n:entity{{concept_name:{repr(concept)}}}) RETURN COUNT(*)'
        return True if self.graph.run(query).evaluate() > 0 else False

    def is_exist_concept_by_id(self, concept_id):
        query = f'MATCH (n:entity{{id:{concept_id}}}) RETURN COUNT(*)'
        return True if self.graph.run(query).evaluate() > 0 else False

    def get_concept_score(self, concept):
        query = f'MATCH (n:entity{{concept_name:{repr(concept)}}}) RETURN n.score'
        return self.graph.run(query).evaluate()

    def get_concept_pagerank_score(self, concept):
        query = f'MATCH (n:entity{{concept_name:{repr(concept)}}}) RETURN n.pagerank_score'
        return self.graph.run(query).evaluate()

    def get_concept_labels(self, concept):
        query = f'MATCH (n:entity:concept{{concept_name:{repr(concept)}}}) RETURN labels(n)'
        return self.graph.run(query).evaluate()

    def is_action(self, word):
        labels = self.get_concept_labels(word)
        if not labels:
            return False
        return True if 'action' in self.get_concept_labels(word) else False

    def is_characteristic(self, word):
        labels = self.get_concept_labels(word)
        if not labels:
            return False
        return True if 'characteristic' in labels else False

    def is_concept(self, word):
        labels = self.get_concept_labels(word)
        if not labels:
            return False
        return False if 'action' in labels or 'characteristic' in labels else True

    def get_out_relation_by_concept(self, concept, rel: str = None, count: int = None):
        query = f'MATCH (n:entity{{concept_name:{repr(concept)}}})-[r]->(x) RETURN n.concept_name, type(r), x.concept_name'
        if rel:
            query = f'MATCH (n:entity{{concept_name:{repr(concept)}}})-[r:`{rel}`]->(x) RETURN n.concept_name, type(r), x.concept_name'
        if count:
            query += f' LIMIT {count}'
        cursor: Cursor = self.graph.run(query)
        return [tuple(record) for record in cursor]

    def get_out_relation_info_by_concept(self, concept, count: int = None):
        """
        返回结点的完整信息
        """
        query = f'MATCH (n:entity{{concept_name:{repr(concept)}}})-[r]->(x) RETURN n.concept_name, type(r), x'
        if count:
            query += f' LIMIT {count}'
        cursor: Cursor = self.graph.run(query)
        result = []
        for record in cursor:
            node: Node = record[2]
            result.append((
                record[0],
                record[1],
                {
                    'id': node['id'],
                    'labels': list(node.labels),
                    'properties': dict(node)
                }
            ))
        return result

    def get_in_relation_by_concept(self, concept, rel: str = None, count: int = None):
        query = f'MATCH (n:entity{{concept_name:{repr(concept)}}})<-[r]-(x) RETURN x.concept_name, type(r), n.concept_name'
        if rel:
            query = f'MATCH (n:entity{{concept_name:{repr(concept)}}})<-[r:`{rel}`]-(x) RETURN x.concept_name, type(r), n.concept_name'
        if count:
            query += f' LIMIT {count}'
        cursor: Cursor = self.graph.run(query)
        return [tuple(record) for record in cursor]

    def get_in_relation_info_by_concept(self, concept, count: int = None):
        """
        返回结点的完整信息
        """
        query = f'MATCH (n:entity{{concept_name:{repr(concept)}}})<-[r]-(x) RETURN x, type(r), n.concept_name'
        if count:
            query += f' LIMIT {count}'
        cursor: Cursor = self.graph.run(query)
        result = []
        for record in cursor:
            node: Node = record[0]
            result.append((
                {
                    'id': node['id'],
                    'labels': list(node.labels),
                    'properties': dict(node)
                },
                record[1],
                record[2]
            ))
        return result

    def is_exit_concept_in_sentence(self, concept, sentence):
        return True if concept in self.find_all_concept_from_sentence(sentence) else False

    def get_random_node(self):
        query = 'MATCH (n:entity) RETURN n.id as id, labels(n) as labels, properties(n) as properties LIMIT 50'
        cursor: Cursor = self.graph.run(query)
        return random.sample(cursor.data(), 5)

    def get_random_lastest_node(self):
        result = []
        max_num = self.get_node_num()
        count, i = 0, 0
        while count < 5:
            node_info = self.get_node_info_by_id(max_num - i)
            i += 1
            if not node_info:
                continue
            result.append(node_info)
            count += 1
        return result

    @staticmethod
    def __exceed_time(minute):
        return time.time() - os.stat(Path(DATA_DIR) / 'hot_concepts_cache.bin').st_mtime < minute * 60

    def get_hot_concepts(self):
        # result = sorted(self.concepts, key=lambda e: e['pagerank'], reverse=True)
        # return result[:10]
        if (Path(DATA_DIR) / 'hot_concepts_cache.bin').exists() and self.__exceed_time(7200):
            # print(self.__exceed_time(7200))
            with open(Path(DATA_DIR) / 'hot_concepts_cache.bin', 'rb') as rf:
                return pickle.load(rf)
        score_query = 'MATCH (n:entity) RETURN max(n.pagerank_score)'
        max_pagerank_score = self.graph.run(score_query).evaluate()
        if not max_pagerank_score:
            return None
        max_pagerank_score -= 0.01
        query = f'MATCH (n:entity) WHERE n.pagerank_score>{max_pagerank_score} RETURN n.id as id, labels(n) as labels, properties(n) as properties'
        cursor: Cursor = self.graph.run(query)
        concepts = [{
            'id': record[0],
            'pagerank': record[2]['pagerank_score'],
            'labels': record[1],
            'properties': record[2]
        } for record in cursor]
        concepts = sorted(concepts, key=lambda x: x['pagerank'], reverse=True)[:10]
        with open(Path(DATA_DIR) / 'hot_concepts_cache.bin', 'wb') as wf:
            pickle.dump(concepts, wf)
        # for concept in concepts:
        #     print(concept[2]['pagerank_score'])
        # print(concepts)
        return concepts

    # def return_hot_concepts(self):
    #     """
    #     提前运行get_hot_concept保存结果
    #     """
    #     if (Path(DATA_DIR) / 'hot_concepts_cache.bin').exists():
    #         with open(Path(DATA_DIR) / 'hot_concepts_cache.bin', 'rb') as rf:
    #             return pickle.load(rf)
    #     return self.get_hot_concepts()

    def __cul_related_node(self, relations, orig_relations) -> list:
        nodes = {}
        try:
            for index, relation_tuple in enumerate(relations):
                node = relation_tuple[0]
                relation = relation_tuple[1]
                if relation not in self.constant.relation_score:
                    # TODO relation not in relation weight
                    relation_score = 0.6 * 0.6 + float(self.relation_weight[relation])
                else:
                    relation_score = self.constant.relation_score[relation] * 0.6 + float(
                        self.relation_weight[relation]) * 0.4
                pagerank_score = node['properties']['pagerank_score']
                pagerank_score = math.log10(pagerank_score * 10000000) / math.log10(10000000.000021683)
                # NOTE: 10000000.000169972(V3.1.46)  (3.0.-10000000.000014795)
                if 'frequency' not in node['properties']:
                    frequency = 1
                else:
                    frequency = node['properties']['sum_frequency']
                frequency_score = math.log10(frequency) / math.log10(10820730)
                # NOTE: 10877974 (V3.1.46) (3.0.-  10021884)
                node_score = pagerank_score * 0.7 + frequency_score * 0.3
                sum_score = relation_score * node_score
                nodes[sum_score] = orig_relations[index]
            nodes = sorted(nodes.items(), key=lambda x: x[0], reverse=True)
            return nodes
        except KeyError:
            return []

    def cul_in_related_node(self, concept):
        in_relations = self.get_in_relation_info_by_concept(concept)
        return self.__cul_related_node([(x, r) for x, r, n in in_relations], in_relations)

    def cul_out_related_node(self, concept):
        out_relations = self.get_out_relation_info_by_concept(concept)
        return self.__cul_related_node([(x, r) for n, r, x in out_relations], out_relations)

    def get_upper_concept(self, concept):
        node = self.get_node_by_concept(concept)
        if not node:
            return []
        relations = self.get_out_relation_info_by_concept(concept)
        upper_concepts = []
        for relation in relations:
            if relation[1] == 'is a' or relation[1] == 'instance of' or relation[1] == 'subclass of':
                upper_concepts.append(relation[2])
        return upper_concepts

    def get_common_upper_concept(self, concept1, concept2):
        node1_upper_concepts = self.get_upper_concept(concept1)
        node2_upper_concepts = self.get_upper_concept(concept2)
        upper_concepts = []
        for upper_concept in node1_upper_concepts:
            if upper_concept in node2_upper_concepts:
                upper_concepts.append(upper_concept)
        return upper_concepts

    def find_in_is_a_relation_concept(self, concept):
        in_relations = self.get_in_relation_by_concept(concept, 'is a')
        return [_[0] for _ in in_relations]

    def find_out_is_a_relation_concept(self, concept):
        out_relations = self.get_out_relation_by_concept(concept, 'is a')
        return [_[2] for _ in out_relations]

    def find_out_is_a_relation_concept_by_id(self, concept_id):
        concept = self.get_concept_by_id(concept_id)
        if not concept:
            return []
        out_relations = self.get_out_relation_by_concept(concept, 'is a')
        return [_[2] for _ in out_relations]

    def find_out_facet_of_relation_concept(self, concept):
        out_relations = self.get_out_relation_by_concept(concept, 'facet of')
        return [_[2] for _ in out_relations]

    def find_out_facet_of_relation_concept_by_id(self, concept_id):
        concept = self.get_concept_by_id(concept_id)
        if not concept:
            return []
        out_relations = self.get_out_relation_by_concept(concept, 'facet of')
        return [_[2] for _ in out_relations]


class SoftwareKGSearcherLocal(SoftwareKGSearcher):
    def __init__(self, trie_path=None):
        super(SoftwareKGSearcherLocal, self).__init__(trie_path)
        self.concepts = self.__construct_concepts()

    @staticmethod
    def __construct_concepts():
        if (Path(DATA_DIR) / 'concept.bin').exists():
            with open(Path(DATA_DIR) / 'concept.bin', 'rb') as rf:
                return pickle.load(rf)
        concepts = {}
        with open(Path(DATA_DIR) / 'concept.csv', 'r', encoding='utf-8') as rf:
            reader = csv.reader(rf)
            next(reader)
            for row in reader:
                concepts[row[2]] = (row[1], row[0])
        with open(Path(DATA_DIR) / 'concept.bin', 'wb') as wf:
            pickle.dump(concepts, wf)
        return concepts

    def is_exist_concept(self, concept):
        return self.concepts.__contains__(concept)

    def get_id_by_concept(self, concept):
        if not self.is_exist_concept(concept):
            return None
        return self.concepts[concept][0]

    def get_concept_labels(self, concept):
        if not self.is_exist_concept(concept):
            return None
        return self.concepts[concept][1]

    def is_action(self, word):
        labels = self.get_concept_labels(word)
        if not labels:
            return False
        return True if 'action' in labels else False

    def is_characteristic(self, word):
        labels = self.get_concept_labels(word)
        if not labels:
            return False
        return True if 'characteristic' in labels else False

    def is_concept(self, word):
        labels = self.get_concept_labels(word)
        if not labels:
            return False
        return False if 'action' in labels or 'characteristic' in labels else True
