import logging
from bson import ObjectId
from flask import request, make_response, jsonify
from pymongo import MongoClient
from alephvault.http_storage import StorageApp
from alephvault.http_storage import MethodHandler, ItemMethodHandler


logging.basicConfig()


class SetMOTDHandler(MethodHandler):

    def __call__(self, client: MongoClient, resource: str, method: str, db: str, collection: str, filter: dict):
        if not request.is_json:
            return make_response(jsonify({"code": "format:unexpected"}), 400)

        try:
            motd = request.json.get('motd')
            if not motd:
                return make_response(jsonify({"code": "unchanged"}), 200)
            result = client[db][collection].update_one(filter, {"$set": {"motd": motd}})
            if result.modified_count:
                return make_response(jsonify({"code": "ok"}), 200)
            else:
                return make_response(jsonify({"code": "not-found"}), 404)
        except AttributeError:
            return make_response(jsonify({"code": "format:unexpected"}), 400)


class GetVersionHandler(MethodHandler):

    def __call__(self, client: MongoClient, resource: str, method: str, db: str, collection: str, filter: dict):
        document = client[db][collection].find_one(filter)
        if document:
            return make_response(jsonify({"version": document["version"]}), 200)
        else:
            return make_response(jsonify({"code": "not-found"}), 404)


class TotalItemsAllElements(MethodHandler):

    def __call__(self, client: MongoClient, resource: str, method: str, db: str, collection: str, filter: dict):
        total = sum([int(count) for account in client[db][collection].find(filter)
                     for item, count in account.get("inventory", {}).items()])
        return jsonify({"total": total}), 200


class TotalItemsOneElement(ItemMethodHandler):

    def __call__(self, client: MongoClient, resource: str, method: str, db: str, collection: str, filter: dict,
                 object_id: ObjectId):
        element = client[db][collection].find_one({**filter, "_id": object_id})
        if not element:
            return jsonify({"code": "not-found"}), 404
        total = sum([int(count) for item, count in element.get("inventory", {}).items()])
        return jsonify({"total": total}), 200


class TotalItemsOneElementForType(ItemMethodHandler):

    def __call__(self, client: MongoClient, resource: str, method: str, db: str, collection: str, filter: dict,
                 object_id: ObjectId):
        element = client[db][collection].find_one({**filter, "_id": object_id})
        if not element:
            return jsonify({"code": "not-found"}), 404
        type_ = request.args.get('type')
        if not type_:
            return jsonify({"code": "missing-type"}), 400
        total = element.get("inventory", {}).get(type_, 0)
        return jsonify({"total": total}), 200


class AddItemsOneElement(ItemMethodHandler):

    def __call__(self, client: MongoClient, resource: str, method: str, db: str, collection: str, filter: dict,
                 object_id: ObjectId):
        element = client[db][collection].find_one({**filter, "_id": object_id})
        if not element:
            return jsonify({"code": "not-found"}), 404
        if not request.is_json:
            return jsonify({"code": "json-body-required"}), 400
        content = request.json
        try:
            item = content.get("item")
            by = int(content.get("by", "0"))
            if not item:
                raise ValueError()
        except:
            return jsonify({"code": "json-body-wrong"}), 400
        client[db][collection].update_one({**filter, "_id": object_id}, {"$set": {
            "inventory." + item: str(by + int(element["inventory"].get(item, "0")))
        }})
        return jsonify({"code": "ok"}), 200


class SubItemsOneElement(ItemMethodHandler):

    def __call__(self, client: MongoClient, resource: str, method: str, db: str, collection: str, filter: dict,
                 object_id: ObjectId):
        element = client[db][collection].find_one({**filter, "_id": object_id})
        if not element:
            return jsonify({"code": "not-found"}), 404
        if not request.is_json:
            return jsonify({"code": "json-body-required"}), 400
        content = request.json
        try:
            item = content.get("item")
            by = int(content.get("by", "0"))
            if not item:
                raise ValueError()
        except:
            return jsonify({"code": "json-body-wrong"}), 400
        client[db][collection].update_one({**filter, "_id": object_id}, {"$set": {
            "inventory." + item: str(int(element["inventory"].get(item, "0")) - by)
        }})
        return jsonify({"code": "ok"}), 200


UNIVERSE = {
    "caption": {
        "type": "string",
        "required": True
    },
    "motd": {
        "type": "string",
        "required": True
    },
    "version": {
        "type": "dict",
        "required": True,
        "schema": {
            "major": {
                "type": "integer",
                "required": True,
                "min": 0
            },
            "minor": {
                "type": "integer",
                "required": True,
                "min": 0
            },
            "revision": {
                "type": "integer",
                "required": True,
                "min": 0
            },
        }
    }
}


ACCOUNT = {
    "address": {
        "type": "string",
        "required": True
    },
    "name": {
        "type": "string",
        "required": True
    },
    "inventory": {
        "type": "dict",
        "required": True,
        "keysrules": {
            # The key is an int256. It cannot be represented as int.
            "type": "string",
            "regex": r"^\d+$"
        },
        "valuesrules": {
            # The value is an int256. It cannot be represented as int.
            "type": "string",
            "regex": r"^\d+$"
        }
    }
}


class SampleStorageApp(StorageApp):
    """
    A sample application, with a sample domain. This domain has some parts, like:

    - Universe: mydb.universe
    - Accounts: mydb.accounts
    """

    SETTINGS = {
        "auth": {
            "db": "auth-db",
            "collection": "api-keys"
        },
        "connection": {
            "host": "localhost",
            "port": 27017,
            "user": "admin",
            "password": "p455w0rd"
        },
        "resources": {
            "universe": {
                "type": "simple",
                "db": "mydb",
                "collection": "universe",
                "soft_delete": True,
                "schema": UNIVERSE,
                "projection": ["caption", "motd"],
                "verbs": "*",
                "methods": {
                    "set-motd": {
                        "type": "operation",
                        "handler": SetMOTDHandler()
                    },
                    "version": {
                        "type": "view",
                        "handler": GetVersionHandler()
                    }
                }
            },
            "accounts": {
                "type": "list",
                "db": "mydb",
                "collection": "accounts",
                "schema": ACCOUNT,
                "list_projection": ["address", "name"],
                "verbs": "*",
                "methods": {
                    "total-items": {
                        "type": "view",
                        "handler": TotalItemsAllElements()
                    },
                },
                "item_methods": {
                    "total-items": {
                        "type": "view",
                        "handler": TotalItemsOneElement()
                    },
                    "total-items-for-type": {
                        "type": "view",
                        "handler": TotalItemsOneElementForType()
                    },
                    "add-items-for-type": {
                        "type": "operation",
                        "handler": AddItemsOneElement()
                    },
                    "subtract-items-for-type": {
                        "type": "operation",
                        "handler": SubItemsOneElement()
                    }
                },
                "indexes": {
                    "unique-name": {
                        "unique": True,
                        "fields": "name"
                    },
                }
            }
        }
    }

    def __init__(self, import_name: str = __name__):
        super().__init__(self.SETTINGS, import_name=import_name)
        try:
            self._client["auth-db"]["api-keys"].insert_one({"api-key": "abcdef"})
        except:
            pass


if __name__ == "__main__":
    app = SampleStorageApp()
    app.run("localhost", 6666)
