import json
import base64
import uuid
from urllib.request import urlopen
from urllib.request import Request
from urllib.error import URLError
from loguru import logger

ASR_URL = 'http://www.chuangfeigu.com:58888/froapi/speech/vopapi'

dev_pid = {
    "mandarin_near": 1537,
    "english": 1737,
    "cantonese": 1637,
    "sichuan": 1837,
    "mandarin_far": 1936
}


class SRError(Exception):
    pass


def _extract(msg):
    try:
        data = json.loads(msg)
        aip_res = data['data']
        aip_data = json.loads(aip_res)
        res_str = aip_data['result'][0]
        res = (True, res_str)
    except:
        logger.exception("error?")
        res = (False, msg)
    return res


class SpeechRecognizer():
    def __init__(self, id, apiKey) -> None:
        """语音识别

        Args:
            id (str): 用户 ID
            apiKey (str): API KEY
        """
        self.custId = id
        self.apiKey = apiKey
        self.cuid = hex(uuid.getnode())[2:]

    def inference(self, file, rate=16000, model="mandarin_near"):
        """语音识别接口

        Args:
            file (str): 语音文件路径，只支持 pcm/wav/amr/m4a 格式
            rate (int, optional): 采样率。 16000 或 8000， 默认 16000
            model (str, optional): 识别模型. "mandarin_near": 普通话近场识别模型, "english": 英语模型,
                "cantonese": 粤语模型, "sichuan": 四川话模型, "mandarin_far": 普通话远场模型

        Returns:
            tuple: (bool, str), 若识别成功，则第一项为 True，第二项为识别结果。
                若识别失败，则第一项为 False，第二项为错误信息。
        """
        _format = file[-3:]
        speech_data = []
        with open(file, 'rb') as speech_file:
            speech_data = speech_file.read()

        length = len(speech_data)
        if length == 0:
            raise SRError(f"文件 {file} 读取 0 字节")

        speech = base64.b64encode(speech_data)
        speech = str(speech, 'utf-8')
        params = {
            'custId': self.custId,
            'apiKey': self.apiKey,
            'dev_pid': dev_pid[model],
            'format': _format,
            'rate': rate,
            'cuid': self.cuid,
            'channel': 1,
            'speech': speech,
            'len': length
        }
        post_data = json.dumps(params, sort_keys=False)
        req = Request(ASR_URL, post_data.encode('utf-8'))
        req.add_header('Content-Type', 'application/json')
        req.add_header('appId', 'v1')
        req.add_header('sign', 'a6e1f81461204ae8b64665fe04d4eef1')
        try:
            f = urlopen(req)
            result_str = f.read()
        except URLError as err:
            print('asr http response http code : ' + str(err.code))
            result_str = err.read()
        return _extract(result_str)


if __name__ == "__main__":
    CUSTID = "efPRTm6MHHOyRtMj"
    APIKEY = "FB65xcK78XMROsSerGgukmN4k10w8GuJ"

    # 需要识别的文件
    AUDIO_FILE = './audio/16k.pcm'  # 只支持 pcm/wav/amr 格式，极速版额外支持m4a 格式
    sr = SpeechRecognizer(CUSTID, APIKEY)
    ret = sr.inference(AUDIO_FILE)
    print(ret)
