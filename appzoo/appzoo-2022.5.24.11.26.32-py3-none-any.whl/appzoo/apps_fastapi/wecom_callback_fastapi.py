#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AppZoo.
# @File         : wecom_callback_
# @Time         : 2022/3/24 下午3:46
# @Author       : yuanjie
# @WeChat       : 313303303
# @Software     : PyCharm`
# @Description  : https://www.freesion.com/article/91501334512/

from meutils.pipe import *
from wechatpy.enterprise import create_reply, parse_message
from wechatpy.enterprise.crypto import WeChatCrypto

import jieba

# ME
from appzoo import App
from fastapi import FastAPI, Form, Depends, File, UploadFile, Body, Request, Response, Form, Cookie

# 应用ID
# 回调模式里面随机生成的那个Token,EncodingAESKey
sCorp_Id = 'ww3c6024bb94ecef59'
sToken = 'Rt1GEhMOXt1Ea'
sEncodingAESKey = 'so4rZ1IBA3cYXEvWZHciWd2oFs1qdZeN3UNExD5UmDK'
crypto = WeChatCrypto(token=sToken, encoding_aes_key=sEncodingAESKey, corp_id=sCorp_Id)

app = App()


@app.api_route('/index', methods=['GET', 'POST'])
async def weixin(request: Request):
    logger.info(request.query_params)
    logger.info(request.method)

    msg_signature = request.query_params.get('msg_signature', '')
    timestamp = request.query_params.get('timestamp', '')
    nonce = request.query_params.get('nonce', '')
    echo_str = request.query_params.get('echostr', '')

    if request.method == 'GET':
        # 认证并对echo_str进行解密并返回明文
        echo_str = await crypto.check_signature(msg_signature, timestamp, nonce, echo_str)
        logger.info(echo_str)
        return echo_str

    # 收到
    raw_message = await request.body()
    logger.info(raw_message)

    decrypted_xml = crypto.decrypt_message(
        raw_message,
        msg_signature,
        timestamp,
        nonce
    )
    msg = parse_message(decrypted_xml)
    logger.info(msg)
    """
    TextMessage(OrderedDict([('ToUserName', 'ww3c6024bb94ecef59'), ('FromUserName', '7683'), ('CreateTime', '1648109637'), ('MsgType', 'text'), ('Content', '42156'), ('MsgId', '401559451'), ('AgentID', '1000041')]))
    """

    _msg = msg.content.strip()
    flag = params = None
    if _msg:
        _ = msg.content.split(maxsplit=1)
        flag = _[0]
        params = _[1:] | xjoin()

    # 回复
    if flag.__contains__('分词'):
        _msg = jieba.lcut(params.strip()) | xjoin()
        logger.info(_msg)

    xml = create_reply(str(_msg), msg).render()
    encrypted_xml = crypto.encrypt_message(xml, nonce, timestamp)

    return encrypted_xml


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000', debug=True)
