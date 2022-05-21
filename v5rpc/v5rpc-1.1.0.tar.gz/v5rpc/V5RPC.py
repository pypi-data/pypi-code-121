import socket
import uuid
import v5rpc.IStrategy as IStrategy
from v5rpc.proto import API_pb2
from v5rpc.proto import DataStructures_pb2


class CacheItem:
    """
    保存上一个发送的包（UUID及内容）
    """

    def __init__(self) -> None:
        self.requestId = None  # UUID
        self.response = None  # bytes


class V5Server:
    """
    以UDP服务器接收平台发来的数据,解外层包（packet）以得到protobuf包装的内层信息.
    经过Transfer类处理,得到返回控制量,并经由packet包装发送.
    """

    def __init__(self, strategy: IStrategy, port: int) -> None:
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client.bind(("127.0.0.1", port))
        self.isDisposed = False
        self.breakFlag = False
        self.strategy = strategy
        self.lastResponse = CacheItem()  # CacheItem

    def run(self):
        if self.isDisposed:  # 其实不知道什么作用
            raise socket.error  # Disposed is True
        self.breakFlag = False  # 其实不知道什么作用
        while (not self.isDisposed) and (not self.breakFlag):
            try:
                data, address = self.client.recvfrom(1024)  # data为接收的数据
                in_packet = V5Packet()
                in_packet.bytes2packet(data)  # data经由packet解包
                if self.lastResponse.requestId == in_packet.requestId:  # 重发
                    response = self.lastResponse.response  # bytes类型
                else:
                    transfer = Transfer(self.strategy)
                    response = transfer.server_routine(in_packet.payload)
                    if response is None:
                        response = bytes()
                    self.lastResponse.requestId = in_packet.requestId
                    self.lastResponse.response = response
                out_packet = V5Packet()  # 发送出去的包
                out_packet.make_response_packet(response, in_packet.requestId)  # self.flags编码有问题
                self.client.sendto(out_packet.packet2bytes(), address)
            except socket.error:
                print("V5poster遇到socket_error")


class Transfer:
    """
    用于将包的信息交由strategy执行.
    包含反序列化,条件判断,将返回值序列化
    """

    def __init__(self, strategy: IStrategy) -> None:
        self.call = API_pb2.RPCCall()
        self.strategy = strategy

    def server_routine(self, protobuf_msg):
        self.call.ParseFromString(protobuf_msg)  # 反序列化,还原protobuf结构体
        case = self.call.WhichOneof("method")  # 返回被激活的one_of(protobuf)的名字,str

        if case == "on_event":
            self.strategy.on_event(self.strategy, self.call.on_event.type, self.call.on_event.arguments)

        elif case == "get_team_info":
            info = self.strategy.get_team_info(self.strategy, self.call.get_team_info.server_version)
            ver = DataStructures_pb2.Version.V1_1

            team_info_result = API_pb2.GetTeamInfoResult()  # 新建结构体
            team_info_result.team_info.version = ver  # 填充结构体
            team_info_result.team_info.team_name = info

            return team_info_result.SerializeToString()

        elif case == "get_instruction":
            wheel, control_info = self.strategy.get_instruction(self.strategy, self.call.get_instruction.field)
            instruction_result = API_pb2.GetInstructionResult()
            instruction_result.command.command = control_info  # 重置功能赋值

            for i in wheel:
                wheel_i_th = DataStructures_pb2.Wheel()
                wheel_i_th.left_speed = i[0]
                wheel_i_th.right_speed = i[1]
                instruction_result.wheels.append(wheel_i_th)

            return instruction_result.SerializeToString()

        elif case == "get_placement":
            placement = self.strategy.get_placement(self.strategy, self.call.get_placement.field)  # v5strategy函数中控制的placement
            placement_result = API_pb2.GetPlacementResult()

            placement_result.placement.ball.position.x = float(placement[5][0])
            placement_result.placement.ball.position.y = float(placement[5][1])
            for i in range(5):
                place_i_th = DataStructures_pb2.Robot()
                place_i_th.position.x = float(placement[i][0])
                place_i_th.position.y = float(placement[i][1])
                place_i_th.rotation = float(placement[i][2])
                place_i_th.wheel.left_speed = 0
                place_i_th.wheel.right_speed = 0  # python和C#的不同之处,python需要给l和r赋值0,才会出现wheel{},平台才可解析
                placement_result.placement.robots.append(place_i_th)
            return placement_result.SerializeToString()

        else:
            print("哪个也没进,麻了")


class V5Packet:
    """
    通讯信息的结构,以及将类的对象转为bytes的方法
    """
    MAGIC = 0x2b2b3556  # 魔数
    REPLY_MASK = 0x1

    def __init__(self) -> None:
        self.magic = None  # unsigned int
        self.requestId = None  # GUID
        self.flags = None  # byte
        self.length = None  # ushort
        self.payload = bytes()  # bytes
        self.Reply = None  # 不在包中

    def make_request_packet(self, payload: bytes):
        if len(payload) > 65535:
            raise ValueError  # 传输过长
        self.magic = self.MAGIC
        self.requestId = uuid.uuid1()
        self.flags = 0
        self.length = len(payload)
        self.payload = payload
        self.Reply = False
        self.assign_flag(self.REPLY_MASK, self.Reply)
        return self

    def make_response_packet(self, payload: bytes, request_id: uuid.UUID):
        if len(payload) > 65535:
            raise ValueError  # 传输过长
        self.magic = self.MAGIC
        self.requestId = request_id
        self.flags = 0
        self.length = len(payload)
        self.payload = payload
        self.Reply = True
        self.assign_flag(self.REPLY_MASK, self.Reply)
        return self

    def check_flag(self, mask: int):  # 对应原代码的get
        return (self.flags & mask) != 0

    def assign_flag(self, mask: int, x: bool):  # 对应原代码的set
        if x == True:
            self.flags = self.flags | mask
        else:
            self.flags = self.flags & (0b11111111 - mask)  # 相当于flag 与 (八位取反mask)

    def packet2bytes(self) -> bytes:
        press = self.MAGIC.to_bytes(4, byteorder="little", signed=False) + \
                self.requestId.bytes + \
                self.flags.to_bytes(1, byteorder="little", signed=False) + \
                self.length.to_bytes(2, byteorder="little", signed=False) + \
                self.payload
        return press

    def bytes2packet(self, press: bytes):
        self.magic = int.from_bytes(press[0:4], byteorder="little")
        self.requestId = uuid.UUID(bytes=press[4:20])
        self.flags = int.from_bytes(press[20:21], byteorder="little")
        self.length = int.from_bytes(press[21:23], byteorder="little")
        self.payload = press[23:]
        return self
