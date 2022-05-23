import json
import os
import time
import typing
import uuid
from concurrent.futures import ThreadPoolExecutor

import grpc
import paho.mqtt.client as mqtt

from . import ZoneSenderData

from .ObjIo import *
from .ZoneSenderFramework import ZoneSenderFramework


class ZoneSenderStone(ZoneSenderFramework):
    def __init__(self) -> None:
        super().__init__()
        ########################################
        self._threadPool = ThreadPoolExecutor(2)
        self._mqttClient = mqtt.Client(
            client_id=uuid.uuid4().hex,
            transport='websockets')
        self._mqttClient.on_connect = self._OnMqttConnect
        self._mqttClient.on_message = self._OnMqttMessage
        self._mqttClient.on_disconnect = self._OnMqttDisconnect
        self._mqttClient.connect(ZoneSenderData.MQTT_BROKER_IP, ZoneSenderData.MQTT_BROKER_PORT)
        self._mqttClient.loop_start()
        
    def Subscribe(self, obj) -> None:
        ''' 订阅对象事件，只有订阅了相关对象，才能在后续的 OnXXX 回调函数中收到对应的对象接收事件

        :param obj: 需要订阅的对象，可以是如下类型\n
            - ZoneSender.ObjIo.CanMessage\n
            - ZoneSender.ObjIo.CanFrame\n
            - ZoneSender.ObjIo.CanSignal\n
            - ZoneSender.ObjIo.CanISignalIPdu\n
            - ZoneSender.ObjIo.SomeipPackage\n
        '''
        obj_ = obj
        if (isinstance(obj_, CanMessage)):
            self._mqttClient.subscribe('zonesender/canstacknode/message/{0}/{1}'.format(obj_.channel, hex(obj_.arbitration_id).lower()))
            self._mqttClient.publish(
                topic='zonesender/canstacknode/subscribe',
                payload=json.dumps({
                    'client_id': self._mqttClient._client_id.decode('utf-8'),
                    'channel': obj_.channel,
                    'arbitration_id': obj_.arbitration_id,
                }).encode('utf-8')
            )
        elif (isinstance(obj_, CanFrame)):
            self._mqttClient.subscribe('zonesender/canparsernode/frame/{0}/{1}'.format(obj_.channel, obj_.name))
            self._mqttClient.publish(
                topic='zonesender/canparsernode/subscribe',
                payload=json.dumps({
                    'client_id': self._mqttClient._client_id.decode('utf-8'),
                    'channel': obj_.channel,
                    'name': obj_.name,
                    'type': 'frame',
                }).encode('utf-8')
            )
        elif (isinstance(obj_, CanSignal)):
            self._mqttClient.subscribe('zonesender/canparsernode/signal/{0}/{1}'.format(obj_.channel, obj_.name))
            self._mqttClient.publish(
                topic='zonesender/canparsernode/subscribe',
                payload=json.dumps({
                    'client_id': self._mqttClient._client_id.decode('utf-8'),
                    'channel': obj_.channel,
                    'name': obj_.name,
                    'type': 'signal',
                }).encode('utf-8')
            )
        elif (isinstance(obj_, CanISignalIPdu)):
            self._mqttClient.subscribe('zonesender/canparsernode/pdu/{0}/{1}'.format(obj_.channel, obj_.name))
            self._mqttClient.publish(
                topic='zonesender/canparsernode/subscribe',
                payload=json.dumps({
                    'client_id': self._mqttClient._client_id.decode('utf-8'),
                    'channel': obj_.channel,
                    'name': obj_.name,
                    'type': 'pdu',
                }).encode('utf-8')
            )
        elif (isinstance(obj_, SomeipPackage)):
            if (obj_.serviceName == ''):
                print('不能订阅空的 someip service')
                return
            self._mqttClient.subscribe('zonesender/someipnode/someippackage/{0}'.format(obj_.serviceName))
            self._mqttClient.publish(
                topic='zonesender/someipnode/subscribe',
                payload=json.dumps({
                    'client_id': self._mqttClient._client_id.decode('utf-8'),
                    'service_name': obj_.serviceName
                }).encode('utf-8')
            )
    
    def UnSubscribe(self, obj) -> None:
        ''' 取消订阅事件，调用该函数后，将不会再 OnXXX 的回调函数中收到相关消息

        :param obj: 需要取消订阅的对象，可以为如下类型\n
            - ZoneSender.ObjIo.CanMessage\n
            - ZoneSender.ObjIo.CanFrame\n
            - ZoneSender.ObjIo.CanSignal\n
            - ZoneSender.ObjIo.CanISignalIPdu\n
            - ZoneSender.ObjIo.SomeipPackage\n
        '''
        obj_ = obj
        if (isinstance(obj_, CanMessage)):
            self._mqttClient.unsubscribe('zonesender/canstacknode/message/{0}/{1}'.format(obj_.channel, hex(obj_.arbitration_id).lower()))
            self._mqttClient.publish(
                topic='zonesender/canstacknode/unsubscribe',
                payload=json.dumps({
                    'client_id': self._mqttClient._client_id.decode('utf-8'),
                    'channel': obj_.channel,
                    'arbitration_id': obj_.arbitration_id,
                }).encode('utf-8')
            )
        elif (isinstance(obj_, CanFrame)):
            self._mqttClient.unsubscribe('zonesender/canparsernode/frame/{0}/{1}'.format(obj_.channel, obj_.name))
            self._mqttClient.publish(
                topic='zonesender/canparsernode/unsubscribe',
                payload=json.dumps({
                    'client_id': self._mqttClient._client_id.decode('utf-8'),
                    'channel': obj_.channel,
                    'name': obj_.name,
                    'type': 'frame',
                }).encode('utf-8')
            )
        elif (isinstance(obj_, CanISignalIPdu)):
            self._mqttClient.unsubscribe('zonesender/canparsernode/pdu/{0}/{1}'.format(obj_.channel, obj_.name))
            self._mqttClient.publish(
                topic='zonesender/canparsernode/unsubscribe',
                payload=json.dumps({
                    'client_id': self._mqttClient._client_id.decode('utf-8'),
                    'channel': obj_.channel,
                    'name': obj_.name,
                    'type': 'pdu',
                }).encode('utf-8')
            )
        elif (isinstance(obj_, CanSignal)):
            self._mqttClient.unsubscribe('zonesender/canparsernode/signal/{0}/{1}'.format(obj_.channel, obj_.name))
            self._mqttClient.publish(
                topic='zonesender/canparsernode/unsubscribe',
                payload=json.dumps({
                    'client_id': self._mqttClient._client_id.decode('utf-8'),
                    'channel': obj_.channel,
                    'name': obj_.name,
                    'type': 'signal',
                }).encode('utf-8')
            )
        elif (isinstance(obj_, SomeipPackage)):
            self._mqttClient.unsubscribe('zonesender/someipnode/someippackage/{0}'.format(obj_.serviceName))
            self._mqttClient.publish(
                topic='zonesender/someipnode/unsubscribe',
                payload=json.dumps({
                    'client_id': self._mqttClient._client_id.decode('utf-8'),
                    'service_name':obj_.serviceName
                }).encode('utf-8')
            )

    def OnCanFrame(self, timestamp: 'float', can_frame: 'CanFrame') -> None:
        ''' [需要用户重写实现定制功能]\n
        当收到一个 CAN 报文应该做什么，此函数在收到任何订阅过的 CAN 报文的时候触发

        :param timestamp: 收到该数据的时间戳
        :param can_frame: ZoneSender.ObjIo.CanFrame 收到的 CANFrame 对象
        '''
        pass

    def OnCanPdu(self, timestamp: 'float', can_pdu: 'CanISignalIPdu') -> None:
        ''' [需要用户重写实现定制功能]\n
        当收到一个 CAN PDU 应该做什么，此函数在收到任何订阅过的 CAN PDU 的时候触发

        :param timestamp: 收到该数据的时间戳
        :param can_pdu: ZoneSender.ObjIo.CanISignalIPdu 收到的 CanISignalIPdu 对象
        '''
        pass

    def OnCanSignal(self, timestamp: 'float', can_signal: 'CanSignal') -> None:
        ''' [需要用户重写实现定制功能]\n
        当收到一个 CAN Signal 应该做什么，此函数在收到任何订阅过的 CAN Signal 的时候触发

        :param timestamp: 收到该数据的时间戳
        :param can_signal: ZoneSender.ObjIo.CanSignal 收到的 CanSignal 对象
        '''
        pass

    def OnCanMessage(self, timestamp: 'float', can_message: 'CanMessage') -> None:
        ''' [需要用户重写实现定制功能]\n
        当收到一个 CAN Message 应该做什么，此函数在收到任何订阅过的 CAN Message 的时候触发

        :param timestamp: 收到该数据的时间戳
        :param can_message: ZoneSender.ObjIo.CanMessage 收到的 CanMessage 对象
        '''
        pass

    def OnSomeipPackage(self, timestamp: 'float', someip_package: 'SomeipPackage') -> None:
        ''' [需要用户重写实现定制功能]\n
        当收到一个 SomeipPackage 应该做什么，此函数在收到任何订阅过的 SomeipPackage 的时候触发

        :param timestamp: 收到该数据的时间戳
        :param someip_package: ZoneSender.ObjIo.SomeipPackage 收到的 SomeipPackage 对象
        '''
        pass

    def SendCan(self, obj, **kwargs) -> None:
        '''发送一条CAN报文, 数据将立刻发送

        :param obj: 要发送的 CAN 对象，可以是如下类型\n
            - ZoneSender.ObjIo.CanMessage\n
            - ZoneSender.ObjIo.CanISignalIPdu\n
        :param kwargs: 附加 key:value 型参数，有如下可能:\n
            - by: str 通过什么参数来发送，有如下可能:\n
                - 'data': 通过 obj.data 的数据来发送\n
                - 'context': 通过 obj.context 的数据来发送\n
        '''
        obj_ = obj
        try:
            if (isinstance(obj_, CanMessage)):
                d_ = {
                    'id': obj_.arbitration_id,
                    'ext': obj_.is_extended_id,
                    'rem': obj_.is_remote_frame,
                    'chl': obj_.channel,
                    'dlc': obj_.dlc,
                    'd': obj_.data,
                    'fd': obj_.is_fd,
                }
                self._mqttClient.publish(
                    topic='zonesender/canstacknode/requests/send_can_message',
                    payload=json.dumps(d_).encode('utf-8')
                )
            elif (isinstance(obj_, CanISignalIPdu)):
                d_ = {
                    'name': obj_.name,
                    'chl': obj_.channel,
                    'context': obj_.context,
                    'd': obj_.data,
                }
                d_['kwargs'] = kwargs
                self._mqttClient.publish(
                    topic='zonesender/canparsernode/requests/send_can_pdu',
                    payload=json.dumps(d_).encode('utf-8')
                )
        except Exception as e_:
            print(e_)

    def SetCycleSendTask(self, period_ms: 'int', obj, times: 'int' = -1) -> None:
        ''' 设置定时发送任务，定时把 obj 发送出去

        :param period_ms: 发送周期
        :param obj: 要发送的对象，支持以下类型\n
            - ZoneSender.ObjIo.CanMessage\n
            - ZoneSender.ObjIo.CanISignalIPdu\n
            - ZoneSender.ObjIo.CanFrame\n
        :param times: 发送的次数，规则如下\n
            - \-1(默认) 一直发送\n
            - 0 停止发送，可以对已经发送的对象设置0来停止发送\n
            - 任意正整数 N，连续发送 N 次\n
        :return: None
        '''
        period_ms_ = period_ms
        obj_ = obj
        times_ = times
        try:
            if (isinstance(obj_, CanMessage)):
                # 设置循环发送 CanMessage
                d_ = {
                    'name': obj_.name,
                    'id': obj_.arbitration_id,
                    'ext': obj_.is_extended_id,
                    'rem': obj_.is_remote_frame,
                    'chl': obj_.channel,
                    'dlc': obj_.dlc,
                    'd': obj_.data,
                    'fd': obj_.is_fd,
                    'times': times_,
                    'period': period_ms_,
                }
                self._mqttClient.publish(
                    topic='zonesender/canstacknode/requests/send_can_message_cyc',
                    payload=json.dumps(d_).encode('utf-8')
                )
            elif (isinstance(obj_, CanFrame)):
                # 设置循环发送 CanFrame
                d_ = {
                    'name': obj_.name,
                    'chl': obj_.channel,
                    'times': times_,
                    'period': period_ms_,
                    'd': [],    # TODO 暂时保留 d 来发送空数据，保持接口一致
                    'context': obj_.context,
                }
                self._mqttClient.publish(
                    topic='zonesender/canparsernode/requests/send_can_frame_cyc',
                    payload=json.dumps(d_).encode('utf-8')
                )
            elif (isinstance(obj_, CanISignalIPdu)):
                # 设置循环发送 CAN PDU
                d_ = {
                    'name': obj_.name,
                    'chl': obj_.channel,
                    'context': obj_.context,
                    'times': times_,
                    'period': period_ms_,
                }
                self._mqttClient.publish(
                    topic='zonesender/canparsernode/requests/send_can_pdu_cyc',
                    payload=json.dumps(d_).encode('utf-8')
                )
        except Exception as e_:
            print(e_)

    def SomeipCallAsync(self, someip_package: 'SomeipPackage') -> None:
        ''' 作为 Client调用，请求一个 someip method | get | set

        :param someip_package: 要发送的 SomeipPackage
        :return: None
        '''
        try:
            d_ = {
                'sv_name': someip_package.serviceName,
                'ince_id': someip_package.instanceId,
                'if_name': someip_package.interfaceName,
                'if_type': someip_package.interfaceType,
                'context': someip_package.context
            }
            self._mqttClient.publish(
                topic='zonesender/someipnode/request/call',
                payload=json.dumps(d_).encode('utf-8')
            )
        except Exception as e_:
            print(e_)

    def SomeipSetDefaultAnswer(self, someip_package: 'SomeipPackage') -> None:
        ''' 作为 Server 调用，设置后台 SomeIpServer 的数据

        :param someip_package: 要设置的 SomeipPackage
        :return: None
        '''
        try:
            d_ = {
                'sv_name': someip_package.serviceName,
                'ince_id': someip_package.instanceId,
                'if_name': someip_package.interfaceName,
                'if_type': someip_package.interfaceType,
                'context': someip_package.context
            }
            self._mqttClient.publish(
                topic='zonesender/someipnode/request/setvalue',
                payload=json.dumps(d_).encode('utf-8')
            )
        except Exception as e_:
            print(e_)

    def SomeipPublish(self, someip_package: 'SomeipPackage') -> None:
        ''' 作为 Server 调用，发送一次 Notification 或者 Event

        :param someip_package: 要发布的 SomeipPackage
        :return: None
        '''
        try:
            d_ = {
                'sv_name': someip_package.serviceName,
                'ince_id': someip_package.instanceId,
                'if_name': someip_package.interfaceName,
                'if_type': someip_package.interfaceType,
                'context': someip_package.context
            }
            self._mqttClient.publish(
                topic='zonesender/someipnode/request/publish',
                payload=json.dumps(d_).encode('utf-8')
            )
        except Exception as e_:
            print(e_)

    def _OnMqttMessage(self, client: mqtt.Client, userdata, msg: mqtt.MQTTMessage) -> None:
        '''当收到MQTTMwssage的时候做什么

        :param client: mqtt client
        :param userdata: None
        :param msg: mqtt.MQTTMessage
        '''
        topic_split_ = msg.topic.split('/')
        # print(msg.topic)
        # 消息分发
        if (topic_split_[1] == 'canstacknode'):
            recv_d_ = json.loads(msg.payload.decode('utf-8'))
            # 收到 CAN 数据
            if (topic_split_[2] == 'message'):
                # 收到 CANMessage
                self._DealWithCanMessage(recv_d_)
        elif (topic_split_[1] == 'canparsernode'):
            recv_d_ = json.loads(msg.payload.decode('utf-8'))
            # print(recv_d_)
            if (topic_split_[2] == 'frame'):
                # 收到 CanFrame
                self._DealWithCanFrame(recv_d_)
            elif (topic_split_[2] == 'signal'):
                # 收到CANSIgnal
                self._DealWithCanSignal(recv_d_)
            elif (topic_split_[2] == 'pdu'):
                # 收到CANPdu
                self._DealWithCanISignalIPdu(recv_d_)
        elif (topic_split_[1] == 'out'):
            print(msg.payload.decode('utf-8'))
        elif (topic_split_[1] == 'someipnode'):
            recv_d_ = json.loads(msg.payload.decode('utf-8'))
            if (topic_split_[2] == 'someippackage'):
                # 收到 SomeipPackage
                # print(recv_d_)
                self._DealWithSomeipPackage(recv_d_)

    def _OnMqttConnect(self, client: mqtt.Client, userdata, flags, rc) -> None:
        '''
        连接到 MQTT Broker 的时候做什么
        '''
        self._mqttClient.subscribe('zonesender/out/info')
        self._mqttClient.subscribe('zonesender/out/warn')
        self._mqttClient.subscribe('zonesender/out/error')
        self._mqttClient.subscribe('zonesender/out/debug')

    def _OnMqttDisconnect(self, client: mqtt.Client, userdata, rc) -> None:
        '''
        当断开与MQTT Broker 连接的时候做什么
        '''
        while (True):
            try:
                client.reconnect()
                break
            except Exception as e_:
                print(e_)
            time.sleep(2)

    def _DealWithCanMessage(self, recv_d: 'dict') -> None:
        '''
        处理接收到的 CaneMessage 消息
        '''
        can_msg_ = CanMessage(
            arbitration_id=recv_d['id'], 
            channel=recv_d['chl'], 
            dlc=recv_d['dlc'], 
            data=recv_d['d'],
            is_fd=recv_d['fd'],
            is_extended_id=recv_d['ext'],
            is_remote_frame=recv_d['rem'])
        self._threadPool.submit(
            self.OnCanMessage,
            recv_d['t'], can_msg_
        )

    def _DealWithCanFrame(self, recv_d: 'dict') -> None:
        '''
        处理收到的 CanFrame 消息
        '''
        can_frame_ = CanFrame(
            name=recv_d['name'],
            channel=recv_d['chl']
        )
        can_frame_.data = recv_d['d']
        can_frame_.dlc = recv_d['dlc']
        can_frame_.id = recv_d['id']
        self._threadPool.submit(
            self.OnCanFrame,
            recv_d['t'], can_frame_
        )

    def _DealWithCanISignalIPdu(self, recv_d: 'dict') -> None:
        '''
        处理收到的 CanISignalIPdu 消息
        '''
        can_pdu_ = CanISignalIPdu(
            name=recv_d['name'],
            channel=recv_d['chl']
        )
        can_pdu_.data = recv_d['d']
        self._threadPool.submit(
            self.OnCanPdu,
            recv_d['t'], can_pdu_
        )

    def _DealWithCanSignal(self, recv_d: 'dict') -> None:
        '''
        处理收到的 CanSignal 消息
        '''
        can_signal_ = CanSignal(
            name=recv_d['name'],
            channel=recv_d['chl'],
            data=recv_d['d'],
            unit=recv_d['u'],
            mean=recv_d['m'],
        )
        self._threadPool.submit(
            self.OnCanSignal,
            recv_d['t'], can_signal_
        )

    def _DealWithSomeipPackage(self, recv_d: 'dict') -> None:
        '''
        处理接收到的 SomeipPackage
        '''
        # print(recv_d)
        someip_package_ = SomeipPackage(recv_d['sv_name'])
        someip_package_.srcIp = recv_d['src_ip']
        someip_package_.srcPort = recv_d['src_port']
        someip_package_.destIp = recv_d['dest_ip']
        someip_package_.destPort = recv_d['dest_port']
        someip_package_.interfaceType = recv_d['type']
        someip_package_.serviceId = recv_d['sv_id']
        someip_package_.instanceId = recv_d['ince_id']
        someip_package_.interfaceId = recv_d['if_id']
        someip_package_.interfaceName = recv_d['if_name']
        someip_package_.context = recv_d['context']
        self._threadPool.submit(
            self.OnSomeipPackage,
            recv_d['t'], someip_package_
        )
