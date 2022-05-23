import os
import logging
import hashlib
import uuid

import aiofiles
from fastapi import FastAPI, Request, Header
from fastapi.responses import StreamingResponse

from app.config import settings

logger = logging.getLogger(__name__)


app = FastAPI()


def _gen_hash(digest):
    _, hash = digest.split("=")
    return hash


@app.get("/ping")
def ping():
    return {"result": "pong"}


@app.put("/objects/{filename}")
async def upload_file(request: Request, filename: str, digest: str = Header()):
    logger.info(f"put object {filename}, digest is {digest}")

    filepath = os.path.join(settings.data_path, str(uuid.uuid4()))

    m = hashlib.sha256()

    logger.info("writting stream to file {filepath}")
    async with aiofiles.open(filepath, mode="wb") as f:
        async for chunk in request.stream():
            await f.write(chunk)
            m.update(chunk)

    hash = m.hexdigest()

    logger.info(f"file hash is {hash}")
    if hash != _gen_hash(digest):
        os.remove(filepath)
        return {"filename": filename, "sha256": ""}

    dest_path = os.path.join(settings.data_path, hash)

    logger.info(f"rename file to {dest_path}")
    os.rename(filepath, dest_path)

    return {"filename": filename, "sha256": hash}


@app.get("/objects/{filename}")
async def download_file(filename: str):
    filepath = os.path.join(settings.data_path, filename)

    logger.info(f"download file {filepath}")

    def iterfile():
        with open(filepath, mode="r") as f:
            yield from f.read()

    return StreamingResponse(iterfile())
