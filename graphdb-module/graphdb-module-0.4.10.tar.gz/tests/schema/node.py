import unittest

from graphdb.schema import Node


class TestNode(unittest.TestCase):

    def setUp(self) -> None:
        self.node_without_prop = {"label": "Person"}
        self.node_with_prop = {"label": "Person", "properties": {
            "name": "Dann",
            "job": "developer"
        }}
        self.node_without_label = {"properties": {
            "name": "Ann",
            "job": "system engineer"
        }}

    def test_create_node_without_prop(self):
        """Test create new node with property
        :return: none
        """
        node = Node(**self.node_without_prop)
        self.assertEqual(node.label, self.node_without_prop["label"])

    def test_create_node_with_prop(self):
        """Test create new node with property
        :return: none
        """
        node = Node(**self.node_with_prop)
        self.assertEqual(node.label, self.node_with_prop["label"])
        self.assertEqual(node.properties, self.node_with_prop["properties"])

    def test_create_node_without_label(self):
        """This will throw an error when try to build node without label
        :return: none
        """
        with self.assertRaises(Exception):
            Node(**self.node_without_label)
