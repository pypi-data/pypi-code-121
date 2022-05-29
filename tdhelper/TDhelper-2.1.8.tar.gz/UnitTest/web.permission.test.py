import __init__
import unittest
from TDhelper.generic.recursion import recursion, recursionCall


@recursion
def permission(item, **kwargs):
    print(item, kwargs, "\r\n")
    if "children" in item:
        for o in item["children"]:
            recursionCall(permission, kwargs['limit'], o, **kwargs)
        kwargs["break"] = False
    else:
        kwargs["break"] = False
    return item, kwargs


class TestReflect(unittest.TestCase):
    def test_permission_call(self):
        _p = recursionCall(
            permission,
            200,{
                "permission_name": "APP Store",
                "permission_key": "APP_STORE",
                "permission_domain": "permission access domain",
                "permission_uri": "api/",
                "permission_enable": True,
                "permission_parent": 0,
                "children": [
                    {
                        "permission_name": "APP LIST",
                        "permission_key": "APP_STORE_APP_LISTS",
                        "permission_domain": "permission access domain",
                        "permission_uri": "api/apps",
                        "permission_enable": True,
                        "children": [
                            {
                                "permission_name": "APP CREATE",
                                "permission_key": "APP_STORE_APP_CREATE",
                                "permission_domain": "permission access domain",
                                "permission_uri": "api/apps",
                                "permission_enable": True,
                            },
                            {
                                "permission_name": "APP RETRIEVE",
                                "permission_key": "APP_STORE_APP_RETRIEVE",
                                "permission_domain": "permission access domain",
                                "permission_uri": "api/apps",
                                "permission_enable": True,
                            },
                            {
                                "permission_name": "APP UPDATE",
                                "permission_key": "APP_STORE_APP_UPDATE",
                                "permission_domain": "permission access domain",
                                "permission_uri": "api/apps",
                                "permission_enable": True,
                            },
                            {
                                "permission_name": "APP DESTROY",
                                "permission_key": "APP_STORE_APP_DESTROY",
                                "permission_domain": "permission access domain",
                                "permission_uri": "api/apps",
                                "permission_enable": True,
                            },
                        ],
                    },
                    {
                        "permission_name": "APP STORE ACCESS",
                        "permission_key": "APP_STORE_ACCESS",
                        "permission_domain": "permission access domain",
                        "permission_uri": "api/access",
                        "permission_enable": True,
                        "children": [
                            {
                                "permission_name": "APP STORE ACCESS LIST",
                                "permission_key": "APP_STORE_ACCESS_LIST",
                                "permission_domain": "permission access domain",
                                "permission_uri": "api/access",
                                "permission_enable": True,
                            },
                            {
                                "permission_name": "APP STORE ACCESS CREATE",
                                "permission_key": "APP_STORE_ACCESS_CREATE",
                                "permission_domain": "permission access domain",
                                "permission_uri": "api/access",
                                "permission_enable": True,
                            },
                            {
                                "permission_name": "APP STORE ACCESS RETRIEVE",
                                "permission_key": "APP_STORE_ACCESS_RETRIEVE",
                                "permission_domain": "permission access domain",
                                "permission_uri": "api/access",
                                "permission_enable": True,
                            },
                            {
                                "permission_name": "APP STORE ACCESS UPDATE",
                                "permission_key": "APP_STORE_ACCESS_UPDATE",
                                "permission_domain": "permission access domain",
                                "permission_uri": "api/access",
                                "permission_enable": True,
                            },
                            {
                                "permission_name": "APP STORE ACCESS DESTROY",
                                "permission_key": "APP_STORE_ACCESS_DESTROY",
                                "permission_domain": "permission access domain",
                                "permission_uri": "api/access",
                                "permission_enable": True,
                            },
                        ],
                    },
                    {
                        "permission_name": "DEVELOPER",
                        "permission_key": "DEVELOPER",
                        "permission_domain": " permission access domain",
                        "permission_uri": "api/developer",
                        "permission_enable": True,
                        "children": [
                            {
                                "permission_name": "DEVELOPER LIST",
                                "permission_key": "DEVELOPER_LIST",
                                "permission_domain": "permission access domain",
                                "permission_uri": "api/developer",
                                "permission_enable": True,
                            },
                            {
                                "permission_name": "DEVELOPER CREATE",
                                "permission_key": "DEVELOPER_CREATE",
                                "permission_domain": "permission access domain",
                                "permission_uri": "api/developer",
                                "permission_enable": True,
                            },
                            {
                                "permission_name": "DEVELOPER RETRIEVE",
                                "permission_key": "DEVELOPER_RETRIEVE",
                                "permission_domain": "permission access domain",
                                "permission_uri": "api/developer",
                                "permission_enable": True,
                            },
                            {
                                "permission_name": "DEVELOPER UPDATE",
                                "permission_key": "DEVELOPER_UPDATE",
                                "permission_domain": "permission access domain",
                                "permission_uri": "api/developer",
                                "permission_enable": True,
                            },
                            {
                                "permission_name": "DEVELOPER DESTROY",
                                "permission_key": "DEVELOPER_DESTROY",
                                "permission_domain": "permission access domain",
                                "permission_uri": "api/developer",
                                "permission_enable": True,
                            },
                        ],
                    },
                    {
                        "permission_name": "DEVELOPER TOKEN",
                        "permission_key": "DEVELOPER_TOKEN",
                        "permission_domain": "permission access domain",
                        "permission_uri": "api/token",
                        "permission_enable": True,
                        "children": [
                            {
                                "permission_name": "Developer token list",
                                "permission_key": "DEVELOPER_TOKEN_LIST",
                                "permission_domain": " permission access domain",
                                "permission_uri": "api/token",
                                "permission_enable": True,
                            },
                            {
                                "permission_name": "Developer token destroy",
                                "permission_key": "DEVELOPER_TOKEN_DESTROY",
                                "permission_domain": " permission access domain",
                                "permission_uri": "api/token",
                                "permission_enable": True,
                            },
                        ],
                    },
                ],
            },
            **{}
        )


if __name__ == "__main__":
    unittest.main()
