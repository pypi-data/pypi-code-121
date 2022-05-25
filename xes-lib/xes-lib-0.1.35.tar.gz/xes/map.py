#conding:utf-8
import requests
from xes import common

g_routes = None

def get_routes(start, end, city = None):
    cookies = common.getCookies()
    headers = {"Cookie": cookies}

    params = {"address_origin":start,"address_destination":end,"city":city}
    rep = requests.get("http://code.xueersi.com/api/ai/python_map/routes", params=params, headers=headers)
    repDic = common.jsonLoads(rep.text)
    if repDic is None:
        raise Exception("高德地图服务请求超时，请稍后再试")

    if repDic["stat"] != 1:
        raise Exception(repDic["msg"])

    global g_routes
    g_routes = repDic["data"]

    route_names = []
    for route in g_routes:
        route_names.append(route["name"])

    return route_names

def get_sites(route_list, num):

    global g_routes
    if g_routes is None:
        raise Exception("请先调用get_routes函数")

    num = int(num)
    route = g_routes[num]
    return route["stops"]
