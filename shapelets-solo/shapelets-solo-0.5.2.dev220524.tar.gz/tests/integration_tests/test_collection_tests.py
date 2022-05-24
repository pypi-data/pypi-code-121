# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

import unittest

from shapelets import init_session
from shapelets.model import Collection, CollectionType


class CollectionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._client = init_session("admin", "admin", "https://127.0.0.1")
        cls._collection = cls._client.create_collection(
            "MyInitialCollection",
            "Initial collection",
            ['Malaga', 'day-time', 'detach-house'],
            CollectionType.ENERGY)

    def test_get_collections(self):
        collections = self._client.get_collections()
        self.assertGreater(len(collections), 1)

    def test_create_collection(self):
        collection = CollectionTest._client.create_collection(
            name="MyCollection2",
            description="This collection keeps data from smart meters from Malaga",
            tags=['Malaga', 'day-time', 'detach-house'],
            collection_type=CollectionType.ENERGY)
        self.assertIsInstance(collection, Collection)

    def test_get_collection(self):
        col_id = CollectionTest._collection.collection_id
        collection = CollectionTest._client.get_collection(col_id)
        self.assertIsInstance(collection, Collection)

    def test_update_collection(self):
        collection = CollectionTest._client.update_collection(
            CollectionTest._collection,
            name="MyDerivateCollection",
            description="Collection of derivates from Malaga",
            tags=["tag0", "tag1"])
        self.assertEqual(collection.name, "MyDerivateCollection")
        self.assertEqual(collection.description, "Collection of derivates from Malaga")
        self.assertCountEqual(collection.tags, ["tag0", "tag1"])

    def test_get_collection_sequences(self):
        sequences = CollectionTest._client.get_collection_sequences(CollectionTest._collection)
        self.assertEqual(len(sequences), 0)

    def test_get_collection_types(self):
        collection_types = CollectionTest._client.get_collection_types()

        self.assertEqual(len(collection_types), 4)

    def test_delete_collection(self):
        collection = CollectionTest._client.create_collection(
            name="MyCollection2",
            description="This collection keeps data from smart meters from Malaga",
            tags=['Malaga', 'day-time', 'detach-house'],
            collection_type=CollectionType.ENERGY)
        result = CollectionTest._client.delete_collection(collection)
        self.assertTrue(result)
