import json
import typing

import grpc

from . import ZoneSenderData
from .ObjIo import *

from .Protos import SomeIpNode_pb2, SomeIpNode_pb2_grpc


class SomeipNodeClient(object):
    def __init__(self) -> None:
        """ SomeipNode 的客户端
        """
        self._someipNodeStub = SomeIpNode_pb2_grpc.SomeIpNodeStub(
            channel=grpc.insecure_channel(
                target='{0}:{1}'
                    .format(
                        ZoneSenderData.SOMEIP_STACK_NODE_IP, 
                        ZoneSenderData.SOMEIP_STACK_NODE_PORT),
                options = ZoneSenderData.GRPC_OPTIONS
            )
        )

    def StartSomeIpStack(self, ip_addr: 'str', iface: 'str') -> 'int':
        ''' 启动 SomeIp 协议栈

        :return: int\n
            - 0: 成功\n
            - 1000: error\n
        '''
        try:
            res_ = self._someipNodeStub.StartSomeIpStack(
                SomeIpNode_pb2.Common__pb2.net_info(
                    ip_addr = ip_addr,
                    iface = iface
                )
            )
            print('启动Someip协议栈, result: {0}, reason: {1}'.format(res_.result, res_.reason))
            return res_.result
        except Exception as e_:
            print(e_)
            return 1000

    def StopSomeIpStack(self) -> 'int':
        '''关闭 SomeIp 协议栈

        :return: int

            - 0: 成功

            - 1000: error
        '''
        try:
            res_ = self._someipNodeStub.StopSomeIpStack(
                SomeIpNode_pb2.Common__pb2.empty()
            )
            print('关闭SomeIp协议栈, result: {0}, reason:{1}'.format(res_.result, res_.reason))
            return res_.reason
        except Exception as e_:
            print(e_)
            return 1000

    def AddSomeIpArxml(self, arxml_path: 'str') -> 'int':
        ''' 添加一个 SomeIp Arxml 文件, 可以重复调用添加多个

        :return: int

            - 0: 成功

            - 1000: error
        '''
        try:
            res_ = self._someipNodeStub.AddSomeIpArxml(
                SomeIpNode_pb2.Common__pb2.file_path(
                    path = arxml_path
                )
            )
            print('加载 SomeIp Arxml 文件 result: {0}, reason: {1}'.format(res_.result, res_.reason))
            return res_.reason
        except Exception as e_:
            print(e_)
            return 1000

    def GetSomeIpServiceInfos(self, return_d: 'dict') -> 'int':
        ''' 获取当前已经加载的 SomeIp Arxml Info

        :param return_d: 如果获取成功，将会把获取的信息填充到该字典中
        :return: int\n
            - 0: 成功\n
            - 1000: error\n
        '''
        try:
            res_ = self._someipNodeStub.GetSomeIpServiceInfos(
                SomeIpNode_pb2.Common__pb2.empty()
            )
            if (not res_.result.result == 0):
                return res_.result.result
            return_d.clear()
            return_d.update(json.loads(res_.json_str_info))
            return res_.result.result
        except Exception as e_:
            print(e_)
            return 1000

    def UpdateSomeIpServiceConfig(
        self, 
        service_name: 'str', 
        instance_id: 'int', 
        service_type: 'str') -> 'int':
        ''' 更新SomeIp中服务的信息

        :param service_id: str SomeIp Service ID
        :param instance_id: int SomeIp Service Instance ID
        :param service_type: str 可以是 'consumer'|'provider' 表示该服务设置为什么类型
        :return: int\n
            - 0: 成功\n
            - 1000: error\n
        '''
        try:
            res_ = self._someipNodeStub.UpdateSomeipServiceConfig(
                SomeIpNode_pb2.service_tag(
                    service_name = service_name,
                    instance_id = instance_id,
                    service_type = service_type
                )
            )
            print('更新 SomeIp 服务设定 result: {0}, reason: {1}'.format(res_.result, res_.reason))
            return res_.result
        except Exception as e_:
            print(e_)
            return 1000

    def Reset(self) -> 'int':
        ''' 复位 SomeIp 协议栈，并清空 SomeIp 服务配置

        :return: int\n
            - 0: 成功\n
            - 1000: error\n
        '''
        try:
            res_ = self._someipNodeStub.Reset(
                SomeIpNode_pb2.Common__pb2.empty()
            )
            print('复位 SomeIp 协议栈 result: {0}, reason: {1}'.format(res_.result, res_.reason))
            return res_.result
        except Exception as e_:
            print(e_)
            return 1000

    def GetSomeIpStackStatus(self) -> 'int':
        '''获取当前 Someip Stack 的状态

        :return: int\n
            - 0 正在运行\n
            - 1 协议栈未启动\n
            - 2 协议栈未初始化\n
            - 1000 error
        '''
        try:
            res_ = self._someipNodeStub.GetSomeipStackStatus(
                SomeIpNode_pb2.Common__pb2.empty()
            )
            print('SomeipStack 的状态为 {0}'.format(res_.result))
            return res_.result
        except Exception as e_:
            print(e_)
            return 1000

    def SomeipCallSync(
        self, 
        someip_package_in: 'SomeipPackage', 
        someip_package_out: 'SomeipPackage', 
        timeout: 'int' = 1000,
        *args, **kwargs) -> 'int':
        ''' 同步调用 SomeipCall

        :param someip_package_in: 要调用的 SomeipPackage
        :param someip_package_out: 如果成功调用，则将返回的 SomeipPackage 填充到该对象中
        :param timeout: 超时参数，单位 ms
        :param by: str 设置使用什么来发送 Someip 'context'|'payload'
        :return: int\n
            - 0 正在运行\n
            - 1 超时\n
            - 1000 error
        '''
        try:
            d_ = someip_package_in.ToDict()
            d_.update({'by': kwargs.get('by', 'context')})
            d_.update({'payload': d_['payload'].hex()})
            res_ = self._someipNodeStub.SomeipCallSync(
                SomeIpNode_pb2.someip_call_context(
                    timeout = timeout,
                    str_context = json.dumps(d_)
                )
            )
            result_ = res_.result.result
            if (result_ == 0):
                # 成功回复
                recv_d_ = json.loads(res_.str_context)
                recv_d_.update({'payload': bytes.fromhex(recv_d_['payload'])})
                # print(recv_d_)
                # someip_package_out = SomeipPackage.From(recv_d_)
                SomeipPackage.CopyData(SomeipPackage.From(recv_d_), someip_package_out)
                return 0
            else:
                print(res_.result.reason)
                return result_
        except Exception as e_:
            print(e_)
            return 1000