'''
This is Asterisk PBX CLI engine.
'''
from __future__ import absolute_import, print_function, unicode_literals
import logging
import os
from urllib.parse import urljoin
import requests
import ssl
from salt.ext.tornado.web import HTTPError
import salt.ext.tornado.web
import salt.utils.process
try:
    from terminado import TermSocket, UniqueTermManager
    HAS_LIBS = True
except ImportError:
    HAS_LIBS = False
    TermSocket = object  # A stub for MyTermSocket inheritance.
import time

__virtualname__ = 'asterisk_cli'

log = logging.getLogger(__name__)


def __virtual__():
    # Check if asterisk binary is available.
    asterisk_binary = __salt__['config.get']('asterisk_binary')
    if not os.path.exists(asterisk_binary):
        msg = 'Asterisk binary {} not found!'.format(asterisk_binary)
        log.warning(msg)
        return False, msg
    if not HAS_LIBS:
        msg = 'Terminado lib not found, Asterisk CLI module not available.'
        log.warning(msg)
        return False, msg
    return True


class MyTermSocket(TermSocket):

    def check_origin(self, origin):
        return True

    def get(self, *args, **kwargs):
        server_id = self.get_argument('server')
        db = self.get_argument('db')
        if not server_id:
            raise HTTPError(404)
        # Check auth token
        auth = self.get_argument('auth')        
        url = urljoin(
            os.environ['ODOO_URL'],
            '/asterisk_plus/console/{}/{}/{}'.format(db, server_id, auth))
        try:
            res = requests.get(url)
            res.raise_for_status()
            if res.text != 'ok':
                raise HTTPError(403)            
        except Exception as e:
            log.error('Odoo fetch request error: %s', e)
        try:
            return super(TermSocket, self).get(*args, **kwargs)
        except Exception:
            log.exception('TermSocker errror:')


def start():
    ssl_crt = __salt__['config.get']('asterisk_cli_ssl_crt')
    ssl_key = __salt__['config.get']('asterisk_cli_ssl_key')
    ssl_options = None
    asterisk_cli_listen_address = __salt__['config.get']('asterisk_cli_listen_address')
    asterisk_cli_port = __salt__['config.get']('asterisk_cli_port')
    odoo_url = '{}://{}:{}'.format(
        'https' if __salt__['config.get']('odoo_use_ssl') else 'http',
        __salt__['config.get']('odoo_host'),
        __salt__['config.get']('odoo_port'))
    asterisk_binary = __salt__['config.get']('asterisk_binary')
    asterisk_options = __salt__['config.get']('asterisk_options')
    salt.utils.process.appendproctitle('AsteriskCLI')
    log.info('CLI Server: Odoo configured on %s.', odoo_url)
    io_loop = salt.ext.tornado.ioloop.IOLoop(make_current=False)
    io_loop.make_current()
    # Set ODOO_URL envvar for MyTermSocket:get().
    os.environ['ODOO_URL'] = odoo_url
    extra_env = {}
    if not __salt__['config.get']('asterisk_shell_enabled'):
        extra_env['SHELL'] = '/usr/sbin/nologin'
    term_manager = UniqueTermManager(
        shell_command=[asterisk_binary, asterisk_options],
        extra_env=extra_env,
        ioloop=io_loop)
    handlers = [
        (r'/', MyTermSocket, {'term_manager': term_manager})]
    # Init app.
    app = salt.ext.tornado.web.Application(handlers)
    if all([ssl_crt, ssl_key]):
        ssl_options = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        # Bug Chrome: SSLV3_ALERT_ILLEGAL_PARAMETER and below did not help
        # ssl_options.options |= ssl.PROTOCOL_SSLv23
        # ssl_options.options |= ssl.PROTOCOL_TLS
        ssl_options.load_cert_chain(ssl_crt, ssl_key)
        log.info('Starting CLI server at HTTPS://%s:%s.',
                 asterisk_cli_listen_address, asterisk_cli_port)
    else:
        log.warning('Starting CLI server (not secure) at HTTP://%s:%s.',
                 asterisk_cli_listen_address, asterisk_cli_port)        
    http_server = salt.ext.tornado.httpserver.HTTPServer(
        app, ssl_options=ssl_options)
    http_server.listen(asterisk_cli_port, address=asterisk_cli_listen_address)
    try:
        if not io_loop._running:
            io_loop.start()
    finally:
        term_manager.shutdown()


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG if os.getenv('DEBUG') else logging.INFO,
        format='%(asctime)s - %(name)s:%(lineno)s - %(levelname)s - %(message)s')
    start()
