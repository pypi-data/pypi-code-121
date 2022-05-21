import os
import pymongo
from pymongo import MongoClient
from datetime import datetime as dt


class MongoEngine:
    '''
    This api will be built around the idea of using a selection_filter to select items in your database, a common task; \
      and using simple understandable function names to operate on the documents returned by the selection_filter

    The purpose is the convenience gained in being able to just say <MongoEngine instance>.remove_key(selection_filter, key) without \
      having to know the weird intricate syntax for simple, common operations

    Names therefore will try to make as much sense as possible (obviously); Coming from my own perspective (which may at any time be ignorant/incomplete)

    Methods will also generally all have a <how_many> parameter, in order to specify if you wish to perform on only one or all \
      of the documents found by the selection_filter

      Perhaps a usage for adding support for n number of documents will present itself but for now \
        one or all seems like the most used cases

    Philosophy will generally be to make easy those functions that are commonplace, and then to not \
      weigh down the software with excessive wrapping of rare usage functionality.

      Use the simple examples and their syntax as documentation for more complex, specialized requirements
    '''

    def __init__(
        self, db='events', collection='events',
            host="mongodb://localhost:27017"):


        try:
            self.client = MongoClient(host)
        except Exception as e:
            print(e)

        self.db = self.client[db]
        if collection:
            self.collection = self.db[collection]
        else:
            self.collection = None

    @classmethod
    def establish_connection(cls, host):
        return cls(host=host)

    @property
    def collection_size(self):
        return self.collection.count_documents({})

    def set_collection(self, new_coll):
        self.collection = self.db[new_coll]

    def set_db(self, new_db, new_coll=None, ignore_coll=False):
        self.db = self.client[new_db]
        if new_coll == None and ignore_coll == False:
            self.collection = self.db[input(
                'Please enter a collection name you wish to access in this db: ')]
        elif ignore_coll == True:
            pass
        else:
            self.collection = self.db[new_coll]
        print(self.__repr__())

    def retrieve_all_from_coll(self):
        return list(self.collection.find())

    def filter_date_range(start_date, end_date):
        pass

    def filter_by_mongo_args(self, *args):
        self.collection.find(args)

    def add_entry(self, json, last_updated=True):
        if last_updated:
            json.update({'last_updated': dt.utcnow()})
        return self.collection.insert_one(json)

    def update_specific_value(self, key, value, new_value, how_many='all'):
        '''
        DISCLAIMER: This function does NOT use selection_filter general syntax because we are looking at a specific key \
          and its more explicit what we're doing this way

        By default, finds all with {<key>: <value>} in the document and updates the key with the <new_value>

        how many supports one or all, where one would indicate the first one found matching the key value pair
        '''
        if how_many == 'all':
            self.collection.update_many(
                {key: value},
                {'$set': {key: new_value}})
        elif how_many == 'one':
            self.collection.find_one_and_update(
                {key: value}, {'$set': {key: new_value}})

    def update_value(self, selection_filter, key, value, how_many='all'):
        if how_many == 'all':
            self.collection.update_many(
                selection_filter, {'$set': {key, value}})
        elif how_many == 'one':
            self.collection.find_one_and_update(
                selection_filter, {'$set': {key: value}})

    def remove_key(self, selection_filter, key, how_many='all'):
        '''Removes key from document(s) matching selection_filter'''
        if how_many == 'all':
            self.collection.update_many(
                selection_filter, {'$unset': {key: ''}})
        elif how_many == 'one':
            self.collection.find_one_and_update(
                selection_filter, {'$unset': {key: ''}})

    def remove_all(self, json):
        self.collection.delete_many(json)

    def delete_one(self, dict_):
        self.collection.delete_one(dict_)

    def sort_by(self, *args):
        return list(self.collection.find({}).sort(*args))

    def collection_length(self):
        return self.collection.count()

    def first_empty_id(self, i=0):
        while i < self.collection_length():
            if self.collection.find({'id': i}) == None:
                return i
            i += 1
        return i

    def get_every_key_in_collection(self):
        keys = []
        for obj in list(self.collection.find()):
            for key in obj.keys():
                if key not in keys:
                    keys.append(key)

        # keys = [key for key not in obj.keys() for obj in list(self.collection.find())]

        return keys

    def delete_collection(self, collection):
        verify = input(
            'Input collection name if you are sure you wish to delete this collection: ')
        if verify == collection:
            self.db[collection].drop()

    def __repr__(self):
        return f"Database: {self.db.name}; Collection: {self.collection.name}"

    def __str__(self):
        return f"Database: {self.db.name}; Collection: {self.collection.name}"
