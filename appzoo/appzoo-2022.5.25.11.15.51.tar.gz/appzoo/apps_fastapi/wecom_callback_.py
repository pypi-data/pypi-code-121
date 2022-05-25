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
from flask import abort, request
from wechatpy.enterprise import create_reply, parse_message
from wechatpy.enterprise.crypto import WeChatCrypto

from flask import Blueprint, Flask

import jieba

# 应用ID
# 回调模式里面随机生成的那个Token,EncodingAESKey
sCorp_Id = 'ww3c6024bb94ecef59'
sToken = 'Rt1GEhMOXt1Ea'
sEncodingAESKey = 'so4rZ1IBA3cYXEvWZHciWd2oFs1qdZeN3UNExD5UmDK'
crypto = WeChatCrypto(token=sToken, encoding_aes_key=sEncodingAESKey, corp_id=sCorp_Id)

app = Flask(__name__)


# 对应回调模式中的URL
@app.route('/index', methods=['GET', 'POST'])
def weixin():
    msg_signature = request.args.get('msg_signature', '')
    timestamp = request.args.get('timestamp', '')
    nonce = request.args.get('nonce', '')

    if request.method == 'GET':
        echo_str = signature(request)
        logger.info(echo_str)

        return echo_str

    # 收到
    raw_message = request.data

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


def signature(request):
    msg_signature = request.args.get('msg_signature', '')
    timestamp = request.args.get('timestamp', '')
    nonce = request.args.get('nonce', '')
    echo_str = request.args.get('echostr', '')
    print(request.args)
    try:
        # 认证并对echo_str进行解密并返回明文
        echo_str = crypto.check_signature(msg_signature, timestamp, nonce, echo_str)
        print(echo_str)
    except Exception as ex:
        print(ex)
        print(request)
        abort(403)
    return echo_str


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000', debug=True)
