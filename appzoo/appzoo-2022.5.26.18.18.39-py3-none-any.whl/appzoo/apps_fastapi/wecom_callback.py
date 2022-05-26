#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AppZoo.
# @File         : wecom_callback
# @Time         : 2022/3/24 下午3:15
# @Author       : yuanjie
# @WeChat       : 313303303
# @Software     : PyCharm
# @Description  :

from flask import Flask, request
from wecom.tx import WXBizMsgCrypt
import xml.etree.cElementTree as ET
from meutils.pipe import *

app = Flask(__name__)

############################################################################
sToken = 'Rt1GEhMOXt1Ea'
sEncodingAESKey = 'so4rZ1IBA3cYXEvWZHciWd2oFs1qdZeN3UNExD5UmDK'
sCorpID = 'ww3c6024bb94ecef59'
wxcpt = WXBizMsgCrypt(sToken, sEncodingAESKey, sCorpID)


############################################################################

@app.route('/index', methods=['GET', 'POST'])
def index():
    # 获取url验证时微信发送的相关参数
    sVerifyMsgSig = request.args.get('msg_signature')
    sVerifyTimeStamp = request.args.get('timestamp')
    sVerifyNonce = request.args.get('nonce')
    sVerifyEchoStr = request.args.get('echostr')

    logger.info(f"sVerifyEchoStr: {sVerifyEchoStr}")
    #
    sReqMsgSig = sVerifyMsgSig
    sReqTimeStamp = sVerifyTimeStamp
    sReqNonce = sVerifyNonce

    # 验证url
    if request.method == 'GET':
        ret, sEchoStr = wxcpt.VerifyURL(sVerifyMsgSig, sVerifyTimeStamp, sVerifyNonce, sVerifyEchoStr)
        print(type(ret))
        print(type(sEchoStr))
        if (ret != 0):
            print(f"ERR: VerifyURL ret:{ret}")
            sys.exit(1)
        return sEchoStr

    # 接收客户端消息
    if request.method == 'POST':
        # sReqMsgSig = request.form.get('msg_signature')
        # sReqTimeStamp = request.form.get('timestamp')
        # sReqNonce = request.form.get('nonce')
        # 赋值url验证请求相同的参数，使用上面注释掉的request.form.get方式获取时，测试有问题

        sReqData = request.data
        print(sReqData)
        ret, sMsg = wxcpt.DecryptMsg(sReqData, sReqMsgSig, sReqTimeStamp, sReqNonce)
        if (ret != 0):
            print("ERR: VerifyURL ret:")
            sys.exit(1)
        # 解析发送的内容并打印
        xml_tree = ET.fromstring(sMsg)
        content = xml_tree.find("Content").text
    ##############################图灵机器人

    url = 'http://www.tuling123.com/openapi/api'
    a = requests.get(url, dict(key='3ac26126997942458c0d93de30d52212', info=content)).json()
    content = a.get('text', content)

    logger.info(a)
    ##############################

    # 被动响应消息，将微信端发送的消息返回给微信端
    sRespData = f"""
            <xml>
            <ToUserName><![CDATA[mycreate]]></ToUserName>
            <FromUserName><![CDATA[wx177d1233ab4b730b]]></FromUserName>
            <CreateTime>1348831860</CreateTime>
            <MsgType><![CDATA[text]]></MsgType>
            <Content><![CDATA[{content}]]></Content>
            <MsgId>1234567890123456</MsgId>
            <AgentID>1</AgentID>
            </xml>"""
    ret, sEncryptMsg = wxcpt.EncryptMsg(sRespData, sReqNonce, sReqTimeStamp)
    if (ret != 0):
        print("ERR: EncryptMsg ret: " + ret)
        sys.exit(1)
    return sEncryptMsg


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000', debug=True)
