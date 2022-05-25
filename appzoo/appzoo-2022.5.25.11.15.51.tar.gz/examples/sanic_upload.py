#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : tql-App.
# @File         : upload_sanci
# @Time         : 2019-11-29 13:12
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  : 


import os
from sanic import Sanic
from sanic.response import redirect, html

app = Sanic()


@app.route('/', methods=['POST', 'GET'])
async def upload(request):
    if request.method == 'POST':
        f = request.files.get("file")
        basepath = os.path.dirname(__file__)
        upload_path = os.path.join(basepath, 'static', f.name)
        print(f.name)
        print(f.type)
        print(f.body)
        with open(upload_path, 'wb') as fw:
            fw.write(f.body)
        return redirect(app.url_for('upload'))
    return html("""
        <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Title</title>
    </head>
    <body>
      <h1>文件上传</h1>
      <form action="" enctype='multipart/form-data' method='POST'>
        <input type="file" name="file">
        <input type="submit" value="上传">
      </form>
    </body>
    </html>
    """)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000)