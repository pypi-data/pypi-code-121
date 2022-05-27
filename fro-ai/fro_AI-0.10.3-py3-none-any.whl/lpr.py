import json
import base64
from urllib.request import urlopen
from urllib.request import Request
from urllib.error import URLError
from loguru import logger

LPR_URL = 'http://www.chuangfeigu.com:58888/froapi/aip/car_license'


class LPRError(Exception):
    pass


def _extract(msg):
    try:
        data = json.loads(msg)
        aip_res = data['data']
        aip_data = json.loads(aip_res)
        res_str = aip_data['words_result']
        res = (True, res_str)
    except:
        logger.exception("error?")
        res = (False, msg)
    return res


class LPR():
    def __init__(self, id, apiKey) -> None:
        """车牌识别

        Args:
            id (str): 用户 ID
            apiKey (str): API KEY
        """
        self.custId = id
        self.apiKey = apiKey

    def inference(self, file, multi_detect=False, multi_scale=False):
        """车牌识别接口

        Args:
            file (str): 车牌图像文件路径，只支持 jpg/jpeg/png/bmp 格式
            multi_detect (bool, optional): 是否检测多张车牌，默认为 False，当置为 True 的时候可以对一张图片内的多张车牌进行识别
            multi_scale (bool, optional): 在高拍等车牌较小的场景下可开启，默认为 False，当置为 True 时，能够提高对较小车牌的检测和识别

        Returns:
            tuple: (bool, str), 若识别成功，则第一项为 True，第二项为识别结果。
                若识别失败，则第一项为 False，第二项为错误信息。
        """
        img_data = []
        with open(file, 'rb') as img_file:
            img_data = img_file.read()

        length = len(img_data)
        if length == 0:
            raise LPRError(f"文件 {file} 读取 0 字节")

        img = base64.b64encode(img_data)
        img = str(img, 'utf-8')
        params = {'custId': self.custId, 'apiKey': self.apiKey, 'image': img}
        if multi_detect:
            params['multi_detect'] = "true"
        if multi_scale:
            params['multi_scale'] = "true"
        post_data = json.dumps(params, sort_keys=False)
        req = Request(LPR_URL, post_data.encode('utf-8'))
        req.add_header('Content-Type', 'application/json')
        req.add_header('appId', 'v1')
        req.add_header('sign', 'a6e1f81461204ae8b64665fe04d4eef1')
        try:
            f = urlopen(req)
            result_str = f.read()
        except URLError as err:
            print('lpr http response http code : ' + str(err.code))
            result_str = err.read()
        return _extract(result_str)


if __name__ == "__main__":
    CUSTID = "efPRTm6MHHOyRtMj"
    APIKEY = "FB65xcK78XMROsSerGgukmN4k10w8GuJ"

    # 需要识别的文件
    IMAGE = "fro_AI/download.png"
    lpr = LPR(CUSTID, APIKEY)
    ret = lpr.inference(IMAGE)
    print(ret)
