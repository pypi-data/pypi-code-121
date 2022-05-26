#!/usr/bin/env python3.6
#! -*- coding: utf-8 -*-
import tornado

from components.dbproxy import DbProxy, LOG
from const.route import ROUTE_MAP
from models.xhhk import appconfig


def regeist_route():
    LOG.info("注册路由ing!")
    isexist = yield DbProxy.find_one_mongo(appconfig, app_id=ROUTE_MAP.app_config)
    if not isexist:
        LOG.error("未找到该机构.")
    else:
        routes = []
        for route, value in ROUTE_MAP.route_map:
            yield DbProxy.find_one_mongo(appconfig, endpoint=route, app_id=ROUTE_MAP.app_config, as_dict=True)
            routes.append(appconfig(
                app_id="",
                type="webservice",
                name=value.get('name'),
                collaborate_type="1900",
                endpoint=route,
                protocol="REST",
                http_method="POST",
                signature_field="Signature",
                signature_position="header",
                signature_version="none",
                signature_key="",
                ssl_crt={},
                services={},
                options={},
                expired_time=0,
                api_version="1.0"
            ))
        yield DbProxy().insert_mongo(routes)
