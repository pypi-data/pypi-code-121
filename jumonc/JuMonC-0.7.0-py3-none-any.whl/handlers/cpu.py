import logging

from flask import abort, jsonify, make_response, Response, request

from typing import Dict, List, Union


from JuMonC.handlers.base import api_version_path, check_version, RESTAPI
from JuMonC.models import pluginInformation
from JuMonC.tasks import CPU
from JuMonC.authentication import scopes
from JuMonC.authentication.check import check_auth
from JuMonC import settings

import JuMonC.models.cache.helper as cache

logger = logging.getLogger(__name__)

links:        List[Dict[str, Union[bool, str, List[Dict[str, str]]]]] = []
status_links: List[Dict[str, Union[bool, str, List[Dict[str, str]]]]] = []
config_links: List[Dict[str, Union[bool, str, List[Dict[str, str]]]]] = []

cpu_path = "/cpu"

@RESTAPI.route(api_version_path + cpu_path, methods=["GET"])
@check_version
@check_auth(scopes["see_links"])
def returnCPULinks(version: int) -> Response:
    logging.debug("Accessed /v%i/cpu/", version)
    return make_response(jsonify(sorted(links, key=lambda dic: dic['link'])), 200)

@RESTAPI.route(api_version_path + cpu_path + "/status", methods=["GET"])
@check_version
@check_auth(scopes["see_links"])
def returnCPUStatusLinks(version: int) -> Response:
    logging.debug("Accessed /v%i/cpu/status", version)
    return make_response(jsonify(sorted(status_links, key=lambda dic: dic['link'])), 200)

@RESTAPI.route(api_version_path + cpu_path + "/config", methods=["GET"])
@check_version
@check_auth(scopes["see_links"])
def returnCPUConfigLinks(version: int) -> Response:
    logging.debug("Accessed /v%i/cpu/config", version)
    return make_response(jsonify(sorted(config_links, key=lambda dic: dic['link'])), 200)

def registerRestApiPaths(version: int) -> Dict[str, Union[bool, str, List[Dict[str, str]]]]:
    links.append(registerStatusLinks(version))
    links.append(registerConfigLinks(version))
    return {
        "link": "/v" + str(version) + cpu_path,
        "isOptional": False,
        "description": "Gather information concerning the CPU",
        "parameters": [
            {"name": "token",
             "description": "Supply a token that shows you are allowed to access this link (or login once using /login)"}]
    }


def registerStatusLinks(version: int) -> Dict[str, Union[bool, str, List[Dict[str, str]]]]:
    
    types : List[str] = ["load"]
    descriptions : List[str] = ["Get the system load, duration can be 1,5 or 15 min"]
    if pluginInformation.cpu_is_working:
        for i, typeStr in enumerate(types):
            status_links.append({
            "link": "/v" + str(version) + cpu_path + "/status/" + typeStr,
            "isOptional": True,
            "description": descriptions[i],
            "parameters": [
                {"name": "node",
                "description": "When this parameter is not present the average data of all nodes is presented, otherwise only from the choosen node"},
                {"name": "token",
                "description": "Supply a token that shows you are allowed to access this link (or login once using /login)"}]
            })
        
        @RESTAPI.route(api_version_path + cpu_path + "/status/<string:datatype>", methods=["GET"])
        @check_version
        @check_auth(scopes["compute_data"])
        def returnCPUStatus(version: int, datatype:str) -> Response:
            humanReadable = request.args.get('humanReadable', default = settings.DEFAULT_TO_HUMAN_READABLE_NUMBERS, type = settings.helpers.parse_boolean)
            logging.debug("Accessed /v%i/cpu/status/%s", version, datatype)
            
            cache_id = cache.add_cache_entry("/v" + str(version) + "/cpu/status/" + datatype)
            
            data = CPU.plugin.getStatusData(dataType = datatype,
                                            overrideHumanReadableWithValue = humanReadable)
            if len(data) > 0:
                for data_element in data:
                    for result_name, result in data_element.items():
                        cache.addResult(cache_id, result_name, result)
                cache.commit()
                return make_response(jsonify(data), 200)
            
            logging.warning("Accessed /v%i/cpu/status/%s, but not avaiable", version, datatype)
            abort(404)
            return make_response("",404)
        
    return {
        "link": "/v" + str(version) + cpu_path + "/status",
        "isOptional": False,
        "description": "Gather information concerning the cpu status",
        "parameters": [
            {"name": "token",
             "description": "Supply a token that shows you are allowed to access this link (or login once using /login)"}]
    }


def registerConfigLinks(version: int) -> Dict[str, Union[bool, str, List[Dict[str, str]]]]:
    types : List[str] = []
    descriptions : List[str] = []
    if pluginInformation.cpu_is_working:
        for i, typeStr in enumerate(types):
            config_links.append({
            "link": "/v" + str(version) + cpu_path + "/status/" + typeStr,
            "isOptional": True,
            "description": descriptions[i],
            "parameters": [
                {"name": "duration",
                "description": "When this parameter is not present the raw data value(s) will be provided, otherwise the average value per second"},
                {"name": "humanReadable",
                "description": "For 'True' convert to better readable numbers, for 'False' return actual number. " + 
                 "If not set to valid value, uses default value(" + str(settings.DEFAULT_TO_HUMAN_READABLE_NUMBERS) + ")."},
                {"name": "node",
                "description": "When this parameter is not present the average data of all nodes is presented, otherwise only from the choosen node"},
                {"name": "token",
                "description": "Supply a token that shows you are allowed to access this link (or login once using /login)"}]
            })
        
        @RESTAPI.route(api_version_path + cpu_path + "/config/<string:datatype>", methods=["GET"])
        @check_version
        @check_auth(scopes["compute_data"])
        def returnCPUConfig(version: int, datatype:str) -> Response:
            humanReadable = request.args.get('humanReadable', default = settings.DEFAULT_TO_HUMAN_READABLE_NUMBERS, type = settings.helpers.parse_boolean)
            logging.debug("Accessed /v%i/cpu/config/%s", version, datatype)
            data = CPU.plugin.getConfigData(dataType = datatype, overrideHumanReadableWithValue = humanReadable)
            
            
            
            if len(data) > 0:
                return make_response(jsonify(data), 200)
            
            logging.warning("Accessed /v%i/cpu/config/%s, but not avaiable", version, datatype)
            abort(404)
            return make_response("",404)
        
    return {
        "link": "/v" + str(version) + cpu_path + "/config",
        "isOptional": False,
        "description": "Gather information concerning the cpu config",
        "parameters": [
            {"name": "token",
             "description": "Supply a token that shows you are allowed to access this link (or login once using /login)"}]
    }
