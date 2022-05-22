from enum import Enum
import enum
import hashlib
import copy

class Protocol:
    def __init__(self, protocolver='td-protocol1.0', charset='utf-8'):
        self.ver = protocolver  # 协议版本
        self.index = -1  # 包序号
        self.charset = charset  # 数据块编码
        self.dataLength = 0  # 数据块长度
        self.dataMd5 = None  # 数据哈希
        self.data = b''  # 数据

    def decode(self):
        '''
            将封装好的协议包转为bytes数据准备发送
        '''
        m_str = ''
        for item in self.__dict__:
            m_str += str(self.__dict__[item]) + '\r'
        return bytes(m_str, encoding=self.charset)

    def encode(self, buff: str, index=0, charset='utf-8'):
        '''
            对数据进行协议封装
        '''
        self.data = buff
        m_md5 = hashlib.md5()
        m_md5.update(buff.encode(encoding=charset))
        self.dataMd5 = m_md5.hexdigest()
        self.dataLength = len(self.data)
        self.charset = charset
        self.index = index

    def checkMD5(self):
        m_md5 = hashlib.md5()
        m_md5.update(self.data.encode(encoding=self.charset))
        if self.dataMd5 == m_md5.hexdigest():
            return True
        else:
            return False

    def clear(self):
        self.index = -1  # 包序号
        self.charset = ''  # 数据块编码
        self.dataLength = 0  # 数据块长度
        self.dataMd5 = None  # 数据哈希
        self.data = b''  # 数据


class analysis:
    def __init__(self, protocol: Protocol):
        self._protocol = protocol  # 协议
        self._buff = b''  # 接受缓存
        self._buffOffset = 0  # 数据缓存游标
        self._counter = 0  # 包头计数器
        self.state = ANALYSIS_STATUS.WAIT_RECV_HEADER  # 状态
        self._recvDataLength = 0  # 获取数据长度
        self.RecvPacketList = []  # 已经接收包列表

    def recv(self, buffer: bytes):
        self._buff += buffer
        self._getData()

    def _getData(self):
        while True:
            if self._buffOffset >= len(self._buff):
                break
            m_buff = self._buff[self._buffOffset:len(self._buff)]
            try:
                m_offset = m_buff.index(b'\r')
            except Exception as e:
                m_offset = 0
            if m_offset <= 0:
                break
            else:
                if self._counter == 0:
                    self.state= ANALYSIS_STATUS.WAIT_RECV_HEADER
                    self._protocol.ver = bytes.decode(
                        m_buff[0:m_offset], encoding='utf-8')
                elif self._counter == 1:
                    self._protocol.index = int(bytes.decode(
                        m_buff[0:m_offset], encoding='utf-8'))
                elif self._counter == 2:
                    self._protocol.charset = bytes.decode(
                        m_buff[0:m_offset], encoding='utf-8')
                elif self._counter == 3:
                    self._protocol.dataLength = int(bytes.decode(
                        m_buff[0:m_offset], encoding='utf-8'))
                elif self._counter == 4:
                    self._protocol.dataMd5 = bytes.decode(
                        m_buff[0:m_offset], encoding='utf-8')
                    self.state = ANALYSIS_STATUS.GET_DATA
                elif self._counter == 5:
                    self._protocol.data = m_buff[0:m_offset]
                    self.state = ANALYSIS_STATUS.RECV_COMPLETE
                self._buffOffset += m_offset+1
                self._counter += 1
                if self.state == ANALYSIS_STATUS.RECV_COMPLETE:
                    self.__getDataComplete()

    def __getDataComplete(self):
        self.RecvPacketList.append(copy.deepcopy(self._protocol))
        self._protocol.clear()
        self._recvDataLength = 0
        self._buff = self._buff[self._buffOffset:len(self._buff)]
        self._buffOffset = 0
        self._counter = 0
        self.state = ANALYSIS_STATUS.RECV_COMPLETE

    def getRecvData(self):
        m_ret = []
        while True:
            m_ret.append(self.RecvPacketList[0])
            del(self.RecvPacketList[0])
            if len(self.RecvPacketList) == 0:
                break
        return m_ret

    def resetState(self):
        self.state = ANALYSIS_STATUS.WAIT_RECV_HEADER

    def getSendBuffer(self):
        return self._protocol.decode()


class ANALYSIS_STATUS(Enum):
    ERROR = 0
    WAIT_RECV_HEADER = 1
    GET_DATA = 2
    RECV_COMPLETE = 3
