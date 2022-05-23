import logging

from flask import jsonify, make_response, Response

from typing import Dict, List, Union


from JuMonC.handlers import base
from JuMonC.handlers import versionTree
from JuMonC.handlers import auth


logger = logging.getLogger(__name__)

links: List[Dict[str, Union[bool, str, List[Dict[str, str]]]]] = []




@base.RESTAPI.route("/", methods=["GET"])
def returnRootLinks() -> Response:
    return make_response(jsonify(sorted(links, key=lambda dic: dic['link'])), 200)


def registerRestApiPaths() -> None:
    for i in range(base.start_version, base.end_version + 1):
        links.append(versionTree.registerRestApiPaths(i))
        
    links.append(auth.registerLogin())
    links.append(auth.registerLogout())
    links.append(auth.registerScope())

    links.append({
        "link": "/version",
        "isOptional": False,
        "description": "Get current version of JuMonC",
        "parameters": [
            {"name": "token",
             "description": "Supply a token that shows you are allowed to access this link (or login once using /login)"}]
    })
    links.append({
        "link": "/ping",
        "isOptional": False,
        "description": "Test link to test avaibility of JuMonC REST API",
        "parameters": [
            {"name": "token",
             "description": "Supply a token that shows you are allowed to access this link (or login once using /login)"}]
    })
    links.append({
        "link": "/stop",
        "isOptional": False,
        "description": "Calling this link stops JuMonC",
        "parameters": [
            {"name": "token",
             "description": "Supply a token that shows you are allowed to access this link (or login once using /login)"}]
    })