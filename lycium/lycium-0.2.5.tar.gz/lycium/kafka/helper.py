#!/usr/bin/env python
# coding: utf-8

class Helper(object):
    """
    辅助基类模块
    """

    def __init__(self):
        self._config = dict()


        self._partition = 0
        # 发送消息的状态，True 是成功发送，False 是发送失败
        self._send_error = None
        self._send_msg = None

    def config_servers(self, servers: list):
        """
        配置连接的服务器,如['localhost:9092']
        """
        self._config["bootstrap.servers"] = ",".join(servers)
        return self

    def config_partition(self, partition: int):
        """
        配置分区，如partition 为0
        """
        self._partition = partition
        return self

    def config_kerberos_service_name(self, name: str):
        """
        配置 kerberos.service.name
        使用kerberos 认证需要配置
        """
        self._config['kerberos.service.name'] = name
        return self

    def config_kerberos_keytab(self, path: str):
        """
        配置kerberos.keytab
        使用kerberos 认证需要配置
        """
        self._config['kerberos.keytab'] = path
        return self

    def config_kerberos_principal(self, value: str):
        """
        配置kerberos.principal
        使用kerberos 认证需要配置
        """
        self._config['kerberos.principal'] = value
        return self

    def config_security_protocol(self, protocol='sasl_plaintext'):
        """
        配置security.protocol
        使用plain 和kerberos 认证需要配置,使用默认即可
        """
        self._config['security.protocol'] = protocol
        return self

    def config_sasl_mechanisms(self, mechanism='PLAIN'):
        """
        配置 sasl.mechanisms
        使用plain 认证需要配置
        """
        self._config['sasl.mechanisms'] = mechanism
        return self

    def config_sasl_username(self, name):
        """
        配置 sasl.username
        使用plain 认证需要配置
        """
        self._config['sasl.username'] = name
        return self

    def config_sasl_password(self, password):
        """
        配置 sasl.password
        使用plain 认证需要配置
        """
        self._config['sasl.password'] = password
        return self

    def config_reconnect_interval(self, interval:int=500):
        """
        配置断线重连的时间间隔，单位是毫秒，默认是500
        """
        self._config['reconnect.backoff.ms'] = interval