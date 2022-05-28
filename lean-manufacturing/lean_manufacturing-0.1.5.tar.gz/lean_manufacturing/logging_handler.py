import logging
from datetime import datetime

import pymongo

localdb = pymongo.MongoClient('mongodb://localhost:27017')

class _MongoHandler(logging.Handler):
    def __init__(self, level=logging.NOTSET, database='monitor', collection='logs', capped=True, size=100000, drop=False):
        logging.Handler.__init__(self, level)

        self.database                   = localdb[database]

        if collection in self.database.list_collection_names():
            if drop:
                self.database.drop_collection(collection)
                self.collection         = self.database.create_collection(collection, **{'capped': capped, 'size': size})
            else:
                self.collection         = self.database[collection]
        else:
            self.collection             = self.database.create_collection(collection, **{'capped': capped, 'size': size})

    def emit(self, record):
        log_content = {'when': datetime.now(),
                    'levelno': record.levelno,
                    'levelname': record.levelname,
                    'collection': getattr(record, 'collection', None),
                    'message': record.msg}
        self.collection.insert_one(log_content)
        print('{when} - {levelname} - {collection} - {message}'.format(**log_content))