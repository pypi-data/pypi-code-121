# -*- coding: UTF-8 -*-
import tornado.web
import json
import os

FILESERVER_BASEURI = 'html'
UPLOADSERVER_FOLDER = 'userdata'
STATIC_FOLDER = ''

class UploadHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('upload page')

    def post(self, *args, **kwargs):
        files = self.request.files # 获取上传的文件
        imgs = files.get('file', [])
        filepaths = []
        for img in imgs:
            filename = img.get('filename')
            ext = img.get('content_type')
            data = img.get('body')

            # 保存文件
            filepath = os.path.join(STATIC_FOLDER, UPLOADSERVER_FOLDER, filename)
            print(filepath)
            file = open(filepath, 'wb') # 保存到UPLOADSERVER_BASEURI文件夹中
            file.write(data)
            file.close()
            filepaths.append(os.path.join('$$base_uri$$', UPLOADSERVER_FOLDER, filename))
        self.write(json.dumps(filepaths, ensure_ascii=False))


class UploadContentHandler(tornado.web.RequestHandler):
    def initialize(self, path: str) -> None:
        self.root = path

    def get(self):
        uri = os.path.join(STATIC_FOLDER, UPLOADSERVER_FOLDER)
        # print(uri)
        files = self.list_all_files(uri)
        # self.write('upload page')
        self.write(json.dumps(files, ensure_ascii=False))

    def list_all_files(self, rootdir):
        import os
        _files = []
        # 列出文件夹下所有的目录与文件
        list = os.listdir(rootdir)
        for i in range(0, len(list)):
            # 构造路径
            path = os.path.join(rootdir, list[i])
            # 判断路径是否为文件目录或者文件
            # 如果是目录则继续递归
            if os.path.isdir(path):
                _files.extend(self.list_all_files(path))
            if os.path.isfile(path):
                _files.append({"url": os.path.join(UPLOADSERVER_FOLDER, list[i]), "created_time": os.path.getctime(path)})
        new_para = sorted(_files, key=lambda x: x["created_time"])
        return new_para


def Handle(config):
    global STATIC_FOLDER
    if not os.path.isdir(config['static']):
        raise Exception('static is not directory: {}'.format(config['static']))
    STATIC_FOLDER = config['static']
    if not os.path.isdir(config['static']+"/"+UPLOADSERVER_FOLDER):
        os.mkdir(config['static']+"/"+UPLOADSERVER_FOLDER)
    static_uri = os.path.join(r"/", config['base_uri'], FILESERVER_BASEURI, r'(.*)$')
    upload_uri = os.path.join(r"/", config['base_uri'], config['upload_uri'])
    upload_static_uri = os.path.join(r"/", config['base_uri'], UPLOADSERVER_FOLDER)
    print(config, static_uri, upload_uri)
    # return [(r'/(.*)$', tornado.web.StaticFileHandler, {'path': 'html/', 'default_filename': 'index.html'})]
    return [
        (static_uri, tornado.web.StaticFileHandler, {'path': config['static'], 'default_filename': 'index.html'}),
        (upload_uri, UploadHandler),
        (upload_static_uri, UploadContentHandler, {'path': FILESERVER_BASEURI}),
        ]


# def Handle(config):
#     if not os.path.isdir(config['static']):
#         raise Exception('static is not directory: {}'.format(config['static']))
#     if not os.path.isdir(config['static']+"/"+UPLOADSERVER_BASEURI):
#         os.mkdir(config['static']+"/"+UPLOADSERVER_BASEURI)
#     uri = os.path.join(r"/", config['base_uri'], config['upload_uri'])
#     print(config, uri)
#     return [(uri, UploadHandler)]

# class MainHandler(tornado.web.RequestHandler):
#     def get(self):
#         self.write("Hello, world")