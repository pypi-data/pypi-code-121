# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

import unittest
import uuid

from shapelets.dsl import Connection


class ConnectionTest(unittest.TestCase):

    def test_connection_hash_eq(self):
        connection1 = Connection(uuid.NAMESPACE_DNS, "a_connector", "parent_connector", 11)
        connection2 = Connection(uuid.NAMESPACE_URL, "b_connector")
        connections = {
            connection1: "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
            connection2: "6ba7b811-9dad-11d1-80b4-00c04fd430c8"
        }
        self.assertEqual(connections[connection1], "6ba7b810-9dad-11d1-80b4-00c04fd430c8")
        self.assertEqual(connections[connection2], "6ba7b811-9dad-11d1-80b4-00c04fd430c8")
        connection = Connection(uuid.NAMESPACE_DNS, "a_connector")
        retrieved_connection = connections.get(connection)
        self.assertIsNone(retrieved_connection)

    def test_connection_to_dict(self):
        connection = Connection(uuid.NAMESPACE_DNS, "a_connector", "parent_connector", 11)
        expected = {
            "node_id": str(connection.node_id),
            "connector_id": {
                "id": connection.connector_name,
                "parent_connector_id": connection.parent_connector_name,
                "param_index": connection.param_index
            }
        }
        self.assertEqual(expected, connection.to_dict())

    def test_connection_from_dict(self):
        connection = {
            "node_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
            "connector_id": {
                "id": "a_connector",
                "parent_connector_id": "parent_connector",
                "param_index": 11
            }
        }
        expected = Connection(uuid.NAMESPACE_DNS, "a_connector", "parent_connector", 11)
        self.assertEqual(expected, Connection.from_dict(connection))
