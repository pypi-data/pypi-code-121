import time
import hmac
import hashlib
import base64
import urllib.parse
import requests
import json
from qrunner.utils.allure_data import AllureData
from qrunner.utils.config import conf


# 钉钉机器人
class Robot:
    def __init__(self, secret=None, url=None):
        self.secret = secret
        self.url = url

    # 生成时间戳timestamp和签名数据sign用于钉钉机器人的请求
    def __gen_timestamp_and_sign(self):
        timestamp = str(round(time.time() * 1000))
        secret_enc = self.secret.encode('utf-8')
        string_to_sign = '{}\n{}'.format(timestamp, self.secret)
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        return timestamp, sign

    # 发送钉钉机器人通知
    def send_msg(self, msg_data):
        # 从gen_timestamp_and_sign方法获取timestamp和sign
        timestamp, sign = self.__gen_timestamp_and_sign()
        # 机器人url
        robot_url = self.url
        # 拼接请求url
        url = '{0}&timestamp={1}&sign={2}'.format(robot_url, timestamp, sign)
        print(url)
        # 请求头
        headers = {'Content-Type': 'application/json'}
        # 发送请求
        ret = requests.post(url, headers=headers, data=json.dumps(msg_data), verify=False)
        # 判断请求结果
        ret_dict = ret.json()
        if ret_dict.get('errcode') == 0:
            print('消息发送成功')
        else:
            print('消息发送失败: {}'.format(ret_dict.get('errmsg')))

    # 从allure报告中获取数据并发送消息
    def send_report(self, msg_title, report_url):
        report_path = conf.get_item('common', 'report_path')
        allure_data = AllureData(report_path).get_basic_info()
        total = allure_data.get('total')
        passed = allure_data.get('passed')
        fail = allure_data.get('fail')
        rate = allure_data.get('rate')

        color_red = 'FF0000'
        color_green = '00FF00'
        if rate < 100:
            color_str = color_red
        else:
            color_str = color_green

        msg_title = f'{msg_title}({time.strftime("%m-%d %H:%M")})'
        result_text = "### {0}\n\n" \
                      "<font color=#C0C0C0>总数：</font>{1}，" \
                      "<font color=#C0C0C0>通过：</font><font color=#C0C0C0>{2}，</font>\n" \
                      "<font color=#C0C0C0>失败：</font><font color=#C0C0C0>{3}，</font>\n" \
                      "<font color=#C0C0C0>成功率：</font><font color=#{4}>{5}%</font>\n" \
                      "> #### [查看详情]({6})\n".format(msg_title, total, passed, fail, color_str, rate, report_url)
        msg_data = {
            "msgtype": "markdown",
            "markdown": {
                "title": msg_title,
                "text": result_text
            }
        }

        self.send_msg(msg_data)




