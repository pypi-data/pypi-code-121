# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

import unittest
import uuid

from shapelets.dsl import Link, Connection


class LinkTest(unittest.TestCase):

    def test_link_hash_eq(self):
        link1 = Link(
            Connection(uuid.NAMESPACE_DNS, "a_connector", "parent_connector", 11),
            Connection(uuid.NAMESPACE_URL, "b_connector"))
        link1.link_id = uuid.NAMESPACE_DNS
        link2 = Link(
            Connection(uuid.NAMESPACE_DNS, "b_connector"),
            Connection(uuid.NAMESPACE_URL, "a_connector", "parent_connector", 11))
        link2.link_id = uuid.NAMESPACE_URL
        links = {
            link1: "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
            link2: "6ba7b811-9dad-11d1-80b4-00c04fd430c8"
        }
        self.assertEqual(links[link1], "6ba7b810-9dad-11d1-80b4-00c04fd430c8")
        self.assertEqual(links[link2], "6ba7b811-9dad-11d1-80b4-00c04fd430c8")
        link = Link(
            Connection(uuid.NAMESPACE_URL, "a_connector"),
            Connection(uuid.NAMESPACE_DNS, "b_connector"))
        self.assertIsNone(links.get(link))

    def test_link_to_dict(self):
        link = Link(
            Connection(uuid.NAMESPACE_URL, "a_connector"),
            Connection(uuid.NAMESPACE_DNS, "b_connector")
        )
        link.link_id = uuid.NAMESPACE_URL
        expected = {
            "id": str(link.link_id),
            "source": link.source.to_dict() if link.source else None,
            "destination": link.destination.to_dict() if link.destination else None
        }
        self.assertEqual(expected, link.to_dict())

    def test_link_from_dict(self):
        link = {
            'id': '6ba7b811-9dad-11d1-80b4-00c04fd430c8',
            'source': {
                'node_id': '6ba7b811-9dad-11d1-80b4-00c04fd430c8',
                'connector_id': {
                    'id': 'a_connector',
                    'parent_connector_id': None,
                    'param_index': None}
            },
            'destination': {
                'node_id': '6ba7b810-9dad-11d1-80b4-00c04fd430c8',
                'connector_id': {
                    'id': 'b_connector',
                    'parent_connector_id': None,
                    'param_index': None
                }
            }
        }
        expected = Link(
            Connection(uuid.NAMESPACE_URL, "a_connector"),
            Connection(uuid.NAMESPACE_DNS, "b_connector")
        )
        expected.link_id = uuid.NAMESPACE_URL
        self.assertEqual(expected, Link.from_dict(link))
