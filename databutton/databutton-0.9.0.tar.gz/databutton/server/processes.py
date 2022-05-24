import asyncio
import logging
from typing import List

from fastapi import FastAPI, Response, WebSocket, status
from httpx import AsyncClient
from starlette.background import BackgroundTask
from starlette.responses import StreamingResponse
from websockets import WebSocketClientProtocol, connect

from databutton.decorators.streamlit import StreamlitApp
from databutton.utils.config import MAX_WEBSOCKET_MESSAGE_SIZE_IN_MB

_streamlit_processes = {}


async def start_processes(app: FastAPI, apps: List[StreamlitApp]):
    global _streamlit_processes
    for st in apps:
        p = StreamlitProcess(st.route, st.filename, st.port)
        await p.start()
        _streamlit_processes[p.route] = p

        p.add_route_to_app(app)


async def get_proxy(route: str, rest: str = "", port: int = 0):
    # Find correct app
    client = AsyncClient(base_url=f"http://localhost:{port}/")
    req = client.build_request("GET", rest)
    r = await client.send(req, stream=True)
    return StreamingResponse(
        r.aiter_raw(), background=BackgroundTask(r.aclose), headers=r.headers
    )


class StreamlitProcess:
    def __init__(self, route: str, fpath: str, port: int):
        self.port = port
        self.route = route
        self.fpath = fpath
        self.subprocess = None

    def stop(self):
        self.subprocess.kill()

    async def start(self):
        cmd = f"PYTHONPATH=. streamlit run {self.fpath} --server.port={self.port} --server.headless=true"
        self.subprocess = await asyncio.create_subprocess_shell(
            cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

    def add_route_to_app(self, app_to_add: FastAPI):
        @app_to_add.get(self.route + "{rest:path}")
        async def _get_app(rest: str):
            try:
                return await get_proxy(self.route, rest, self.port)
            except Exception as e:
                # Simply ignore messages. It's not this one's job to make sure it's up and running
                logging.debug("Error in http proxy", extra=e)

        @app_to_add.websocket(self.route + "stream")
        async def handle_proxied_websocket(ws_client: WebSocket):
            try:
                await ws_client.accept()
                port = self.port
                if port is None:
                    return Response(status_code=status.HTTP_404_NOT_FOUND)
                max_size = MAX_WEBSOCKET_MESSAGE_SIZE_IN_MB * int(1e6)
                async with connect(
                    f"ws://localhost:{port}/stream", max_size=max_size
                ) as ws_server:
                    fwd_task = asyncio.create_task(forward(ws_client, ws_server))
                    rev_task = asyncio.create_task(reverse(ws_client, ws_server))
                    await asyncio.gather(fwd_task, rev_task)
            except Exception as e:
                # Simply ignore messages. It's not this one's job to make sure it's up and running
                logging.debug("Error in websocket proxy", extra=e)


async def forward(ws_client: WebSocket, ws_server: WebSocketClientProtocol):
    while True:
        data = await ws_client.receive_bytes()
        await ws_server.send(data)


async def reverse(ws_client: WebSocket, ws_server: WebSocketClientProtocol):
    while True:
        data = await ws_server.recv()
        await ws_client.send_text(data)
