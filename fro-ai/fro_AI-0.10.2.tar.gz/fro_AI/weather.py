import json
from urllib.request import urlopen
from urllib.request import Request
from urllib.error import URLError
from loguru import logger

URL = 'http://www.chuangfeigu.com:58888/froapi/weather'


def _extract(msg):
    try:
        data = json.loads(msg)
        aip_res = data['data']

        res = (True, aip_res)

    except:
        logger.exception("error?")
        res = (False, msg)
    return res


class Weather():
    def __init__(self, id, apiKey) -> None:
        """天气查询

        Args:
            id (str): 用户 ID
            apiKey (str): API KEY
        """
        self.custId = id
        self.apiKey = apiKey

    def inference(self, city):
        """天气查询接口

        Args:
            city (str): 城市名称

        Returns:
            tuple: (bool, str), 若识别成功，则第一项为 True，第二项为识别结果。
                若识别失败，则第一项为 False，第二项为错误信息。
        """
        params = {'custId': self.custId, 'apiKey': self.apiKey, 'city': city}

        post_data = json.dumps(params, sort_keys=False)
        req = Request(URL, post_data.encode('utf-8'))
        req.add_header('Content-Type', 'application/json')
        req.add_header('appId', 'v1')
        req.add_header('sign', 'a6e1f81461204ae8b64665fe04d4eef1')
        try:
            f = urlopen(req)
            result_str = f.read()
        except URLError as err:
            print('car classify http response http code : ' + str(err.code))
            result_str = err.read()
        return _extract(result_str)


if __name__ == "__main__":
    CUSTID = "efPRTm6MHHOyRtMj"
    APIKEY = "FB65xcK78XMROsSerGgukmN4k10w8GuJ"

    weather = Weather(CUSTID, APIKEY)
    ret = weather.inference("番禺")
    print(ret)
