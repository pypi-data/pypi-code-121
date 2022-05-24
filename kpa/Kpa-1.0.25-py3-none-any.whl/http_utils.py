
def get_ip():
    import subprocess
    return subprocess.check_output('dig +short myip.opendns.com @resolver1.opendns.com'.split()).strip().decode('ascii')
    # import socket
    # sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # sock.connect(('resolver1.opendns.com', 53))
    # sock.send(b'\0\0\1\0\0\1\0\0\0\0\0\0\4myip\7opendns\3com\0\0\1\0\1')
    # resp = sock.recv(1000)
    # return '.'.join(str(b) for b in resp[-4:])
    # import requests, re
    # data = requests.get('http://checkip.dyndns.com/').text
    # return re.compile(r'Address: (\d+\.\d+\.\d+\.\d+)').search(data).group(1)


def open_browser(url):
    import os
    import webbrowser
    if 'DISPLAY' not in os.environ:
        print('The DISPLAY variable is not set, so not attempting to open a web browser\n')
        return False
    for name in 'windows-default macosx chrome chromium mozilla firefox opera safari'.split():
        # Note: `macosx` fails on macOS 10.12.5 due to <http://bugs.python.org/issue30392>.
        try:
            b = webbrowser.get(name)
            if b.open(url):
                return True
        except Exception:
            pass
    return False


def run_gunicorn(app, host='0.0.0.0', port=5000, use_reloader=True, num_workers=4, accesslog='-'):
    '''takes a flask app or perhaps other kinds of wsgi apps'''
    # TODO: figure out how to suppress sigwinch
    import gunicorn.app.base
    class StandaloneGunicornApplication(gunicorn.app.base.BaseApplication):
        # from <http://docs.gunicorn.org/en/stable/custom.html>
        def __init__(self, app, opts=None):
            self.application = app
            self.options = opts or {}
            super().__init__()
        def load_config(self):
            for key, val in self.options.items():
                self.cfg.set(key, val)
        def load(self):
            return self.application
    options = {
        'bind': '{}:{}'.format(host, port),
        'reload': use_reloader,
        'workers': num_workers,
        'accesslog': accesslog,
        'access_log_format': '%(t)s | %(s)s | %(L)ss | %(m)s %(U)s %(q)s | resp_len:%(B)s | referrer:"%(f)s" | ip:%(h)s | agent:%(a)s',
        # docs @ <http://docs.gunicorn.org/en/stable/settings.html#access-log-format>
        'worker_class': 'gevent',
    }
    sga = StandaloneGunicornApplication(app, options)
    # # debugging:
    # for skey,sval in sorted(sga.cfg.settings.items()):
    #     cli_args = sval.cli and ' '.join(sval.cli) or ''
    #     val = str(sval.value)
    #     print(f'cfg.{skey:25} {cli_args:28} {val}')
    #     if sval.value != sval.default:
    #         print(f'             default: {str(sval.default)}')
    #         print(f'             short: {sval.short}')
    #         print(f'             desc: <<\n{sval.desc}\n>>')
    sga.run()


from .func_cache_utils import shelve_cache
@shelve_cache
def cached_get(url):
    import requests
    # Do we need to encode this response somehow?
    # Maybe as `(resp.status, resp.text)`?
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:62.0) Gecko/20100101 Firefox/62.0',
               'Accept-Language':'en-US,en;q=0.5',
    }
    return requests.get(url, headers=headers)
