"""
MongoDB Module for accessing MongoDB Atlas server via AWS IAM.
"""


from urllib.parse import quote_plus
from pymongo import MongoClient
import time


class Mongo:
    def __init__(
        self,
        aws_access_key_id,
        aws_secret_access_key,
        mongo_cluster,
        max_pool_size=64,
        **kwargs,
    ):
        access_key_id = quote_plus(aws_access_key_id)
        secret_access_key = quote_plus(aws_secret_access_key)
        cluster = quote_plus(mongo_cluster)

        uri = (
            "mongodb+srv://%s:%s@%s/"
            % (
                access_key_id,
                secret_access_key,
                cluster,
            )
            + "?authSource=$external"
            + "&authMechanism=MONGODB-AWS"
            + "&retryWrites=true"
            + "&w=majority"
            + "&readConcernLevel=majority"
            + "&readPreference=secondaryPreferred"
        )

        try:
            self.client = MongoClient(uri, maxPoolSize=max_pool_size, **kwargs)
        except Exception as err:
            raise Exception("ERROR - Connection to MongoClient:", err)

    def create_database(self, database_name):
        try:
            db_list = self.client.list_database_names()
            if database_name not in db_list:
                self.client[database_name]
                print(f"Database '{database_name}' created..")
                print("List of databases:", self.client.list_database_names())
            else:
                print(f"Database '{database_name}' already existing..")
        except Exception as err:
            raise Exception("ERROR - Creating DB to MongoClient:", err)

    def create_collection(self, database, collection_name):
        try:
            db = self.client[database]
            col_list = db.list_collection_names()
            if collection_name not in col_list:
                db[collection_name]
                print(f"Collection '{collection_name}' in '{database}' created..")
                print(f"List of '{database}' collections: {db.list_collection_names()}")
            else:
                print(
                    f"Collection '{collection_name}' already existing in '{database}'.."
                )
        except Exception as err:
            raise Exception("ERROR - Creating DB to MongoClient:", err)

    def insert_items(self, database, collection, queries):
        try:
            # Modify queries to add created_at and updated_at
            for query in queries:
                query["created_at"] = int(time.time())
                query["updated_at"] = int(time.time())

            writer = self.client[database][collection]
            result = writer.insert_many(queries)
            # print(f"Successfully inserted {len(queries)} documents to '{database}'-'{collection}'")
            return result.inserted_ids
        except Exception as err:
            raise Exception("ERROR - Inserting to MongoClient:", err)

    def insert_item(self, database, collection, query):
        try:
            # Add datetime
            query["created_at"] = int(time.time())
            query["updated_at"] = int(time.time())

            writer = self.client[database][collection]
            result = writer.insert_one(query)
            # print(f"Successfully inserted document to '{database}'-'{collection}'")
            return result.inserted_id
        except Exception as err:
            raise Exception("ERROR - Inserting to MongoClient:", err)

    def get_items(self, database, collection, query=None):
        try:
            reader = self.client[database][collection]
            docs = []
            for doc in reader.find(query):
                docs.append(doc)
            return docs
        except Exception as err:
            raise Exception("ERROR - Getting items from MongoClient:", err)

    def update_item(self, database, collection, id, value):
        try:
            value["updated_at"] = int(time.time())
            selected_collection = self.client[database][collection]
            selected_collection.update_one({"_id": id}, {"$set": value})
        except Exception as err:
            raise Exception("ERROR - Updating item in MongoClient:", err)

    def remove_item(self, database, collection, id):
        try:
            selected_collection = self.client[database][collection]
            selected_collection.delete_one({"_id": id})
        except Exception as err:
            raise Exception("ERROR - Delete item in MongoClient:", err)
