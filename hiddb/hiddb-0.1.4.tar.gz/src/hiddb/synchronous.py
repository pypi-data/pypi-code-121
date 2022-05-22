import asyncio
import hiddb.asynchronous


def sync(async_func):
    return asyncio.run(async_func)

class HIDDB:
    def __init__(self, key: str, secret: str):
        self.hiddb = sync(hiddb.asynchronous.HIDDB.create(key, secret))

    def check_health(self):
        return sync(self.hiddb.check_health())

    def create_database(self, database_name: str):
        return sync(self.hiddb.create_database(database_name))

    def list_databases(self):
        return sync(self.hiddb.list_databases())

    def get_database(self, database_id: str):
        return sync(self.hiddb.get_database(database_id))

    def delete_database(self, database_id: str):
        return sync(self.hiddb.delete_database(database_id))

    def create_instance(self, database_id: str, type: str, volume_size: str):
        return sync(self.hiddb.create_instance(database_id, type, volume_size))

    def get_instances(self):
        return sync(self.hiddb.get_instances())

    def get_instance(self, instance_id: str):
        return sync(self.hiddb.get_instance(instance_id))

    def delete_instance(self, instance_id: str):
        return sync(self.hiddb.delete_instance(instance_id))

    def create_collection(self, database_id: str, collection_name: str):
        return sync(self.hiddb.create_collection(database_id, collection_name))

    def list_collections(self, database_id: str):
        return sync(self.hiddb.list_collections(database_id))

    def get_collection(self, database_id: str, collection_name: str):
        return sync(self.hiddb.get_collection(database_id, collection_name))

    def delete_collection(self, database_id: str, collection_name: str):
        return sync(self.hiddb.delete_collection(database_id, collection_name))

    def create_index(self, database_id: str, collection_name: str, field_name: str, dimension: int):
        return sync(self.hiddb.create_index(database_id, collection_name, field_name, dimension))

    def list_indices(self, database_id: str, collection_name: str):
        return sync(self.hiddb.list_indices(database_id, collection_name))

    def get_index(self, database_id: str, collection_name: str, index_name: str):
        return sync(self.hiddb.get_index(database_id, collection_name, index_name))
    
    def delete_index(self, database_id: str, collection_name: str, index_name: str):
        return sync(self.hiddb.delete_index(database_id, collection_name, index_name))

    def insert_document(self, database_id: str, collection_name: str, documents: list):
        return sync(self.hiddb.insert_document(database_id, collection_name, documents))

    def search_nearest_documents(self, database_id: str, collection_name: str, field_name: str, vectors=None, ids=None, max_neighbors=10):
        return sync(self.hiddb.search_nearest_documents(database_id, collection_name, field_name, vectors, ids=ids, max_neighbors=max_neighbors))

    def get_document(self, database_id: str, collection_name: str, document_id: str):
        return sync(self.hiddb.get_document(database_id, collection_name, document_id))

    def delete_document(self, database_id: str, collection_name: str, document_id: str):
        return sync(self.hiddb.delete_document(database_id, collection_name, document_id))
