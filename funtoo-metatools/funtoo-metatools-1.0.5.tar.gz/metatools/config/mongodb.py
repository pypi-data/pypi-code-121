from pymongo import MongoClient

MONGODB_NAME = 'metatools2'


def get_collection(collection_name):
	client = MongoClient()
	db = getattr(client, MONGODB_NAME)
	return getattr(db, collection_name)
