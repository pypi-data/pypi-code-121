"""Main module."""
import json
import os
from multiprocessing.pool import ThreadPool
from pathlib import Path
from typing import List

import aiofiles
import requests as requests

CHUNK_SIZE = 5368709 * 2


class Ufile:
    api_key: str = ""
    fuid: str = ""

    def __init__(self, api_key: str = ""):
        self.api_key = api_key

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

        response = requests.post('https://store-eu-hz-3.ufile.io/v1/upload/create_session',
                                 data=f"file_size={file_size}", headers=headers)
        self.fuid = json.loads(response.content)['fuid']
        chunks = await self.split_file(file_name)

        def upload_chunk(i, chunk):
            requests.post('https://store-eu-hz-3.ufile.io/v1/upload/chunk', data={
                "chunk_index": i + 1,
                "fuid": self.fuid,
            }, files={
                "file": open(chunk, 'rb')
            })

        with ThreadPool() as p:
            p.starmap(upload_chunk, enumerate(chunks))

        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        response = requests.post('https://store-eu-hz-3.ufile.io/v1/upload/finalise', data={
            'fuid': self.fuid,
            'file_name': file_path.stem,
            'file_type': file_path.suffix[1:],
            'total_chunks': len(chunks)
        }, headers=headers)

        return json.loads(response.content)['url']

    async def download_file_link(self, slug):
        return requests.get(f"https://ufile.io/v1/download/{slug}", headers={
            "X-API-KEY": self.api_key
        }).content

    async def download_file(self, slug: str, download_address: str):
        link = requests.get(f"https://ufile.io/v1/download/{slug}", headers={
            "X-API-KEY": self.api_key
        }).content

        response = requests.get(link)
        open(download_address, "wb").write(response.content)


if __name__ == '__main__':
    pass
