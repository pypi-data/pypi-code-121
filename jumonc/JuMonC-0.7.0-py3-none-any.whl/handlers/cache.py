import logging

from flask import jsonify, make_response, Response, request

from typing import Dict, List, Union

from sqlalchemy import desc


from JuMonC.handlers.base import api_version_path, check_version, RESTAPI
from JuMonC.authentication import scopes
from JuMonC.authentication.check import check_auth
from JuMonC import settings

import JuMonC.models.cache.dbmodel as cache_model

from JuMonC.models import pluginInformation


logger = logging.getLogger(__name__)

links:List[Dict[str, Union[bool, str, List[Dict[str, str]]]]] = []

cache_path = "/cache"

@RESTAPI.route(api_version_path + cache_path, methods=["GET"])
@check_version
@check_auth(scopes["see_links"])
def returnCacheLinks(version: int) -> Response:
    logging.debug("Accessed /v%i/cache/", version)
    return make_response(jsonify(sorted(links, key=lambda dic: dic['link'])), 200)

def registerRestApiPaths(version: int) -> Dict[str, Union[bool, str, List[Dict[str, str]]]]:
    if pluginInformation.flask_path_reg is False:
        links.append(registerCacheList(version))
        links.append(registerCacheID(version))
    pluginInformation.flask_path_reg = True
    return {
        "link": "/v" + str(version) + cache_path,
        "isOptional": False,
        "description": "Retrieve old results",
        "parameters": [
            {"name": "token",
             "description": "Supply a token that shows you are allowed to access this link (or login once using /login)"}]
    }


def registerCacheList(version: int) -> Dict[str, Union[bool, str, List[Dict[str, str]]]]:
        
    @RESTAPI.route(api_version_path + cache_path + "/list", methods=["GET"])
    @check_version
    @check_auth(scopes["retrieve_simulation_data"])
    def returnCacheList(version: int) -> Response:
        entries = request.args.get('entries', default = settings.CACHE_DEFAULT_ENTRIES_PER_PAGE, type = int)
        page = request.args.get('page', default = 1, type = int)
        logging.debug("Accessed /v%i/cache/list/", version)

        if page < 1:
            return make_response("Pages start with 1, you set page number to: " + str(page), 422)

        
        start = (page-1)*entries
        cache_data = cache_model.CacheEntry.query.order_by(desc(cache_model.CacheEntry.cache_id)).offset(start).limit(entries)
        
        data:List[Dict[str, Union[int, float,str]]] = []
        index:Dict[str, Union[int, float,str]] = {"page": page,
                     "description": "Showing cache elements " + str(start) + " to " + str(start+entries) + ", most recent results first",
                    }
        if entries == settings.CACHE_DEFAULT_ENTRIES_PER_PAGE:
            if page > 1:
                index["previous page"] = "/v" + str(version) + "cache/list/?page=" + str(page-1)
            index["next page"] = "/v" + str(version) + "/cache/list/?page=" + str(page+1)
        else:
            if page > 1:
                index["previous page"] = "/v" + str(version) + "cache/list/?entries=" + str(entries) + "&page=" + str(page-1)
            index["next page"] = "/v" + str(version) + "/cache/list/?entries=" + str(entries) + "&page=" + str(page+1)
        data.append(index)
            
        for element in cache_data:
            data.append({"ID": element.cache_id,
                         "time": element.time.strftime(settings.DATETIME_FORMAT),
                         "link": "/v" + str(version) + "/cache/id/?id=" + str(element.cache_id),
                         "API_path": element.API_path})
        
        return make_response(jsonify(data), 200)
        
    return {
        "link": "/v" + str(version) + cache_path + "/list",
        "isOptional": False,
        "description": "List old results that can be retrieved, if to many results are avaiable, it will be split into pages",
        "parameters": [
            {"name": "page",
             "description": "Which page will be used"},
            {"name": "entries",
             "description": "How many entries are per page"},
            {"name": "token",
             "description": "Supply a token that shows you are allowed to access this link (or login once using /login)"}]
    }
        


def registerCacheID(version: int) -> Dict[str, Union[bool, str, List[Dict[str, str]]]]:
    
    @RESTAPI.route(api_version_path + cache_path + "/id", methods=["GET"])
    @check_version
    @check_auth(scopes["retrieve_simulation_data"])
    def returnCacheID(version: int) -> Response:
        c_id = request.args.get('id', type = int)
        logging.debug("Accessed /v%i/cache/id/", version)
        
        entry = cache_model.CacheEntry.query.filter_by(cache_id=c_id).first()
        if not entry:
            return make_response(("Cache entry with ID ",
                                  str(c_id),
                                  "could not be found. You can use /v",
                                  str(version),
                                  "/cache/list to see all avaiable entries"),
                            422)
            
        data:Dict[str, Union[bool, str, Dict[str, str]]] = {}
        data["Used API path"] = entry.API_path
        data["time"] = str(entry.time.strftime(settings.DATETIME_FORMAT))
            
        parameters:Dict[str, str] = {}
        for parameter in entry.parameters:
            parameters[parameter.parameter_name] = str(parameter.parameter_value)
        data["parameter"] = parameters
            
        results:Dict[str, str] = {}
        for result in entry.results_int:
            results[result.result_name] = str(result.result)
        for result in entry.results_float:
            results[result.result_name] = str(result.result)
        for result in entry.results_str:
            results[result.result_name] = result.result
        data["results"] = results  
            
        return make_response(jsonify(data), 200)
        
    return {
        "link": "/v" + str(version) + cache_path + "/id",
        "isOptional": False,
        "description": "Retrieve complete cache entry by ID",
        "parameters": [
            {"name": "id",
             "description": "ID of the cahce entry that shall be retrieved"},
            {"name": "token",
             "description": "Supply a token that shows you are allowed to access this link (or login once using /login)"}]
    }
        
