"""
  handlers.py
 
  Copyright (C) 2022 by RStudio, PBC
 
"""

from jupyterlab_rsw.constants import SERVER_ENDPOINT, SERVER_URL, URI_SCHEME, SESSION_URL, URL_ENDPOINT
from jupyterlab_rsw.proxiedServersProvider import ProxiedServersProvider

from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join

import json
import tornado
from typing import Optional, Awaitable

class UrlComponentsHandler(APIHandler):
    @tornado.web.authenticated
    def get(self):
        if SERVER_URL and len(SERVER_URL) != 0:
            base_url = SERVER_URL
        elif URI_SCHEME:
            base_url = URI_SCHEME + ':'
        else: # this case should only be reached in local testing
            base_url = 'http:'
            print("""Warning: Environment variables SERVER_URL and URI_SCHEME are not set - 
                   proxied server links will not work as expected.""")
        if SESSION_URL:
            base_session_url = base_url + SESSION_URL
        else: # this case should only be reached in local testing
            base_session_url = base_url
            print("""Warning: Environment variable SESSION_URL is not set - 
                   proxied server links will not work as expected.""")
        self.finish(json.dumps({
            "baseSessionUrl": base_session_url
        }));

class ProxiedServersHandler(APIHandler):
    def __init__(self, application, request, **kwargs):
        self.provider = kwargs.pop('provider')
        super().__init__(application, request, **kwargs)

    async def prepare(self) -> Optional[Awaitable[None]]:
        await self.provider.load_running_servers()

    @tornado.web.authenticated
    def get(self):
        json_data = self.provider.get_servers_json()
        self.finish(json_data)

def setup_handlers(web_app, url_path):
    host_pattern = ".*$"
    base_url = web_app.settings["base_url"]

    url_route_pattern = url_path_join(base_url, url_path, URL_ENDPOINT)
    servers_route_pattern = url_path_join(base_url, url_path, SERVER_ENDPOINT)
    provider = ProxiedServersProvider()
    handlers = [(servers_route_pattern, ProxiedServersHandler, {"provider": provider}),
                (url_route_pattern, UrlComponentsHandler)]

    web_app.add_handlers(host_pattern, handlers)
