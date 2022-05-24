# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

import unittest
import uuid

from shapelets.dsl import ArgumentType, ArgumentTypeEnum, ArgumentValue
from shapelets.dsl import Node, SourceNode


class GraphNodesTest(unittest.TestCase):

    def test_node_hash_eq(self):
        node1 = Node("sum_two_numbers")
        node1.node_id = uuid.NAMESPACE_DNS
        node2 = Node("")
        node2.node_id = uuid.NAMESPACE_URL
        nodes = {
            node1: "sum_two_numbers",
            node2: "fibonacci"
        }
        self.assertEqual(nodes[node1], "sum_two_numbers")
        self.assertEqual(nodes[node2], "fibonacci")
        self.assertIsNone(nodes.get(Node("fibonacci")))

    def test_node_to_dict(self):
        node = Node("brew_some_coffee")
        node.node_id = uuid.NAMESPACE_DNS
        expected = {
            "id": str(node.node_id),
            "operation": node.operation
        }
        self.assertEqual(expected, node.to_dict())

    def test_node_from_dict(self):
        node = {
            "id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
            "operation": "brew_some_coffee"
        }
        expected = Node("brew_some_coffee")
        expected.node_id = uuid.NAMESPACE_DNS
        self.assertEqual(expected, Node.from_dict(node))

    def test_source_node_hash_eq(self):
        node1 = SourceNode(ArgumentValue(ArgumentType(ArgumentTypeEnum.STRING), "Alberto"))
        node1.id = uuid.NAMESPACE_DNS
        node2 = SourceNode(ArgumentValue(ArgumentType(ArgumentTypeEnum.INT), 25))
        node2.id = uuid.NAMESPACE_URL
        nodes = {
            node1: "username",
            node2: "age"
        }
        self.assertEqual(nodes[node1], "username")
        self.assertEqual(nodes[node2], "age")
        self.assertIsNone(nodes.get(Node("age")))

    def test_source_node_to_dict(self):
        node = SourceNode(ArgumentValue(ArgumentType(ArgumentTypeEnum.STRING), "Alberto"))
        node.node_id = uuid.NAMESPACE_DNS
        expected = {
            "id": str(node.node_id),
            "operation": SourceNode.OPERATION,
            "value": {
                "type": ArgumentTypeEnum.STRING.value,
                "string": "Alberto"
            }
        }
        self.assertEqual(expected, node.to_dict())
