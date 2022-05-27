import json
import struct
import gzip
import enum
from typing import Union
from ..encrypt.aes import aes_encrypt, aes_decrypt

'''
包头（0xEF 0xFE） + 控制码(2B) + 编号(2B) + 传输方式(1B) + 长度(4B) + 内容() + 校验和（1B） + 包尾(0xFE 0xEF)
    控制码(帧类型 + 包类型)
        帧类型
            0x00 请求帧
            0x01 回复帧
        包类型
            0x01 注册
            0x02 心跳
            0x03 数据
            0x04 文件
            0x05 控制
    传输方式
        0x00	字符串
        0x01	压缩字符串
        0x02	加密字符串
        0x03	加密压缩字符串
                
        0x20	Bytes字符串
        0x21	压缩Bytes字符串
        0x22	加密Bytes字符串
        0x23	加密压缩Bytes字符串
        
        0x30	Json字符串
        0x31	压缩Json字符串
        0x32	加密Json字符串
        0x33	加密压缩Json字符串

'''

class FRAME:
    START = 0   # 包头
    FRAME_TYPE = 2 # 帧类型
    PACKAGE_TYPE = 3  # 包类型
    FRAME_INDEX = 4  # 编号
    TRANSFER_TYPE = 6  # 传输方式
    CONTENT_LENGTH = 7  # 长度
    CONTENT = 11  # 内容
    SUM = -3 # 累加校验和
    END = -2  # 帧类型
    EXTRA_LENGTH = 14   # 附加长度

class FRAMEFLAG:
    START_FLAG = bytes.fromhex('EF FE')
    END_FLAG = bytes.fromhex('FE EF')

# 包类型
class PACKAGETYPE(enum.IntEnum):
    REGISTER = 1    # 注册
    HEARTBEAT = 2   # 心跳
    DATA = 3    # 数据
    FILE = 4    # 文件
    CONTROL = 5 # 控制

# 帧类型
class FRAMETYPE(enum.IntEnum):
    REQ = 0 # 请求
    ACK = 1 # 回复
    CONFIG = 2  # 确认包

# 传输方式
class TRANSFERTYPE(enum.IntEnum):

    TXT = 0x00 # 字符串
    TXT_COMPRESS = 0x01 # 压缩字符串
    TXT_ENCRYPT = 0x02 # 加密字符串
    TXT_COMPRESS_ENCRYPT = 0x03 # 加密压缩字符串

    BYTES = 0x20  # BYTES字符串
    BYTES_COMPRESS = 0x21  # 压缩BYTES字符串
    BYTES_ENCRYPT = 0x22  # 加密BYTES字符串
    BYTES_COMPRESS_ENCRYPT = 0x23  # 加密压缩BYTES字符串

    JSON = 0x30  # Json字符串
    JSON_COMPRESS = 0x31  # 压缩Json字符串
    JSON_ENCRYPT = 0x32  # 加密Json字符串
    JSON_COMPRESS_ENCRYPT = 0x33  # 加密压缩Json字符串

def convert_to_transfer_data(transfer_type: int, data: Union[str, bytes, dict], secret: str = '', encode: str = 'utf-8') -> bytes:
    if isinstance(data, str):
        data = data.encode(encode)
    if isinstance(data, dict):
        data = json.dumps(data, ensure_ascii=False).encode(encode)
    if transfer_type in [TRANSFERTYPE.TXT, TRANSFERTYPE.BYTES, TRANSFERTYPE.JSON]:
        return data
    elif transfer_type in [TRANSFERTYPE.TXT_COMPRESS, TRANSFERTYPE.JSON_COMPRESS, TRANSFERTYPE.BYTES_COMPRESS]:
        return gzip.compress(data)
    elif transfer_type in [TRANSFERTYPE.TXT_ENCRYPT, TRANSFERTYPE.JSON_ENCRYPT, TRANSFERTYPE.BYTES_ENCRYPT]:
        return aes_encrypt(data, secret)
    elif transfer_type in [TRANSFERTYPE.TXT_COMPRESS_ENCRYPT, TRANSFERTYPE.JSON_COMPRESS_ENCRYPT, TRANSFERTYPE.BYTES_COMPRESS_ENCRYPT]:
        return gzip.compress(aes_encrypt(data, secret))
    raise Exception(f"unsupport transfer_type({transfer_type})")

def convert_from_transfer_data(transfer_type: int, data: bytes, secret: str = '', encode: str = 'utf-8') -> Union[str, bytes, dict]:
    if transfer_type == TRANSFERTYPE.TXT:
        return data.decode(encode)
    elif transfer_type == TRANSFERTYPE.TXT_COMPRESS:
        return gzip.decompress(data).decode(encode)
    elif transfer_type == TRANSFERTYPE.TXT_ENCRYPT:
        return aes_decrypt(data, secret).decode(encode)
    elif transfer_type == TRANSFERTYPE.TXT_COMPRESS_ENCRYPT:
        return aes_decrypt(gzip.decompress(data), secret).decode(encode)
    elif transfer_type == TRANSFERTYPE.BYTES:
        return data
    elif transfer_type == TRANSFERTYPE.BYTES_COMPRESS:
        return gzip.decompress(data)
    elif transfer_type == TRANSFERTYPE.BYTES_ENCRYPT:
        return aes_decrypt(data, secret)
    elif transfer_type == TRANSFERTYPE.BYTES_COMPRESS_ENCRYPT:
        return aes_decrypt(gzip.decompress(data), secret)
    elif transfer_type == TRANSFERTYPE.JSON:
        return json.loads(data.decode(encode))
    elif transfer_type == TRANSFERTYPE.JSON_COMPRESS:
        return json.loads(gzip.decompress(data).decode(encode))
    elif transfer_type == TRANSFERTYPE.JSON_ENCRYPT:
        return json.loads(aes_decrypt(data, secret).decode(encode))
    elif transfer_type == TRANSFERTYPE.JSON_COMPRESS_ENCRYPT:
        return json.loads(aes_decrypt(gzip.decompress(data), secret).decode(encode))
    else:
        raise Exception(f"unsupport transfer_type({transfer_type})")

# 包头固定长度
def get_pack_header_length() -> int:
    return int(FRAME.CONTENT - FRAME.FRAME_TYPE)

# 包头起始长度
def get_pack_start_length() -> int:
    return int(FRAME.FRAME_TYPE - FRAME.START)

def convert_bytes_to_int(data: bytes) -> int:
    return struct.unpack('L', data[:4])[0]

# 组包
def pack_frame(packs: dict, secret: str='') -> bytes:
    if isinstance(packs, dict):
        frame_type = packs.get('frame_type')
        if frame_type is None:
            raise Exception(f"No Params(frame_type)")

        package_type = packs.get('package_type')
        if package_type is None:
            raise Exception(f"No Params(package_type)")

        package_index = packs.get('package_index')
        if package_index is None:
            raise Exception(f"No Params(package_index)")

        transfer_type = packs.get('transfer_type')
        if transfer_type is None:
            raise Exception(f"No Params(transfer_type)")

        data = packs.get('data')
        if data is None:
            raise Exception(f"No Params(data)")

        data = convert_to_transfer_data(transfer_type, data, secret)

        length = len(data)
        if length > 0:
            packs = bytearray(length + FRAME.EXTRA_LENGTH)
            packs[FRAME.START: FRAME.START + 2] = FRAMEFLAG.START_FLAG  # 包头
            packs[FRAME.FRAME_TYPE] = frame_type  # 帧类型
            packs[FRAME.PACKAGE_TYPE] = package_type  # 包类型
            packs[FRAME.FRAME_INDEX: FRAME.FRAME_INDEX + 2] = struct.pack('H', package_index)  # 编号
            packs[FRAME.TRANSFER_TYPE] = transfer_type  # 传输方式
            packs[FRAME.CONTENT_LENGTH: FRAME.CONTENT_LENGTH + 4] = struct.pack('L', length)  # 长度
            packs[FRAME.CONTENT: FRAME.CONTENT + length] = data
            packs[FRAME.CONTENT + length] = sum(data) & 0xFF
            packs[FRAME.END:] = FRAMEFLAG.END_FLAG
            return packs
        raise Exception(f"Invalid length({len(data)}<=0)")
    raise Exception(f"Invalid Type")

# 解包
def unpack_frame(data: bytes, secret: str='') -> dict:
    length = len(data)
    if length > FRAME.EXTRA_LENGTH:
        packs = {}
        if data[FRAME.START: FRAME.START + 2] == FRAMEFLAG.START_FLAG and data[FRAME.END:] == FRAMEFLAG.END_FLAG:
            content_length = struct.unpack('L', data[FRAME.CONTENT_LENGTH: FRAME.CONTENT_LENGTH + 4])[0]
            if length == content_length + FRAME.EXTRA_LENGTH:
                content = data[FRAME.CONTENT: FRAME.CONTENT + content_length]
                if sum(content) & 0xFF == data[FRAME.CONTENT + content_length]:    # 校验和
                    packs['frame_type'] = data[FRAME.FRAME_TYPE]
                    packs['package_type'] = data[FRAME.PACKAGE_TYPE]
                    packs['package_index'] = struct.unpack('H', data[FRAME.FRAME_INDEX: FRAME.FRAME_INDEX + 2])[0]
                    packs['transfer_type'] = data[FRAME.TRANSFER_TYPE]
                    packs['data'] = convert_from_transfer_data(packs['transfer_type'], data[FRAME.CONTENT: FRAME.CONTENT + content_length], secret)
                    return packs
                raise Exception(f"Invalid SumCheck")
            raise Exception(f"Invalid length({content_length} + {FRAME.EXTRA_LENGTH} != {length})")
        raise Exception(f"Invalid Start or End")
    raise Exception(f"Invalid length({len(data)}<{FRAME.EXTRA_LENGTH})")
