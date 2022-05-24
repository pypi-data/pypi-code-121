# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

import unittest

from shapelets.dsl import ArgumentType, ArgumentTypeEnum
from shapelets.dsl import Connector


class ConnectorTest(unittest.TestCase):

    def test_connector_hash_eq(self):
        connector1 = Connector("lint", ArgumentType(ArgumentTypeEnum.LIST, ArgumentTypeEnum.INT))
        connector2 = Connector("text", ArgumentType(ArgumentTypeEnum.STRING))
        connectors = {
            connector1: "lint",
            connector2: "text"
        }
        self.assertEqual(connectors[connector1], "lint")
        self.assertEqual(connectors[connector2], "text")
        connector = Connector("lint", ArgumentType(ArgumentTypeEnum.INT))
        retrieved_connector = connectors.get(connector)
        self.assertIsNone(retrieved_connector)

    def test_connector_to_dict(self):
        connector = Connector("lint", ArgumentType(ArgumentTypeEnum.LIST, ArgumentTypeEnum.INT))
        expected = {
            "name": connector.connector_name,
            "type": connector.connector_type.get_all_values()
        }
        self.assertEqual(expected, connector.to_dict())

    def test_connector_from_dict(self):
        connector = {
            "name": "lint",
            "type": "ARGUMENT_LIST:INTEGER"
        }
        expected = Connector("lint", ArgumentType(ArgumentTypeEnum.LIST, ArgumentTypeEnum.INT))
        self.assertEqual(expected, Connector.from_dict(connector))
