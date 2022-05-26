"""Tests for `sckg_neo4j` package."""
import unittest
from pathlib import Path

from sckg.sckg_neo4j import SoftwareKGSearcherRemote, SoftwareKGSearcherLocal
from definitions import DATA_DIR

# url, usr, pwd = 'bolt://10.176.64.33:7687', 'neo4j', 'fdsefdse'
url, usr, pwd = 'bolt://47.116.194.87:9204', 'neo4j', 'fdsefdse'
sckg_neo4j = SoftwareKGSearcherRemote(url, usr, pwd)
sckg_neo4j_local = SoftwareKGSearcherLocal(str(Path(DATA_DIR) / 'sckg.trie'))


class TestSckgNeo4j(unittest.TestCase):
    def setUp(self) -> None:
        pass

    def test_get_node_num(self):
        print(sckg_neo4j.get_node_num())

    def test_get_relation_num(self):
        print(sckg_neo4j.get_relation_num())

    def test_get_node_info_by_id(self):
        print(sckg_neo4j.get_node_info_by_id(10))
        print(sckg_neo4j.get_node_info_by_id(1375167))

    def test_get_concept_by_id(self):
        print(sckg_neo4j.get_concept_by_id(6926))
        print(sckg_neo4j.get_concept_by_id(1375167))

    def test_get_node_by_concept(self):
        print(sckg_neo4j.get_node_by_concept('vue'))
        print(sckg_neo4j.get_node_by_concept('duyi'))

    def test_get_id_by_concept(self):
        print(sckg_neo4j.get_id_by_concept('java'))
        print(sckg_neo4j.get_id_by_concept('duyi'))

    def test_get_id_by_concept_local(self):
        print(sckg_neo4j.get_concept_labels('java'))
        print(sckg_neo4j_local.get_concept_labels('duyi'))

    def test_is_exist_concept(self):
        print(sckg_neo4j.is_exist_concept('is'))
        print(sckg_neo4j.is_exist_concept('duyi'))

    def test_is_exist_concept_local(self):
        print(sckg_neo4j_local.is_exist_concept('java'))
        print(sckg_neo4j_local.is_exist_concept('duyi'))

    def test_is_exist_concept_by_id(self):
        print(sckg_neo4j.is_exist_concept_by_id(1375166))
        print(sckg_neo4j.is_exist_concept_by_id(1375167))

    def test_get_concept_score(self):
        print(sckg_neo4j.get_concept_score('cnn'))
        print(sckg_neo4j.get_concept_score('duyi'))

    def test_get_concept_pagerank_score(self):
        print(sckg_neo4j.get_concept_pagerank_score('cnn'))
        print(sckg_neo4j.get_concept_pagerank_score('duyi'))

    def test_get_concept_labels(self):
        print(sckg_neo4j.get_concept_labels('open'))
        print(sckg_neo4j.get_concept_labels('duyi'))

    def test_get_concept_labels_local(self):
        print(sckg_neo4j_local.get_concept_labels('open'))
        print(sckg_neo4j_local.get_concept_labels('duyi'))

    def test_is_action(self):
        print(sckg_neo4j.is_action('use'))

    def test_is_action_local(self):
        print(sckg_neo4j_local.is_action('use'))

    def test_is_characteristic(self):
        print(sckg_neo4j.is_characteristic('open'))

    def test_is_characteristic_local(self):
        print(sckg_neo4j_local.is_characteristic('open'))

    def test_is_concept(self):
        print(sckg_neo4j.is_concept('how'))

    def test_is_concept_local(self):
        print(sckg_neo4j_local.is_concept('how'))

    def test_get_out_relation_by_concept(self):
        print(sckg_neo4j.get_out_relation_by_concept('vuejs'))
        print(sckg_neo4j.get_out_relation_by_concept('vuejs', count=3))
        print(sckg_neo4j.get_out_relation_by_concept('duyi'))

    def test_get_out_relation_info_by_concept(self):
        # print(sckg_neo4j.get_out_relation_info_by_concept('react.js'))
        print(sckg_neo4j.get_out_relation_info_by_concept('react.js', count=3))
        print(sckg_neo4j.get_out_relation_info_by_concept('duyi'))

    def test_get_in_relation_by_concept(self):
        print(sckg_neo4j.get_in_relation_by_concept('web framework'))
        print(sckg_neo4j.get_in_relation_by_concept('web framework', count=3))
        print(sckg_neo4j.get_in_relation_by_concept('duyi'))

    def test_get_in_relation_info_by_concept(self):
        print(sckg_neo4j.get_in_relation_info_by_concept('node.js'))
        print(sckg_neo4j.get_in_relation_info_by_concept('node.js', count=3))
        print(sckg_neo4j.get_in_relation_info_by_concept('duyi'))

    def test_find_all_concept_from_sentence(self):
        print(sckg_neo4j.find_all_concept_from_sentence(
            "How can I send an email by Java application using GMail, Yahoo, or Hotmail?"))
        print(sckg_neo4j_local.find_all_concept_from_sentence(
            "How can I send an email by Java application using GMail, Yahoo, or Hotmail?"))

    def test_find_longest_valid_concept_from_sentence(self):
        print(sckg_neo4j.find_longest_valid_concept_from_sentence(
            "How can I send an email by Java application using GMail, Yahoo, or Hotmail?"))
        print(sckg_neo4j_local.find_longest_valid_concept_from_sentence(
            "How can I send an email by Java application using GMail, Yahoo, or Hotmail?"))

    def test_find_longest_valid_concept_non_stop_words_from_sentence(self):
        print(sckg_neo4j.find_longest_valid_concept_non_stop_words_from_sentence(
            "How can I get last inserted id using Hibernate"))
        # print(sckg_neo4j_local.find_longest_valid_concept_non_stop_words_from_sentence(
        #     "How can I send an email by Java application using GMail, Yahoo, or Hotmail?"))

    def test_find_longest_concept_from_sentence(self):
        print(sckg_neo4j.find_longest_concept_from_sentence(
            "How can I send an email by Java application using GMail, Yahoo, or Hotmail?"))
        print(sckg_neo4j_local.find_longest_concept_from_sentence(
            "How can I send an email by Java application using GMail, Yahoo, or Hotmail?"))

    def test_get_get_random_node(self):
        print(sckg_neo4j.get_random_node())

    def test_get_random_lastest_node(self):
        print(sckg_neo4j.get_random_lastest_node())

    def test_get_hot_concepts(self):
        print(sckg_neo4j.get_hot_concepts())

    def test_cul_in_related_node(self):
        print(sckg_neo4j.cul_in_related_node('jquery'))
        print(sckg_neo4j.cul_in_related_node('duyi'))

    def test_cul_out_related_node(self):
        print(sckg_neo4j.cul_out_related_node('jquery'))
        print(sckg_neo4j.cul_out_related_node('duyi'))

    def test_get_upper_concept(self):
        print(sckg_neo4j.get_upper_concept('jquery'))
        print(sckg_neo4j.get_upper_concept('duyi'))

    def test_get_common_upper_concept(self):
        print(sckg_neo4j.get_common_upper_concept('java', 'javascript'))
        print(sckg_neo4j.get_common_upper_concept('java', 'duyi'))

    def test_find_include_prefix_concept(self):
        print(sckg_neo4j_local.find_include_prefix_concept('java'))

    def test_find_in_is_a_relation_concept(self):
        print(sckg_neo4j.find_in_is_a_relation_concept('java'))
        print(sckg_neo4j.find_in_is_a_relation_concept('duyi'))

    def test_find_out_relation_concept(self):
        print(sckg_neo4j.find_out_is_a_relation_concept('java'))
        print(sckg_neo4j.find_out_is_a_relation_concept('duyi'))
        print(sckg_neo4j.find_out_facet_of_relation_concept('angular hint'))
        print(sckg_neo4j.find_out_facet_of_relation_concept('duyi'))

    def test_find_out_relation_concept_by_id(self):
        print(sckg_neo4j.find_out_is_a_relation_concept_by_id(5126))
        print(sckg_neo4j.find_out_is_a_relation_concept_by_id(0))
        print(sckg_neo4j.find_out_facet_of_relation_concept_by_id(211476))
        print(sckg_neo4j.find_out_facet_of_relation_concept_by_id(0))
