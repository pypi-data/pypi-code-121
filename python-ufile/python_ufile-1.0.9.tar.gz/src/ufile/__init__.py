"""Top-level package for ufile."""

__author__ = """Aria Bagheri"""
__email__ = 'ariab9342@gmail.com'
__version__ = '1.0.9'

import asyncio
import datetime
import json
import os
from itertools import starmap
from pathlib import Path
from typing import List, Callable, Awaitable, Any

import aiofiles
import aiohttp

CHUNK_SIZE = 5368709 * 2


class _Progress:
    last_update_at: datetime.datetime = None
    value: int = 0

    def __init__(self):
        pass

    def update(self, v: int):
        self.value += v

    def should_update(self):
        if not self.last_update_at:
            self.last_update_at = datetime.datetime.now()
        if self.last_update_at + datetime.timedelta(milliseconds=200) >= datetime.datetime.now():
            return False
        self.last_update_at = datetime.datetime.now()
        return True


class Ufile:
    api_key: str = ""
    fuid: str = ""
    progress_callback: Callable[[int, int], Awaitable[Any]] = None

    def __init__(self, api_key: str = "", progress_callback: Callable[[int, int], Awaitable[Any]] = None):
        self.api_key = api_key
        self.progress_callback = progress_callback

    @staticmethod
    async def split_file(file_name: str) -> List[str]:
        file_path = Path(file_name)
        num_chunks = 0
        if not os.path.exists("temp/"):
            os.mkdir("temp/")
        file_names_list = []
        async with aiofiles.open(file_name, 'rb') as f:
            while content := await f.read(CHUNK_SIZE):
                async with aiofiles.open(f"temp/{file_path.stem}.{num_chunks}{file_path.suffix}", mode="wb") as fw:
                    await fw.write(content)
                    file_names_list.append(fw.name)
                num_chunks += 1
        return file_names_list

    async def upload_file(self, file_name: str):
        file_path = Path(file_name)
        file_size = os.path.getsize(file_name)

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        if self.api_key:
            headers['X-API-KEY'] = self.api_key
        async with aiohttp.ClientSession() as session:
            async with session.post('https://store-eu-hz-3.ufile.io/v1/upload/create_session',
                                    data=f"file_size={file_size}", headers=headers) as response:
                response = await response.text()

                self.fuid = json.loads(response)['fuid']

            chunks = await self.split_file(file_name)

            progress = _Progress()

            async def upload_chunk(i, chunk):
                async with session.post('https://store-eu-hz-3.ufile.io/v1/upload/chunk',
                                        data={
                                            "chunk_index": f"{i + 1}",
                                            "fuid": self.fuid,
                                            "file": open(chunk, 'rb')
                                        }):
                    progress.update(os.path.getsize(chunk))
                    if self.progress_callback and progress.should_update():
                        await self.progress_callback(progress.value, file_size)
                    os.remove(chunk)

            def add_to_event_loop(j, c):
                return asyncio.get_event_loop().create_task(upload_chunk(j, c))

            tasks = starmap(add_to_event_loop, enumerate(chunks))

            await asyncio.gather(*tasks)

            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            data = {
                'fuid': self.fuid,
                'file_name': file_path.name,
                'file_type': file_path.suffix[1:],
                'total_chunks': len(chunks)
            }
            async with session.post('https://store-eu-hz-3.ufile.io/v1/upload/finalise',
                                    data=data, headers=headers) as response:
                loaded_content = await response.content.read()
                return json.loads(loaded_content)['url']

    async def download_file_link(self, slug):
        headers = {
            "X-API-KEY": self.api_key
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://ufile.io/v1/download/{slug}", headers=headers) as response:
                return await response.text()

    async def download_file(self, slug: str, download_address: str):
        headers = {
            "X-API-KEY": self.api_key
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://ufile.io/v1/download/{slug}", headers=headers) as response:
                link = await response.text()
                async with session.get(link) as download_response:
                    open(download_address, "wb").write(await download_response.content.read())
