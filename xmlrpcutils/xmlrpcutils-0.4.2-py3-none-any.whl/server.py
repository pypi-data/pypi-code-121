

import json
import logging
from socketserver import ThreadingMixIn
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler

from fastutils import logutils
from daemon_application import DaemonApplication

logger = logging.getLogger(__name__)

XMLRPC_403_XML = b"""<?xml version="1.0" encoding="UTF-8" ?>
<methodResponse>
    <fault>
        <value>
            <struct>
                <member>
                    <name>faultCode</name>
                    <value><int>403</int></value>
                </member>
                <member>
                    <name>faultString</name>
                    <value><string>403 Forbidden</string></value>
                </member>
            </struct>
        </value>
    </fault>
</methodResponse>
"""

class SimpleXmlRpcRequestHandler(SimpleXMLRPCRequestHandler):
    """
    supported server settings:

    apikey-auth-header: apikey
    apikeys:
      app1:
      app2:
    
    keepalive:
      enable: true
      timeout: 5
      max: 60
    """
    def is_apikey_auth_on(self):
        if self.server.config.get("apikeys", {}):
            return True
        else:
            return False

    def is_server_tokens_on(self):
        return self.server.config.get("server-tokens", False)

    def is_keepalive_on(self):
        return self.server.config.get("keepalive", {}).get("enable", False)

    def get_keepalive_timeout(self):
        return self.server.config.get("keepalive", {}).get("timeout", 5)
    
    def get_keepalive_max(self):
        return self.server.config.get("keepalive", {}).get("max", 60)

    def get_apikey_auth_header_name(self):
        return self.server.config.get("apikey-auth-header", "apikey")

    def get_apikeys(self):
        return self.server.config.get("apikeys", {})

    def send_response(self, code, message=None):
        self.log_request(code)
        self.send_response_only(code, message)
        # hide/show response's Server header
        if self.is_server_tokens_on():
            self.send_header("Server", self.version_string())
        # hide/show response's Connection/Keep-Alive headers
        if self.is_keepalive_on():
            self.send_header("Connection", "Keep-Alive")
            keepalive_timeout = self.get_keepalive_timeout()
            keepalive_max = self.get_keepalive_max()
            self.send_header("Keep-Alive", f"timeout={keepalive_timeout}, max={keepalive_max}")
        self.send_header("Date", self.date_time_string())

    def do_POST(self):
        if self.is_apikey_auth_on():
            apikey_auth_header_name = self.get_apikey_auth_header_name()
            apikeys = self.get_apikeys()
            self._apikey = self.headers.get(apikey_auth_header_name, None)
            if self._apikey:
                self._appinfo = apikeys.get(self._apikey, None)
            else:
                self._appinfo = None
            if self._apikey and self._appinfo:
                return super().do_POST()
            else:
                # apikey verify failed, return error message
                logger.error("Apikey auth verify failed, headers={}".format(json.dumps(dict(self.headers))))
                self.send_response(403)
                self.send_header("Content-Type", "text/xml")
                self.send_header("Content-Length", len(XMLRPC_403_XML))
                self.end_headers()
                self.wfile.write(XMLRPC_403_XML)
        else:
            return super().do_POST() 

class SimpleThreadedXmlRpcServer(ThreadingMixIn, SimpleXMLRPCServer):
    
    def __init__(self, *args, **kwargs):
        self.config = {}
        super().__init__(*args, **kwargs)
        self.register_introspection_functions()
        self.register_multicall_functions()

    def set_config(self, config):
        self.config = config

class SimpleXmlRpcServer(DaemonApplication):

    def get_default_listen_port(self):
        return getattr(self, "default_listen_port", 8381)
    
    def get_disable_debug_service_flag(self):
        return getattr(self, "disable_debug_service", False)

    def get_request_handler_class(self):
        return SimpleXmlRpcRequestHandler

    def main(self):
        logutils.setup(**self.config)
        self.server_listen = tuple(self.config.get("server", {}).get("listen", ("0.0.0.0", self.get_default_listen_port())))
        logger.warn("Starting xmlrpc server on {server_listen}...".format(server_listen=self.server_listen))
        self.server = SimpleThreadedXmlRpcServer(
            self.server_listen,
            requestHandler=self.get_request_handler_class(),
            allow_none=True,
            encoding="utf-8",
            )
        self.server.set_config(self.config)
        self.register_services()
        try:
            self.server.serve_forever()
        except KeyboardInterrupt:
            logger.warn("Got KeyboardInterrupt signal, stopping the service...")

    def register_services(self):
        disable_debug_service_flag = self.get_disable_debug_service_flag()
        if not disable_debug_service_flag:
            from .service import DebugService
            DebugService().register_to(self.server)
