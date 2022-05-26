import IPython

from pathlib import Path
from tqdm import tqdm
from urllib.parse import urlparse

from ._version import __version__


DEFAULT_CHUNK_SIZE = 8 << 10


def is_jupyterlite():
    return IPython.sys.platform == 'emscripten'


async def _get_chunks(url, chunk_size):
    desc = Path(urlparse(url).path).name
    if is_jupyterlite():
        import io
        from js import fetch
        response = await fetch(url, stream=True)
        bio = io.BytesIO((await response.arrayBuffer()).to_py())
        pbar = tqdm(
            miniters=1,
            desc=desc,
            total=int(response.headers.get('content-length', 0)))
        chunk = bio.read(chunk_size)
        while chunk:
            yield chunk
            pbar.update(len(chunk))
            chunk = bio.read(chunk_size)
        pbar.close()
    else:
        import requests
        with requests.get(url, stream=True) as response:
            pbar = tqdm(
                miniters=1,
                desc=desc,
                total=int(response.headers.get('content-length', 0)))
            for chunk in response.iter_content(chunk_size=chunk_size):
                yield chunk
                pbar.update(len(chunk))
            pbar.close()


async def download(url, filename=None, chunk_size=DEFAULT_CHUNK_SIZE):
    if filename is None:
        filename = Path(urlparse(url).path).name
    with open(filename, 'wb') as f:
        async for chunk in _get_chunks(url, chunk_size):
            f.write(chunk)
    print(f'Saved as {filename}')


async def read(url, chunk_size=DEFAULT_CHUNK_SIZE):
    return b''.join([chunk async for chunk in _get_chunks(url, chunk_size)])


if is_jupyterlite():
    tqdm.monitor_interval = 0

# For backwards compadibility
download_dataset = download
read_dataset = read
