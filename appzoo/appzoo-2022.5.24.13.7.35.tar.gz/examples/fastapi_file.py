#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AppZoo.
# @File         : fastapi_file
# @Time         : 2021/12/28 下午1:35
# @Author       : yuanjie
# @WeChat       : 313303303
# @Software     : PyCharm
# @Description  : 

from meutils.pipe import *
from typing import List
import uvicorn

from fastapi import FastAPI, File, UploadFile
from starlette.responses import HTMLResponse, FileResponse, StreamingResponse

app = FastAPI()


@app.get("/downloadfile")
def downloadfile():
    return FileResponse('/Users/yuanjie/Desktop/字段词根字典（征求意见稿）.xlsx', filename='词根翻译结果.xlsx')


@app.post("/_file/")
async def get_file(file: bytes = File(...)):
    print(file)
    with open('./text.txt', 'wb') as f:
        f.write(file)

    return {"fileSize": len(file)}


@app.post("/file/")
async def create_files(file: bytes = File(...)):
    with open('./base.jpg', 'wb') as f:
        f.write(file)

    return {"fileSize": len(file)}


@app.post('/uploadFile')
async def uploadFile(file: UploadFile = File(...)):
    """缺少验证是否上传文件"""
    content = await file.read()
    with open('./test.file', 'wb') as f:
        f.write(content)

    return {"filename": file.filename}


@app.post('/uploadFile_')
async def uploadFile(file: UploadFile = File(...)):
    """缺少验证是否上传文件"""
    content = await file.read()

    df = pd.read_excel(content)[['中文全称', '英文名称', '英文简称']]
    print(df)

    # content = await file.read()
    #
    # return {"content": content}


@app.post("/files/")
async def create_files(
        files: List[bytes] = File(...)
):
    print(type(files))
    print(files)
    return {"file_sizes": [len(file) for file in files]}


@app.post("/uploadfiles/")
async def create_upload_files(
        files: List[UploadFile] = File(...)
):
    print(files)
    return {"filenames": [file.filename for file in files]}


@app.get("/")
async def main():
    content = """
<body>
<form action="/file/" enctype="multipart/form-data" method="post">
<input name="file" type="file">
<input type="submit" value="file上传">
</form>
<form action="/files/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit" value="files上传">
</form>
<form action="/uploadFile/" enctype="multipart/form-data" method="post">
<input name="file" type="file">
<input type="submit" value="uploadFile上传">
</form>
<form action="/uploadfiles/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit" value="uploadfiles上传">
</form>
</body>
 """
    return HTMLResponse(content=content)


if __name__ == '__main__':
    uvicorn.run(app, port=9955, host='0.0.0.0')
