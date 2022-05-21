# -*- coding: UTF-8 -*-
from tornado.web import RequestHandler
import os

UPLOADSERVER_BASEURI = 'userdata'

class UploadHandler(RequestHandler):
    def get(self):
        self.write('upload page')

    def post(self, *args, **kwargs):
        self.write('upload post page')
        files = self.request.files # 获取上传的文件
        imgs = files.get('img', [])
        for img in imgs:
            filename = img.get('filename')
            ext = img.get('content_type')
            data = img.get('body')

            # 保存文件
            file = open(UPLOADSERVER_BASEURI + '/%s' % filename, 'wb') # 保存到UPLOADSERVER_BASEURI文件夹中
            file.write(data)
            file.close()

def Handle(config):
    if not os.path.isdir(config['static']):
        raise Exception('static is not directory: {}'.format(config['static']))
    if not os.path.isdir(config['static']+"/"+UPLOADSERVER_BASEURI):
        os.mkdir(config['static']+"/"+UPLOADSERVER_BASEURI)
    uri = os.path.join(r"/", config['base_uri'], config['upload_uri'])
    print(config, uri)
    return [(uri, UploadHandler)]
