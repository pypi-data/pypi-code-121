import logging

from flask import abort, jsonify, make_response, Response, request

from typing import Dict, List, Union


from JuMonC.handlers.base import api_version_path, check_version, RESTAPI
from JuMonC.authentication import scopes
from JuMonC.authentication.check import check_auth
from JuMonC.models import pluginInformation
from JuMonC.tasks import disk
from JuMonC import settings

import JuMonC.models.cache.helper as cache


logger = logging.getLogger(__name__)

links:        List[Dict[str, Union[bool, str, List[Dict[str, str]]]]] = []
status_links: List[Dict[str, Union[bool, str, List[Dict[str, str]]]]] = []
config_links: List[Dict[str, Union[bool, str, List[Dict[str, str]]]]] = []

io_path = "/io"

@RESTAPI.route(api_version_path + io_path, methods=["GET"])
@check_version
@check_auth(scopes["see_links"])
def returnIOLinks(version: int) -> Response:
    logging.debug("Accessed /v%i/io/", version)
    return make_response(jsonify(sorted(links, key=lambda dic: dic['link'])), 200)

@RESTAPI.route(api_version_path + io_path + "/status", methods=["GET"])
@check_version
@check_auth(scopes["see_links"])
def returnIOStatusLinks(version: int) -> Response:
    logging.debug("Accessed /v%i/io/status", version)
    return make_response(jsonify(sorted(status_links, key=lambda dic: dic['link'])), 200)

@RESTAPI.route(api_version_path + io_path + "/config", methods=["GET"])
@check_version
@check_auth(scopes["see_links"])
def returnIOConfigLinks(version: int) -> Response:
    logging.debug("Accessed /v%i/io/config", version)
    return make_response(jsonify(sorted(config_links, key=lambda dic: dic['link'])), 200)

def registerRestApiPaths(version: int) -> Dict[str, Union[bool, str, List[Dict[str, str]]]]:
    links.append(registerStatusLinks(version))
    #links.append(registerConfigLinks(version)) not in use for now
    return {
        "link": "/v" + str(version) + io_path,
        "isOptional": False,
        "description": "Gather information about the disk IO",
        "parameters": [
            {"name": "token",
             "description": "Supply a token that shows you are allowed to access this link (or login once using /login)"}]
    }


def registerStatusLinks(version: int) -> Dict[str, Union[bool, str, List[Dict[str, str]]]]:
    types : List[str] = ["read_count", "write_count",
                         "read_bytes", "write_bytes",
                         "read_time", "write_time",
                         "busy_time",
                         "read_merged_count", "write_merged_count"]
    descriptions : List[str] = ["number of reads", "number of writes",
                                "number of bytes read", "number of bytes written",
                                "time spent reading from disk", "time spent writing to disk" ,
                                "time spent doing actual I/Os",
                                "number of merged reads (see iostats doc)", "number of merged writes (see iostats doc)"]
    if pluginInformation.disk_is_working:
        for i, typeStr in enumerate(types):
            status_links.append({
            "link": "/v" + str(version) + io_path + "/status/" + typeStr,
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
        
        @RESTAPI.route(api_version_path + io_path + "/status/<string:datatype>", methods=["GET"])
        @check_version
        @check_auth(scopes["compute_data"])
        def returnIOStatus(version: int, datatype:str) -> Response:
            duration = request.args.get('duration', default = -1.0, type = float)
            humanReadable = request.args.get('humanReadable', default = settings.DEFAULT_TO_HUMAN_READABLE_NUMBERS, type = settings.helpers.parse_boolean)
            logging.debug("Accessed /v%i/io/status/%s", version, datatype)
            
            cache_id = cache.add_cache_entry("/v" + str(version) + "/io/status/" + datatype)
            if duration >0:
                cache.addParameter(cache_id, "duration", str(duration))
                cache.commit()
            
            data = disk.plugin.getStatusData(dataType = datatype,
                                               duration = duration,
                                               overrideHumanReadableWithValue = humanReadable)
            if len(data) > 0:
                for data_element in data:
                    for result_name, result in data_element.items():
                        cache.addResult(cache_id, result_name, result)
                cache.commit()
                return make_response(jsonify(data), 200)
            
            logging.warning("Accessed /v%i/io/status/%s, but not avaiable", version, datatype)
            abort(404)
            return make_response("",404)
        
    return {
        "link": "/v" + str(version) + io_path + "/status",
        "isOptional": False,
        "description": "Gather information concerning the IO status",
        "parameters": [
            {"name": "token",
             "description": "Supply a token that shows you are allowed to access this link (or login once using /login)"}]
    }


def registerConfigLinks(version: int) -> Dict[str, Union[bool, str, List[Dict[str, str]]]]:
    types : List[str] = []
    descriptions : List[str] = []
    if pluginInformation.disk_is_working:
        for i, typeStr in enumerate(types):
            config_links.append({
            "link": "/v" + str(version) + io_path + "/status/" + typeStr,
            "isOptional": True,
            "description": descriptions[i],
            "parameters": [
                {"name": "humanReadable",
                "description": "For 'True' convert to better readable numbers, for 'False' return actual number. " + 
                 "If not set to valid value, uses default value(" + str(settings.DEFAULT_TO_HUMAN_READABLE_NUMBERS) + ")."},
                {"name": "node",
                "description": "When this parameter is not present the average data of all nodes is presented, otherwise only from the choosen node"},
                {"name": "token",
                "description": "Supply a token that shows you are allowed to access this link (or login once using /login)"}]
            })
        
        @RESTAPI.route(api_version_path + io_path + "/config/<string:datatype>", methods=["GET"])
        @check_version
        @check_auth(scopes["compute_data"])
        def returnIOConfig(version: int, datatype:str) -> Response:
            humanReadable = request.args.get('humanReadable', default = settings.DEFAULT_TO_HUMAN_READABLE_NUMBERS, type = settings.helpers.parse_boolean)
            logging.debug("Accessed /v%i/io/config/%s", version, datatype)
            data = disk.plugin.getConfigData(dataType = datatype, overrideHumanReadableWithValue = humanReadable)
            if len(data) > 0:
                return make_response(jsonify(data), 200)
            
            logging.warning("Accessed /v%i/io/config/%s, but not avaiable", version, datatype)
            abort(404)
            return make_response("",404)
        
    return {
        "link": "/v" + str(version) + io_path + "/config",
        "isOptional": False,
        "description": "Gather information concerning the IO config",
        "parameters": [
            {"name": "token",
             "description": "Supply a token that shows you are allowed to access this link (or login once using /login)"}]
    }
