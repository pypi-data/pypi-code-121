#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : tql-App.
# @File         : flask_upload
# @Time         : 2019-11-29 13:22
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  : 

from flask import Flask, request, redirect, url_for
import os

app = Flask(__name__)

@app.route('/upload', methods=['POST', 'GET'])
def upload():
    if request.method == 'POST':
        f = request.files['file']
        basepath = os.path.dirname(__file__)
        upload_path = os.path.join(basepath, 'static', f.filename)
        f.save(upload_path)
        return redirect(url_for('upload'))
    # return render_template('./upload.html')
    return '''
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
    '''


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=9001, debug=True)
