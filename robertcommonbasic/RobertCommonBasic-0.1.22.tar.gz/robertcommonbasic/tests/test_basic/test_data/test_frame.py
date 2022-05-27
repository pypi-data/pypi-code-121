import base64
import os
import socket
from robertcommonbasic.basic.data.frame import FRAME, PACKAGETYPE, FRAMETYPE, TRANSFERTYPE, pack_frame, unpack_frame


def test():
    data = {'frame_type': FRAMETYPE.REQ, 'package_type': PACKAGETYPE.DATA, 'package_index': 1, 'transfer_type': TRANSFERTYPE.TXT_COMPRESS_ENCRYPT, 'data': '测试数据1'}
    packs = pack_frame(data, 'key1')
    data_ = unpack_frame(packs, 'key1')
    assert data_ == data

    data1 = {'frame_type': FRAMETYPE.REQ, 'package_type': PACKAGETYPE.DATA, 'package_index': 100, 'transfer_type': TRANSFERTYPE.BYTES_COMPRESS_ENCRYPT, 'data': '测试数据1'.encode('utf-8')}
    packs = pack_frame(data1, 'key1')
    data1_ = unpack_frame(packs, 'key1')
    assert data1_ == data1

    file_path = f"e:/service.rar"
    content = open(file_path, 'rb').read()
    content1 = base64.b64encode(content).decode()
    data2 = {'frame_type': FRAMETYPE.REQ, 'package_type': PACKAGETYPE.DATA, 'package_index': 101, 'transfer_type': TRANSFERTYPE.JSON_COMPRESS_ENCRYPT, 'data': {'name': os.path.basename(file_path), 'content': content1}}
    packs = pack_frame(data2)
    data2_ = unpack_frame(packs)
    assert data2_ == data2


    open(f"{os.path.dirname(file_path)}/copy_{os.path.basename(file_path)}", 'wb').write(base64.b64decode(data2.get('data').get('content').encode()))
    print(data2_)

    print()

def format_data(data: bytes):
    return ''.join(["%02X " % x for x in data]).strip()

def test_client():

    data = {'frame_type': FRAMETYPE.REQ, 'package_type': PACKAGETYPE.REGISTER, 'package_index': 1, 'transfer_type': TRANSFERTYPE.TXT_COMPRESS_ENCRYPT, 'data': 'testdtu'}
    data = pack_frame(data)
    data1 = format_data(data)

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('127.0.0.1', 9520))
    client.send(data)
    while True:
        data = client.recv(1024)  # 接收数据
        if data[0:2] == FRAME.START_FLAG and data[-2:] == FRAME.END_FLAG:
            file_path = f"e:/service.rar"
            content = base64.b64encode(open(file_path, 'rb').read()).decode()
            data2 = {'frame_type': FRAMETYPE.REQ, 'package_type': PACKAGETYPE.FILE, 'package_index': 2, 'transfer_type': TRANSFERTYPE.JSON_COMPRESS_ENCRYPT,'data': {'name': os.path.basename(file_path), 'content': content}}
            packs = pack_frame(data2)
            client.send(packs)
        print(data)

test()