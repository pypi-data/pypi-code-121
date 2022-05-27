import json
import base64
from urllib.request import urlopen
from urllib.request import Request
from urllib.error import URLError
from loguru import logger

URL = 'http://www.chuangfeigu.com:58888/froapi/aip/car_detect'


class DetectError(Exception):
    pass


def _extract(msg):
    try:
        data = json.loads(msg)
        aip_res = data['data']
        aip_data = json.loads(aip_res)
        if 'vehicle_info' in aip_data:
            res = (True, aip_data)
        else:
            res = (False, aip_data)
    except:
        logger.exception("error?")
        res = (False, msg)
    return res


class CarDetect():
    def __init__(self, id, apiKey) -> None:
        """车辆检测

        Args:
            id (str): 用户 ID
            apiKey (str): API KEY
        """
        self.custId = id
        self.apiKey = apiKey

    def inference(self, file):
        """车辆检测接口

        Args:
            file (str): 汽车图像文件路径，只支持 jpg/png/bmp 格式

        Returns:
            tuple: (bool, str), 若识别成功，则第一项为 True，第二项为识别结果。
                若识别失败，则第一项为 False，第二项为错误信息。
        """
        img_data = []
        with open(file, 'rb') as img_file:
            img_data = img_file.read()

        length = len(img_data)
        if length == 0:
            raise DetectError(f"文件 {file} 读取 0 字节")

        img = base64.b64encode(img_data)
        img = str(img, 'utf-8')
        params = {'custId': self.custId, 'apiKey': self.apiKey, 'image': img}

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

    # 需要识别的文件
    IMAGE = "fro_AI/test2.jpg"
    car_dt = CarDetect(CUSTID, APIKEY)
    ret = car_dt.inference(IMAGE)
    print(ret)
