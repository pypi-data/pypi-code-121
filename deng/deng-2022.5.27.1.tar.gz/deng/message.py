"""发送企业微信通知"""
# coding = utf-8
import logging
import requests


logger = logging.getLogger("DengUtils")


def send_wechat_message(message: dict, receiver: str):
    """发送企业微信消息"""
    url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send"
    res = requests.post(url, params={"key": receiver}, json=message)
    if res.status_code == 200 and res.json()["errcode"] == 0:
        logger.info(f"发送企业微信通知成功")
    else:
        logger.error(f"发送企业微信通知失败：{res.text}")


def send_text_alert_message(app_name: str, message: str, receiver: str):
    """发送文本告警消息，@所有人"""
    _alert_message = {
        "msgtype": "text",
        "text": {"content": f"消息来源：{app_name}，\n{message}", "mentioned_list": ["@all"]},
    }
    send_wechat_message(message=_alert_message, receiver=receiver)
