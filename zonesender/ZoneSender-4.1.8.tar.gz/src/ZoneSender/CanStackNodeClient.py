import os
import typing

import grpc

from . import ZoneSenderData
from .ObjIo import *

from .Protos import CanStackNode_pb2, CanStackNode_pb2_grpc


class CanStackNodeClient(object):
    def __init__(self) -> None:
        """ CanStackNode的客户端
        """
        self._canStub = CanStackNode_pb2_grpc.CanStackNodeStub(
            channel=grpc.insecure_channel(
                target='{0}:{1}'
                    .format(
                        ZoneSenderData.CAN_STACK_NODE_IP, 
                        ZoneSenderData.CAN_STACK_NODE_PORT),
                options = ZoneSenderData.GRPC_OPTIONS
            )
        )

    def SetConfigs(
        self,
        configs
        ) -> 'int':
        """ 设置 CAN 协议线的参数

        :param configs: typing.List[ZoneSender.ObjIo.CanStackConfig]
        :return: int

            - 0: 成功

            - 1000: error
        """
        try:
            configs_ = list()
            for config_ in configs:
                configs_.append(
                    CanStackNode_pb2.can_channel_config(
                        channel = config_.channel,
                        bitrate = config_.bitrate,
                        is_fd = config_.isFd,
                        fd_bitrate = config_.fdBitrate,
                        bus_type = config_.busType,
                        app_name = config_.appName,
                    )
                )
            res_ = self._canStub.SetConfigs(
                CanStackNode_pb2.can_channel_configs(
                    configs = configs_
                )
            )
            print('SetCanStackConfig result: {0}, reason: {1}'.format(res_.result, res_.reason))
            return res_.result
        except Exception as e_:
            print(e_)
            return 1000

    def StartCanStack(self) -> 'int':
        '''启动 CAN 协议栈

        :return: int

            - 0: 成功

            - 1000: error
        '''
        try:
            res_ = self._canStub.StartCanStack(CanStackNode_pb2.Common__pb2.empty())
            print('StartCanStack result: {0}, reason: {1}'.format(res_.result, res_.reason))
            return res_.result
        except Exception as e_:
            print(e_)
            return 1000

    def StopCanStack(self) -> 'int':
        ''' 关闭Can协议栈

        :return: int

            - 0: 成功

            - 1000: error
        '''
        try:
            res_ = self._canStub.StopCanStack(CanStackNode_pb2.Common__pb2.empty())
            print('StopCanStack result: {0}, reason: {1}'.format(res_.result, res_.reason))
            return res_.result
        except Exception as e_:
            print(e_)
            return 1000

    def ClearSend(self) -> 'int':
        '''关闭所有CAN循环任务

        :return: int

            - 0: 成功

            - 1000: error
        '''
        try:
            res_ = self._canStub.ClearSend(CanStackNode_pb2.Common__pb2.empty())
            print('ClearCanCycTask result: {0}, reason: {1}'.format(res_.result, res_.reason))
            return res_.result
        except Exception as e_:
            print(e_)
            return 1000

    def ClearSubscribe(self) -> 'int':
        ''' 清空订阅的客户端列表

        :return: int

            - 0: 成功

            - 1000: error
        '''
        try:
            res_ = self._canStub.ClearSubscribe(
                CanStackNode_pb2.Common__pb2.empty()
            )
            print('清除所有 CanStack 的订阅 result: {0}, reason: {0}'.format(res_.result, res_.reason))
            return res_.result
        except Exception as e_:
            print(e_)
            return 1000

    def StartLog(
        self, 
        name: 'str', 
        file_path: 'str', 
        channels: typing.List['int'],
        max_log_time_minute: 'int' = 60) -> 'int':
        ''' 启动一个记录任务

        :param name: str 该记录任务的名称，用于唯一标识一个记录任务
        :param file_path: str 要记录的文件存放的位置，必须注明记录的文件类型，如 xxx.blf
        :param channels: List['int'] 要记录的通道列表
        :max_log_time_minute: int 最大记录的分钟数 单位 min
        :return: int

            - 0: 成功

            - 1: 失败，未知的文件类型

            - 1000: error
        '''
        try:
            abs_file_path_ = os.path.abspath(file_path)
            res_ = self._canStub.StartLog(
                CanStackNode_pb2.log_start_request(
                    name = name,
                    file_path = abs_file_path_,
                    max_log_time_minute = max_log_time_minute,
                    channels = channels,
                )
            )
            print('StartLog reasut: {0} reason: {1}'.format(res_.result, res_.reason))
            return res_.result
        except Exception as e_:
            print(e_)
            return 1000

    def StopLog(
        self, 
        name: 'str') -> 'int':
        '''停止一个记录任务

        :param name: str 该记录任务的名称，传入之前启动记录任务使用的名称
        :return: int

            - 0: 成功

            - 1: 失败，找不到指定的记录任务

            - 1000: error
        '''
        try:
            res_ = self._canStub.StopLog(
                CanStackNode_pb2.log_stop_request(
                    name = name,
                )
            )
            print('StopLog result: {0}, reason: {1}'.format(res_.result, res_.reason))
            return res_.result
        except Exception as e_:
            print(e_)
            return 1000

    def ClearLogger(self) -> 'int':
        ''' 取消所有的记录任务

        :return: int

            - 0: 成功

            - 1: 失败，找不到指定的记录任务

            - 1000: error
        '''
        try:
            res_ = self._canStub.ClearLogger(CanStackNode_pb2.Common__pb2.empty())
            print('清除所有数据记录任务 result: {0}, reason: {1}'.format(res_.result, res_.reason))
            return res_.result
        except Exception as e_:
            print(e_)
            return 1000