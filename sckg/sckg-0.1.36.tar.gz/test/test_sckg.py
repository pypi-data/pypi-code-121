#!/usr/bin/env python

"""Tests for `sckg` package."""
import unittest

from click.testing import CliRunner
from kgdt.models.graph import GraphData

from sckg import sckg_neo4j
from sckg import cli
from sckg.graph import SoftwareKG
from util.path_util import PathUtil


class TestSckg(unittest.TestCase):
    """Tests for `sckg` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_something(self):
        """Test something."""

    def test_command_line_interface(self):
        """Test the CLI."""
        runner = CliRunner()
        result = runner.invoke(cli.main)
        assert result.exit_code == 0
        assert 'sckg.cli.main' in result.output
        help_result = runner.invoke(cli.main, ['--help'])
        assert help_result.exit_code == 0
        assert '--help  Show this message and exit.' in help_result.output

    def test_get_node_info_by_id(self):
        graph_path = PathUtil.graph_data("KG", "test")
        tree = PathUtil.trie("Trie", "V1.0.2")
        sckg = SoftwareKG(graph_path, tree)
        print(sckg.get_node_info_by_id(27))

    def test_is_exit_facet_of_relation(self):
        graph_path = PathUtil.graph_data("KG", "test")
        tree = PathUtil.trie("Trie", "V1.0.2")
        sckg = SoftwareKG(graph_path, tree)
        assert sckg.is_exit_facet_of_relation("java", "java jdk") == True

    def test_is_exit_relation(self):
        graph_path = PathUtil.graph_data("KG", "test")
        tree = PathUtil.trie("Trie", "V1.0.2")
        sckg = SoftwareKG(graph_path, tree)
        assert sckg.is_exit_relation("java", "java jdk") == True

    def test_is_exit_concept(self):
        graph_path = PathUtil.graph_data("KG", "test")
        tree = PathUtil.trie("Trie", "V1.0.2")
        sckg = SoftwareKG(graph_path, tree)
        assert sckg.is_exist_concept("java") == True

    def test_get_node_by_concept(self):
        graph_path = PathUtil.graph_data("KG", "V1.0.6")
        tree = PathUtil.trie("Trie", "V1.0.7")
        sckg = SoftwareKG(graph_path, tree)
        print(sckg.get_node_by_concept("java"))

    def test_is_characteristic(self):
        graph_path = PathUtil.graph_data("KG", "V1.1.0")
        tree = PathUtil.trie("Trie", "V1.0.7")
        sckg = SoftwareKG(graph_path, tree)
        print(sckg.is_characteristic("proceed"))

    def test_get_in_relations(self):
        graph_path = PathUtil.graph_data("KG", "V1.0.6")
        tree = PathUtil.trie("Trie", "V1.0.7")
        sckg = SoftwareKG(graph_path, tree)
        print(sckg.get_in_relations("java"))

    def test_get_out_relations(self):
        graph_path = PathUtil.graph_data("KG", "V1.0.6")
        tree = PathUtil.trie("Trie", "V1.0.7")
        sckg = SoftwareKG(graph_path, tree)
        print(sckg.get_out_relations("java"))

    def test_get_concept_by_id(self):
        graph_path = PathUtil.graph_data("KG", "test")
        tree = PathUtil.trie("Trie", "V1.0.2")
        sckg = SoftwareKG(graph_path, tree)
        print(sckg.get_concept_by_id(2))

    def test_find_common_out_relationship_node(self):
        graph_path = PathUtil.graph_data("KG", "test")
        tree = PathUtil.trie("Trie", "V1.0.2")
        sckg = SoftwareKG(graph_path, tree)
        print(sckg.find_common_out_relationship_node("java jdk", "java ee"))

    def test_find_out_is_a_relation_concept(self):
        graph_path = PathUtil.graph_data("KG", "test")
        tree = PathUtil.trie("Trie", "V1.0.2")
        sckg = SoftwareKG(graph_path, tree)
        print(sckg.find_out_is_a_relation_concept("java"))

    def test_find_in_is_a_relation_concept(self):
        graph_path = PathUtil.graph_data("KG", "V2.9.6")
        tree = PathUtil.trie("Trie", "V1.0.4")
        sckg = SoftwareKG(graph_path, tree)
        print(sckg.find_in_is_a_relation_concept("java"))

    def test_find_common_in_relationship_node(self):
        graph_path = PathUtil.graph_data("KG", "test")
        tree = PathUtil.trie("Trie", "V1.0.2")
        sckg = SoftwareKG(graph_path, tree)
        print(sckg.find_common_in_relationship_node("java", "java jdk"))

    def test_find_include_prefix_concept(self):
        graph_path = PathUtil.graph_data("KG", "test")
        tree = PathUtil.trie("Trie", "V1.0.2")
        sckg = SoftwareKG(graph_path, tree)
        print(sckg.find_include_prefix_concept("java"))

    def test_find_longest_concept_from_sentence(self):
        graph_path = PathUtil.graph_data("KG", "V1.1.0")
        tree = PathUtil.trie("Trie", "V1.0.10")
        sckg = SoftwareKG(graph_path, tree)
        # print(sckg.find_longest_concept_from_sentence("golog is a high-level agent programming language based on prolo"))
        print(sckg.find_longest_concept_from_sentence('Now, I personally have no idea what this _OE_SOCKETS is actually for, so if any z/OS sockets programmers are out there (all 3 of you), perhaps you could give me a rundown of how this all works?'))

    def test_find_longest_valid_concept_from_sentence(self):
        graph_path = PathUtil.graph_data("KG", "V1.0.8")
        tree = PathUtil.trie("Trie", "V1.0.10")
        sckg = SoftwareKG(graph_path, tree)
        # print(sckg.find_longest_concept_from_sentence("golog is a high-level agent programming language based on prolo"))
        print(sckg.find_longest_valid_concept_from_sentence('Now, I personally have no idea what this _OE_SOCKETS is actually for, so if any z/OS sockets programmers are out there (all 3 of you), perhaps you could give me a rundown of how this all works?'))


    def test_find_all_concept_from_sentence(self):
        graph_path = PathUtil.graph_data("KG", "V1.0.6")
        tree = PathUtil.trie("Trie", "V1.0.7")
        sckg = SoftwareKG(graph_path, tree)
        print(sckg.find_all_concept_from_sentence("a cloud-native programming language"))
        print(sckg.find_all_concept_from_sentence("Node.js is an event-based, non-blocking, asynchronous I/O runtime that uses Google's V8 JavaScript engine and libuv library"))
        # print(sckg.find_all_concept_from_sentence("Is it possible to use private field conventions for Fluent NHibernate Automapping?"))

    def test_get_all_concept(self):
        graph_path = PathUtil.graph_data("KG", "test")
        tree = PathUtil.trie("Trie", "V1.0.2")
        sckg = SoftwareKG(graph_path, tree)
        print(sckg.get_all_concept())

    def test_get_upper_concept(self):
        graph_path = PathUtil.graph_data("KG", "test")
        tree = PathUtil.trie("Trie", "V1.0.2")
        sckg = SoftwareKG(graph_path, tree)
        print(sckg.get_upper_concept("java"))

    def test_get_nums(self):
        graph_path = PathUtil.graph_data("KG", "test")
        self.graph: GraphData = GraphData.load(graph_path)

        print(self.graph.get_node_num())

    def test_get_common_upper_concept(self):
        graph_path = PathUtil.graph_data("KG", "test")
        tree = PathUtil.trie("Trie", "V1.0.2")
        sckg = SoftwareKG(graph_path, tree)
        print(sckg.get_common_upper_concept("java", 'python'))

    def test_get_random_node(self):
        graph_path = PathUtil.graph_data("KG", "V1.0.6")
        tree = PathUtil.trie("Trie", "V1.0.7")
        sckg = SoftwareKG(graph_path, tree)
        print(sckg.get_random_node())

    def test_get_hot_concept(self):
        graph_path = PathUtil.graph_data("KG", "V3.0.30")
        tree = PathUtil.trie("Trie", "V3.0.16")
        sckg = SoftwareKG(graph_path, tree)
        a=sckg.get_hot_concepts()
        print(a)

    def test_get_random_lasted_node(self):
        graph_path = PathUtil.graph_data("KG", "V2.0.0")
        tree = PathUtil.trie("Trie", "V2.0.0")
        sckg = SoftwareKG(graph_path, tree)
        print(sckg.get_random_lastest_node())

    def test_is_exit_concept_in_sentence(self):
        graph_path = PathUtil.graph_data("KG", "V1.0.6")
        tree = PathUtil.trie("Trie", "V1.0.7")
        sckg = SoftwareKG(graph_path, tree)
        print(sckg.is_exit_concept_in_sentence('programming language','dynamically and strongly typed programming language'))

    def test_find_out_is_a_relation_concept_by_id(self):
        graph_path = PathUtil.graph_data("KG", "V1.0.8")
        tree = PathUtil.trie("Trie", "V1.0.9")
        sckg = SoftwareKG(graph_path, tree)
        print(sckg.find_out_is_a_relation_concept_by_id(5817))

    def test_get_node_num(self):
        graph_path = PathUtil.graph_data("KG", "V1.0.6")
        tree = PathUtil.trie("Trie", "V1.0.7")
        sckg = SoftwareKG(graph_path, tree)
        print(sckg.get_node_num())

    def test_get_relation_num(self):
        graph_path = PathUtil.graph_data("KG", "V1.0.6")
        tree = PathUtil.trie("Trie", "V1.0.7")
        sckg = SoftwareKG(graph_path, tree)
        print(sckg.get_relation_num())

    def test_get_sum_pagerank_score(self):
        graph_path = PathUtil.graph_data("KG", "V3.0.30")
        tree = PathUtil.trie("Trie", "V3.0.30")
        sckg = SoftwareKG(graph_path, tree)
        print(sckg.get_sum_pagerank_score())
        print(sckg.get_sum_frequency())

    def test_cul_out_related_node(self):
        graph_path = PathUtil.graph_data("KG", "V3.0.25")
        tree = PathUtil.trie("Trie", "V3.0.16")
        sckg = SoftwareKG(graph_path, tree)
        print(sckg.cul_out_related_node('transformer'))

    def test_cul_in_related_node(self):
        graph_path = PathUtil.graph_data("KG", "V3.1.68")
        tree = PathUtil.trie("Trie", "V3.1.4")
        sckg = SoftwareKG(graph_path, tree)
        # print(sckg.cul_in_related_node('tensorflow'))
        print(sckg.cul_out_related_node('jquery'))
        # # print('--------')
        # print(sckg.cul_in_related_node('transformer'))
        # print(sckg.cul_out_related_node('transformer'))
        # print('------')
        # print(sckg.cul_in_related_node('rnn'))
        # print(sckg.cul_out_related_node('rnn'))
        # print('------')
        # print(sckg.cul_in_related_node('cnn'))
        # print(sckg.cul_out_related_node('cnn'))
        # print('------')
        # print(sckg.cul_in_related_node('programming language'))
        # print(sckg.cul_out_related_node('programming language'))
        # print("==============")
        # print(sckg.get_sum_pagerank_score())
        # print(sckg.get_sum_frequency())
        # for a in sckg.get_hot_concepts():
        #     print(a)

