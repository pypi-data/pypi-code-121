import os
from cerberus import schema_registry


_MAX_RESULTS = 20


METHOD = {
    "type": {
        "type": "string",
        "required": True,
        "allowed": ["view", "operation"]
    },
    "handler": {
        "type": "method",
        "required": True
    }
}
schema_registry.add("alephvault.http_storage.schemas.method", METHOD)


ITEM_METHOD = {
    "type": {
        "type": "string",
        "required": True,
        "allowed": ["view", "operation"]
    },
    "handler": {
        "type": "item-method",
        "required": True
    }
}
schema_registry.add("alephvault.http_storage.schemas.item-method", ITEM_METHOD)


RESOURCE = {
    "type": {
        "type": "string",
        "required": True,
        "allowed": ["list", "simple"]
    },
    "db": {
        "type": "string",
        "required": True,
        "regex": "[a-zA-Z][a-zA-Z0-9_-]+"
    },
    "collection": {
        "type": "string",
        "required": True,
        "regex": "[a-zA-Z][a-zA-Z0-9_-]+"
    },
    "filter": {
        "type": "dict",
        "default_setter": lambda doc: {},
    },
    "projection": {
        # Intended for element and simple.
        "anyof": [
            {"type": "list"},
            {"type": "dict"}
        ]
    },
    "order_by": {
        "dependencies": {"type": "list"},
        "type": "list",
        "schema": {
            "type": "string",
            "regex": "-?[a-zA-Z][a-zA-Z0-9_-]+"
        }
    },
    "list_projection": {
        # Intended for elements in list pages.
        "dependencies": {"type": "list"},
        "anyof": [
            {"type": "list"},
            {"type": "dict"}
        ]
    },
    "methods": {
        "type": "dict",
        "default_setter": lambda doc: {},
        "keysrules": {
            "type": "string",
            "regex": "[a-zA-Z][a-zA-Z0-9_-]+"
        },
        "valuesrules": {
            "type": "dict",
            "schema": "alephvault.http_storage.schemas.method",
        },
    },
    "item_methods": {
        "type": "dict",
        # No default setter will be given here, since it collides
        # with the dependency setting (breaks for "type": "simple").
        "dependencies": {"type": "list"},
        "keysrules": {
            "type": "string",
            "regex": "[a-zA-Z][a-zA-Z0-9_-]+"
        },
        "valuesrules": {
            "type": "dict",
            "schema": "alephvault.http_storage.schemas.item-method",
        },
    },
    "verbs": {
        "empty": False,
        "default_setter": lambda doc: '*',
        "anyof": [
            {
                "type": "string",
                "allowed": ["*"]
            },
            {
                "type": "list",
                "dependencies": {"type": "list"},
                "allowed": ['create', 'list', 'read', 'replace', 'update', 'delete']
            },
            {
                "type": "list",
                "dependencies": {"type": "simple"},
                "allowed": ['create', 'read', 'replace', 'update', 'delete']
            }
        ]
    },
    "list_max_results": {
        "type": "integer",
        "default_setter": lambda doc: _MAX_RESULTS,
        "min": 1
    },
    "schema": {
        "type": "dict",
        "default_setter": lambda doc: {}
    },
    "soft_delete": {
        "type": "boolean",
        "default_setter": lambda doc: False
    },
    "indexes": {
        "type": "dict",
        "default_setter": lambda doc: {},
        "keysrules": {
            "type": "string",
            "empty": False,
            "regex": "[a-zA-Z][a-zA-Z0-9_-]+",
        },
        "valuesrules": {
            "type": "dict",
            "schema": {
                "unique": {
                    "type": "boolean",
                    "default_setter": lambda doc: False
                },
                "fields": {
                    "required": True,
                    "anyof": [
                        {
                            "type": "string",
                            "regex": "[#~@-]?[a-zA-Z][a-zA-Z0-9_-]+",
                        },
                        {
                            "type": "list",
                            "empty": False,
                            "schema": {
                                "type": "string",
                                "regex": "[#~@-]?[a-zA-Z][a-zA-Z0-9_-]+",
                            }
                        }
                    ]
                }
            }
        }
    }
}
schema_registry.add("alephvault.http_storage.schemas.resource", RESOURCE)


SETTINGS = {
    "debug": {
        "type": "boolean",
        "default": False,
    },
    "connection": {
        "type": "dict",
        "default_setter": lambda doc: {},
        "schema": {
            "host": {
                "type": "string",
                "empty": False,
                "default_setter": lambda doc: os.getenv('MONGODB_HOST', 'localhost')
            },
            "port": {
                "type": "integer",
                "empty": False,
                "default_setter": lambda doc: int(os.getenv('MONGODB_PORT', '27017'))
            },
            "user": {
                "type": "string",
                "empty": False,
                "default_setter": lambda doc: os.getenv('MONGODB_USER', '')
            },
            "password": {
                "type": "string",
                "empty": False,
                "default_setter": lambda doc: os.getenv('MONGODB_PASSWORD', '')
            }
        }
    },
    "global": {
        "type": "dict",
        "default_setter": lambda doc: {},
        "schema": {
            "list_max_results": {
                "type": "integer",
                "min": 1
            }
        }
    },
    "auth": {
        "type": "dict",
        "default_setter": lambda doc: {},
        "schema": {
            "db": {
                "type": "string",
                "regex": "[a-zA-Z][a-zA-Z0-9_-]+",
                "default_setter": lambda doc: os.getenv("APP_AUTH_DB", "alephvault_http_storage")
            },
            "collection": {
                "type": "string",
                "regex": "[a-zA-Z][a-zA-Z0-9_-]+",
                "default_setter": lambda doc: os.getenv("APP_AUTH_DB", "auth")
            },
        }
    },
    "resources": {
        "type": "dict",
        "required": True,
        "valuesrules": {
            "type": "dict",
            "schema": "alephvault.http_storage.schemas.resource",
        },
        "keysrules": {
            "type": "string",
            "regex": "[a-zA-Z][a-zA-Z0-9_-]+"
        }
    }
}
schema_registry.add("alephvault.http_storage.schemas.settings", SETTINGS)
