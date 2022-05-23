import asyncio
import time

import websockets
from flask import Flask, request
import json
import _thread
app = Flask(__name__)

cmd_queue = asyncio.Queue()
text_queue = asyncio.Queue()


async def ws_send_cmd(websocket):
    while True:
        try:
            if not cmd_queue.empty():
                send_cmd = await cmd_queue.get()
                print("> send cmd: ", send_cmd)
                await websocket.send("5" + json.dumps(send_cmd))
            else:
                await asyncio.sleep(0.1)
                continue
        except Exception as e:
            await asyncio.sleep(0.1)
            print("get cmd queue error", e.__str__())


async def ws_send_text(websocket):
    while True:
        try:
            if not text_queue.empty():
                send_text = await text_queue.get()
                print("> send text: ", send_text)
                await websocket.send("5" + json.dumps(send_text))
            else:
                await asyncio.sleep(0.1)
                continue
        except Exception as e:
            await asyncio.sleep(0.1)
            print("get text queue error", e.__str__())


async def ws_recv_handler(websocket):
    while True:
        try:
            recv_msg = await asyncio.wait_for(websocket.recv(), timeout=0.1)
            if not recv_msg or recv_msg == '':
                await  asyncio.sleep(0.1)
                continue
            print("< receive_msg: ", recv_msg)
            package_cmd = recv_msg[0]
            if package_cmd == '3':
                print("> send_msg: ", '4')
                await  websocket.send('4')
            if package_cmd == '5':
                package = json.load(package_cmd[1:])
                ack = {
                   'msgId': package['header']['msgId']
                }
                print("> send_msg: ", '6'+json.dumps(ack))
                await websocket.send('6' + json.dumps(ack))
            if package_cmd == '6':
                pass
        except Exception as e:
            print(e.__str__())


async def serve(websocket, path):
    await asyncio.gather(
        ws_send_cmd(websocket),
        ws_send_text(websocket),
        ws_recv_handler(websocket)
    )


def start_ws_server(addr, port):
    event_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(event_loop)
    start_server = websockets.serve(serve, addr, port)
    event_loop.run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()


@app.route('/cmd/send', methods=['POST'])
def send_cmd():
    data = json.loads(request.data.decode('utf-8'))
    cmd_queue.put_nowait(data)
    resp = {'cmd': data,
            'success': True}
    return json.dumps(resp)


@app.route('/text/send', methods=['POST'])
def send_text():
    data = json.loads(request.data.decode('utf-8'))
    text_queue.put_nowait(data)
    resp = {'text': data, 'success': True}
    return json.dumps(resp)


def start_flask():
    app.run(host='0.0.0.0', port=8901)


if __name__ == "__main__":
    _thread.start_new_thread(start_flask, ())
    start_ws_server('localhost', 8101)
