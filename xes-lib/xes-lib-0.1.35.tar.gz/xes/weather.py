import requests

from xes import common
# 获得温度
def air_temp(location, start = 0):
    cookies = common.getCookies()
    headers = {"Cookie": cookies}
    params = {"location": location, "day": start}
    rep = requests.get("https://code.xueersi.com/api/ai/python_weather/temperature", params=params, headers=headers)
    repDic = common.jsonLoads(rep.text)
    if repDic is None:
        raise Exception("天气查询失败,请稍后再试")
    if repDic["stat"] != 1:
        raise Exception(repDic["msg"])

    return int(repDic["data"])


# 获得风速
def air_speed(location, start = 0):
    cookies = common.getCookies()
    headers = {"Cookie": cookies}
    params = {"location":location,"day":start}
    rep = requests.get("https://code.xueersi.com/api/ai/python_weather/wind_speed", params=params, headers=headers)
    repDic = common.jsonLoads(rep.text)
    if repDic is None:
        raise Exception("天气查询失败,请稍后再试")
    if repDic["stat"] != 1:
        raise Exception(repDic["msg"])

    return int(repDic["data"])