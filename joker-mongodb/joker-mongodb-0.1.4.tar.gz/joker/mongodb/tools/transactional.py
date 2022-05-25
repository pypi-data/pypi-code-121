#!/usr/bin/env python3
# coding: utf-8

import datetime

import pymongo.errors
from pymongo import ReturnDocument
from pymongo.collection import Collection


class TransactionHelper:
    def __init__(self, coll: Collection):
        self.coll = coll

    def lock(self, name: str, ttl: int = 60):
        now = datetime.datetime.now()
        expire_at = now + datetime.timedelta(seconds=ttl)
        self.coll.delete_many(
            {'expire_at': {'$lt': now}, 'type': 'lock'},
        )
        record = {
            '_id': name,
            'type': 'lock',
            'expire_at': expire_at,
        }
        try:
            self.coll.insert_one(record)
        except pymongo.errors.DuplicateKeyError:
            return False
        return True

    def unlock(self, name: str):
        self.coll.delete_one({'_id': name, 'type': 'lock'})

    def get_next_serial_code(self, prefix='ID', length=6):
        doc = self.coll.find_one_and_update(
            {'_id': prefix, 'type': 'serial'},
            {'$inc': {'i': 1}},
            upsert=True, return_document=ReturnDocument.AFTER,
        )
        return prefix + str(doc['i']).zfill(length)
