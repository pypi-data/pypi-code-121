import hashlib
import json


def api_collection_id(collection_id):
    return collection_id if collection_id != "root" else None


def uuid(item):
    return hashlib.md5(str(item["id"]).encode()).hexdigest()


def content_hash(item):
    return hashlib.md5(json.dumps(item, sort_keys=True).encode()).hexdigest()
