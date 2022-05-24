import asyncio
import json
from typing import List

import nbformat
from websockets.legacy.client import WebSocketClientProtocol

from nbr.schemas.message import Content
from nbr.schemas.result import ExecutionStatus, RunResult
from nbr.schemas.session import Session
from nbr.utils.message import create_message
from nbr.utils.websocket import connect_websocket


class Kernel:
    def __init__(self, *, session: Session) -> None:
        self._session: Session = session
        self._channel_tasks: List[asyncio.Task] = []
        self._status: ExecutionStatus = ExecutionStatus.WAITING

        self._websocket: WebSocketClientProtocol

        self._cells: List
        self._current_cell: int

    async def listen_server(self) -> None:
        """Listen server messages."""
        while True:
            msg = await self._websocket.recv()

            msg_json = json.loads(msg)
            content = msg_json["content"]

            if "data" in content:
                content["output_type"] = "execute_result"
                self._cells[self._current_cell].outputs = [
                    nbformat.NotebookNode(content)
                ]

            if "status" in content:
                self._cells[self._current_cell]["execution_count"] = (
                    self._current_cell + 1
                )
                self._current_cell += 1

            if (
                "status" in content
                and "execution_count" in content
                and content["execution_count"] == len(self._cells)
            ):
                self._status = ExecutionStatus.SUCCESS

                await self._stop()
                break

            if "status" in content and content["status"] == "aborted":
                self._status = ExecutionStatus.ERROR

                await self._stop()
                break

    async def start(self, base_url: str) -> None:
        self._websocket = await connect_websocket(
            base_url=base_url, session=self._session
        )
        self._channel_tasks.append(asyncio.create_task(self.listen_server()))

    async def _stop(self) -> None:
        self._channel_tasks[-1].cancel()
        await self._websocket.close()

    async def execute(self, cells: List[nbformat.NotebookNode]) -> RunResult:
        self._cells = cells
        self._current_cell = 0

        for cell in cells:
            code = cell["source"]

            content = Content(code=code)
            message = create_message(
                channel="shell",
                msg_type="execute_request",
                session=self._session.name,
                content=content,
            )

            await self._websocket.send(message)

        await asyncio.gather(*self._channel_tasks)

        return RunResult(status=self._status, cells=self._cells)
