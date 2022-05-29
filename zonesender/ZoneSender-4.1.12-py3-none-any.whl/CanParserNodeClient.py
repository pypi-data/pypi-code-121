import json
import typing

import grpc

from . import ZoneSenderData
from .ObjIo import *

from .Protos import CanParserNode_pb2, CanParserNode_pb2_grpc


class CanParserNodeClient(object):
    def __init__(self) -> None:
        """ CanParserNode 的客户端
        """
        self._canDbParserStub = CanParserNode_pb2_grpc.CanParserNodeStub(
            channel=grpc.insecure_channel(
                target='{0}:{1}'
                    .format(
                        ZoneSenderData.CAN_PARSERNODE_NODE_IP, 
                        ZoneSenderData.CAN_PARSERNODE_NODE_PORT),
                options = ZoneSenderData.GRPC_OPTIONS
            )
        )

    def AddCanDbFile(self, db_path: 'str') -> 'int':
        ''' 添加一个DB文件

        :param db_path: str CAN DB 的文件路径
        :return: int

            - 0: 成功

            - 1: 解析失败

            - 2: 文件类型不能识别

            - 1000: error
        '''
        try:
            res_ = self._canDbParserStub.AddDbFile(
                CanParserNode_pb2.db_path(
                    db_path = db_path,
                )
            )
            print('AddCanDbFile result: {0}, reason: {1}'.format(res_.result, res_.reason))
            return res_.result
        except Exception as e_:
            print(e_)
            return 1000

    def SetDBConfig(self, config_d: 'dict') -> 'int':
        ''' 设置 channel 与 CAN DB 的 Mapping

        :param config_d: dict 例如

            {0: 'PTCANFD',

            1: 'BOCAN'}

        :return: int

            - 0: 成功

            - 1000: error
        '''
        try:
            l_ = list()
            for channel_, cluster_name_ in config_d.items():
                l_.append(CanParserNode_pb2.db_config_pair(
                    channel = channel_,
                    db_name = cluster_name_,
                ))
            res_ = self._canDbParserStub.SetConfig(
                CanParserNode_pb2.db_configs(
                    configs = l_
                )
            )
            print('SetCanDbConfig result: {0}, reason: {1}'.format(res_.result, res_.reason))
            return res_.result
        except Exception as e_:
            print(e_)
            return 1000

    def ClearCanDb(self) -> 'int':
        ''' 清除所有的CANDB配置

        :return: int

            - 0: 成功

            - 1000: error
        '''
        try:
            res_ = self._canDbParserStub.Clear(
                CanParserNode_pb2.Common__pb2.empty()
            )
            print('清除所有 CANDB 配置 result: {0}, reason: {1}'.format(res_.result, res_.reason))
            return res_.result
        except Exception as e_:
            print(e_)
            return 1000

    def ClearSubscribe(self) -> 'int':
        ''' 清除 CanparserNode 的订阅客户端

        :return: int

            - 0: 成功

            - 1000: error
        '''
        try:
            res_ = self._canDbParserStub.ClearSubscribe(
                CanParserNode_pb2.Common__pb2.empty()
            )
            print('清除所有 CanParser 的订阅 result: {0}, reason: {0}'.format(res_.result, res_.reason))
            return res_.result
        except Exception as e_:
            print(e_)
            return 1000

    def GetMqttTopicTreeJson(self, return_d: 'dict') -> 'int':
        ''' 获取所有的 Mqtt Tree dict 对象
        如果获取成功，将会在 return_d 中填充 TopicTree dict

        :param return_d: 要返回的 Mqtt Topic Tree 字典
        :return: int

            - 0: 获取成功

            - 1000: error
        '''
        try:
            res_ = self._canDbParserStub.GetMqttTopicTreeJson(
                CanParserNode_pb2.Common__pb2.empty()
            )
            if (not res_.result.result == 0):
                return res_.result.result
            parser_json_str_ = res_.str_json
            return_d.clear()
            return_d.update(json.loads(parser_json_str_))
            return res_.result.result
        except Exception as e_:
            print(e_)
            return 1000

    def CanEncode(self, can_obj) -> 'int':
        ''' 对 CAN 对象进行编码
        
        :param can_obj: 要编码的 CAN Obj 可能是 ZoneSender.ObjIo.CanISignalPdu
        :return: int\n
            - 0              编码成功\n
            - \-1             类型不对\n
            - 1              找不到对应的通道\n
            - 2              找不到对应的 PDU 名字\n
            - 3              找不到 PDU context 中指定的信号名\n
            - 1000           Error\n
        '''
        try:
            if (isinstance(can_obj, CanISignalIPdu)):
                res_ = self._canDbParserStub.EncodePdu(
                    CanParserNode_pb2.i_signal_i_pdu_obj(
                        channel=can_obj.channel,
                        pdu_name=can_obj.name,
                        pdu_context=json.dumps(can_obj.context)
                    )
                )
                result_ = res_.result.result
                if (result_ == 0):
                    can_obj.data = res_.data
                else:
                    print(res_.result.reason)
                return result_
            else:
                return -1
        except Exception as e_:
            print(e_)
            return 1000