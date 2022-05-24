
import sys, html, urllib, re, os


def status_code_server(environ, start_response):
    # TODO: query all status codes using [urllib.request.urlopen, requests.get, requests.get.raise_for_status] to compare error-handling
    #  - results should be: (urlopen / requests.get*)
    #    - can't connect => URLError / requests.exceptions.ConnectionError
    #    - 000-100 => BadStatusLine / requests.exceptions.ConnectionError
    #    - 101-199 => HTTPError / ok
    #    - 200-299 => ok
    #    - 301-303,307 with valid "Location:" header => respond for new location
    #    - 300-399 otherwise => HTTPError / ok
    #    - 400-599 => HTTPError / ok (but raise_for_status raises requests.exceptions.HTTPError)
    #    - 600-999 => HTTPError / ok
    headers = [('Content-type', 'text/plain')]
    path = environ.get('PATH_INFO','')

    m = re.match(r'^/([0-9]{3})/([0-9]{3})$', path)
    if m:
        status = m.group(1) + ' WAT'
        headers.append(('Location', '/{}'.format(m.group(2))))
        ret = 'following xxx -> xxx path for {}\n'.format(path).encode('utf8')
        headers.append(('Content-Length', str(len(ret))))
        start_response(status, headers)
        return [ret]

    m = re.match(r'^/([0-9]{3})$', path)
    if m:
        status = m.group(1) + ' WAT'
        ret = 'following xxx path for {}\n'.format(path).encode('utf8')
        headers.append(('Content-Length', str(len(ret))))
        start_response(status, headers)
        return [ret]

    raise Exception('bad url: {path}'.format(**locals()))


def make_redirect_server(target_base_url):
    assert re.match(r'https?://(?:[-a-z0-9]+\.)+[-a-z0-9]+(?:/.*)?', target_base_url)
    def redirect_server(environ, start_response):
        headers = [('Content-type', 'text/plain')]
        path = environ.get('PATH_INFO','')
        if environ.get('QUERY_STRING'):
            path += '?' + environ.get('QUERY_STRING')
        if re.match(r'^[-/a-zA-Z0-9%\.+~_=:\?&]*$', path):
            status = '302 Found'
            headers.append(('Location', '{}{}'.format(target_base_url, path)))
            ret = 'redirecting to {}{}\n'.format(target_base_url, path)
        else:
            status = '404 Not Found'
            ret = 'URL not permitted\n'
        start_response(status, headers); return [ret.encode('utf8')]
    return redirect_server

def directory_server(environ, start_response):
    # TODO: just implement a simple version by hand
    def normalize_path(path):
        # This code is taken from http.server.SimpleHTTPRequestHandler.translate_path()
        import urllib.parse, posixpath
        path = path.split('?', 1)[0]
        path = path.split('#', 1)[0]
        path = urllib.parse.unquote(path)
        path = posixpath.normpath(path)
        words = [word for word in path.split('/') if word]
        path = os.getcwd()
        for word in words:
            if os.path.dirname(word) or word in (os.curdir, os.pardir):
                # ignore components like `.`, `..`, (and also somehow directories?)
                continue
            path = os.path.join(path, word)
        return path
    path = normalize_path(environ.get('PATH_INFO', ''))



def magic_directory_server(environ, start_response):
    # This is like `python3 -m http.server` (http.server.SimpleHTTPRequestHandler).
    # `SimpleHTTPRequestHandler` chooses mimetype using file extension (mimetypes.types_map)
    # This server instead uses mime-guessing
    # I have a solid implementation in `MimeSniffingHTTPRequestHandler` but I'm not sure how to convert it to WSGI/gunicorn
    #    It extends `http.server.SimpleHTTPRequestHandler`
    #       which extends `http.server.BaseHTTPRequestHandler`
    #           which extends `socketserver.StreamRequestHandler`.
    #    It's run using `http.server.test(HandlerClass=MimeSniffingHTTPRequestHandler, ServerClass=http.server.HTTPServer)`
    #       which uses `http.server.HTTPServer(('localhost', 8001), MimeSniffingHTTPRequestHandler).serve_forever()`
    #          which extends `socketserver.TCPServer`
    def normalize_path(path):
        # This code is taken from http.server.SimpleHTTPRequestHandler.translate_path()
        import urllib.parse, posixpath
        path = path.split('?', 1)[0]
        path = path.split('#', 1)[0]
        has_trailing_slash = path.rstrip().endswith('/')
        path = urllib.parse.unquote(path)
        path = posixpath.normpath(path)
        words = [word for word in path.split('/') if word]
        path = os.getcwd()
        for word in words:
            if os.path.dirname(word) or word in (os.curdir, os.pardir):
                # ignore components like `.`, `..`, (and also somehow directories?)
                continue
            path = os.path.join(path, word)
        if has_trailing_slash:
            path += '/'
        return path
    def generate_directory_listing(path):
        enc = sys.getfilesystemencoding()
        try:
            lst = os.listdir(path)
        except OSError:
            return 'Failed to list directory'.encode(enc), enc
        lst.sort(key=lambda a: a.lower())
        r = []
        displaypath = html.escape(urllib.parse.unquote(path), quote=False)
        title = 'Directory listing for %s' % displaypath
        r.append('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" '
                 '"http://www.w3.org/TR/html4/strict.dtd">')
        r.append('<html>\n<head>')
        r.append('<meta http-equiv="Content-Type" '
                 'content="text/html; charset=%s">' % enc)
        r.append('<title>%s</title>\n</head>' % title)
        r.append('<body>\n<h1>%s</h1>' % title)
        r.append('<hr>\n<ul>')
        for name in lst:
            displayname = linkname = name
            fullname = os.path.join(path, name)
            if os.path.isdir(fullname):
                displayname = linkname = name + '/'
            if os.path.islink(fullname):
                displayname = name + '@'
            r.append('<li><a href="%s">%s</a></li>'
                     % (urllib.parse.quote(linkname),
                        html.escape(displayname, quote=False)))
        r.append('</ul>\n<hr>\n</body>\n</html>\n')
        return '\n'.join(r).encode(enc), enc
    def guess_content_type(fpath):
        # TODO: use `http.server.SimpleHTTPRequestHandler.guess_type` method
        import magic
        return magic.from_file(fpath, mime=True)
    path = normalize_path(environ.get('PATH_INFO', ''))
    if os.path.isdir(path):
        parts = urllib.parse.urlsplit(environ.get('PATH_INFO',''))
        if not parts.path.endswith('/'):
            # redirect browser like apache2 does
            new_parts = (parts[0], parts[1], parts[2] + '/', parts[3], parts[4])
            new_url = urllib.parse.urlunstplit(new_parts)
            start_response('301 MOVEDPERMANENTLY', [('Location', new_url)])
            return b''
        else:
            data, enc = generate_directory_listing(path)
            start_response('200 OK', [('Content-type', 'text/html; charset=%s' % enc)
                                      ('Content-Length', str(len(data)))])
            return data
    ctype = guess_content_type(path)
    try:
        f = open(path, 'rb')
    except OSError:
        start_response('404 NOTFOUND', [('Connection', 'close')])
    # Note: work-in-progress

def serve(app, port=5000):
    from .http_utils import run_gunicorn
    try:
        run_gunicorn(app, port=port, use_reloader=False)
    except KeyboardInterrupt:
        pass
