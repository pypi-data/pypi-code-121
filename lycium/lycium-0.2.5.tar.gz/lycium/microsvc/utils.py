#!/usr/bin/env python
# encoding: utf-8

""" 
常用的辅助方法
"""
# from config import token_salt
from lycium.kafka.protocol.kafkapacket_pb2 import KafkaPacket
from lycium.microsvc.protocol.packagewrapper_pb2 import PackageWrapperRequest,PackageWrapperResponse
from lycium.microsvc.protocol import  packagewrapper_pb2
import jwt
import json
import logging

logger = logging.getLogger('microsvc')


def safe_string(s):
    """ 
    针对sql 语句，去掉转义字符
    """
    byte_str = s.encode("utf-8")
    return byte_str.decode("unicode_escape")

def verify_token(token:str,salt:str):
    """ 
    验证token的有效性
    """
    data = None
    try:
        data = jwt.decode(token,salt,verify=True,algorithms=['HS256'])
    except Exception as e:
        return False,None
    return True,data['name']

def decode_websocket_package(message:KafkaPacket):
    """ 
    对来自websocket 网关发过来的信息的body字段进行反序列化操作
    """
    if  "xhhk.com.deshengmen.biz" == message.replyTo or message.type == "protobuf":
        request = PackageWrapperRequest()
        request.ParseFromString(message.body)
        message.body=request.payload
        return request
        
    return None

def encode_websocket_package(body,request:PackageWrapperRequest):
    if request is not None:
        response = PackageWrapperResponse()
        response.uid.append(request.uid)
        response.personid.append(request.personid)
        response.mode=packagewrapper_pb2.Unicast
        response.useragent = request.useragent
        response.bizcode = request.bizcode
        response.requestid = request.requestid
        if isinstance(body,(dict,list)):
            body = json.dumps(body).encode('utf-8')
        if isinstance(body,str):
            body = body.encode('utf-8')
        
        response.payload = body
        return response.SerializeToString()
    else:
        return body
    

if __name__ == "__main__":
    verify_token("eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJuYW1lIjoiNjIzNDU4MTgyMzE5MTQ0OTYxIiwiZXhwIjoxNjEwMzQ4NDAwfQ.cHvs845OBs52cQJHknIPGqhNQykLGWX1mt2wHa0klCA")