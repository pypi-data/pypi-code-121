import requests
import json
import time
from xes import common
#发送短信
def send_msg(mobile, content):

    if not isinstance(mobile, str) and not isinstance(mobile, int):
        raise Exception("参数必须为字符串或者数字")

    #如果输入了逗号，只给第一个手机号发短信
    if isinstance(mobile, str):
        mobile = mobile.split(",")[0]
    params1 = {"mobiles":mobile, "content": content}
    cookies = common.getCookies()

    headers = {"Cookie": cookies}
    rep = requests.get("https://code.xueersi.com/api/ai/python_sms/send", params=params1, headers=headers)
    repDic = common.jsonLoads(rep.text)
    if repDic is None:
        raise Exception("运营商状态报告超时,信息可能发送失败了")
    if repDic["stat"] != 1:
        raise Exception(repDic["msg"])

    if repDic["data"]["state"] == "SUCCESS":
        print("信息正在通过短信运营商发送，大约20S后可查看信息发送结果.....")
        time.sleep(5)
        params2 = {"batchId": repDic["data"]["batchId"], "mobile": mobile}
        for i in range(1, 5):
            rep2 = requests.get("https://code.xueersi.com/api/ai/python_sms/report", params=params2, headers=headers)
            repDic2 = json.loads(rep2.text)
            if repDic2["data"]["msg"] is not None:
                return repDic2["data"]["msg"]
            time.sleep(4)
    else:
        return repDic["data"]["msg"]

    return "运营商状态报告超时,信息可能发送失败了"
