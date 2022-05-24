import html
import io
import os
import sys
import urllib
from functools import partial
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, HTTPServer

import click

from src.utils import iputils


def http_server(d, port, host):
    handler = partial(MingHttpHandler, directory=d)
    httpd = HTTPServer((host, port), handler)
    click.echo(
        'http server start.............\n监听地址:\nhttp://{}:{}\nhttp://{}:{}'.format(host, port, iputils.get_host_ip(),
                                                                                   port))
    httpd.serve_forever(poll_interval=0.1)


class MingHttpHandler(SimpleHTTPRequestHandler):

    def list_directory(self, path):
        """
        重写 显示目录的页面  增加 .  ..目录
        修改title
        """
        try:
            list = os.listdir(path)
        except OSError:
            self.send_error(
                HTTPStatus.NOT_FOUND,
                "No permission to list directory")
            return None
        # 由于os.listdir 不显示 .  .. 这里手工为每个文件夹目录添加
        list.append('.')
        list.append('..')
        list.sort(key=lambda a: a.lower())
        r = []
        try:
            displaypath = urllib.parse.unquote(self.path,
                                               errors='surrogatepass')
        except UnicodeDecodeError:
            displaypath = urllib.parse.unquote(path)
        displaypath = html.escape(displaypath, quote=False)
        enc = sys.getfilesystemencoding()
        title = 'Directory listing for %s' % displaypath
        r.append('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" '
                 '"http://www.w3.org/TR/html4/strict.dtd">')
        r.append('<html>\n<head>')
        r.append('<meta http-equiv="Content-Type" '
                 'content="text/html; charset=%s">' % enc)
        r.append('<title>ming-tools %s</title>\n</head>' % title)
        r.append('<body>\n<h1>%s</h1>' % title)
        r.append('<hr>\n<ul>')
        for name in list:
            fullname = os.path.join(path, name)
            displayname = linkname = name
            # Append / for directories or @ for symbolic links
            if os.path.isdir(fullname):
                displayname = name + "/"
                linkname = name + "/"
            if os.path.islink(fullname):
                displayname = name + "@"
                # Note: a link to a directory displays with @ and links with /
            r.append('<li><a href="%s">%s</a></li>'
                     % (urllib.parse.quote(linkname,
                                           errors='surrogatepass'),
                        html.escape(displayname, quote=False)))
        r.append('</ul>\n<hr>\n</body>\n</html>\n')
        encoded = '\n'.join(r).encode(enc, 'surrogateescape')
        f = io.BytesIO()
        f.write(encoded)
        f.seek(0)
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-type", "text/html; charset=%s" % enc)
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        return f
