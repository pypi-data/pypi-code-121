import json
import time

import aiohttp_cors
import socketio
from aiohttp import web


class ClientService:
    def __init__(self, port, plugin_id):
        self.port = port
        self.plugin_id = plugin_id
        self.sio = self.__get_socket_io()
        self.app = self.__get_web_app()
        self.sio.attach(self.app)
        self.controllers = []

    def __get_socket_io(self):
        sio = socketio.AsyncServer(
            async_mode='aiohttp', cors_allowed_origins='*')

        @sio.event
        async def connect(sid, environ, auth):
            print(f"✨ Client connected: {sid} => {len(self.controllers)} controllers")
            for controller in self.controllers:
                await controller.on_connect(sid)

        @sio.on('client-state-changed')
        async def on_client_state_changed(sid, data):
            print(f"📣 Client state changed: {sid} => {len(self.controllers)} controllers")
            for controller in self.controllers:
                await controller.on_client_state_changed(sid, json.loads(data))

        return sio

    def __get_web_app(self):
        app = web.Application()

        cors = aiohttp_cors.setup(app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_methods="*",
                allow_headers="*",
            )
        })

        cors.add(app.router.add_static('/static', 'static'))

        return app

    def listen(self):
        web.run_app(self.app, port=self.port)

    def add_controller(self, controller):
        self.controllers.append(controller)

    async def emit_busy(self, sid, collection_name):
        layer = {
            "id": f"busy-{collection_name}",
            "collectionName": "busy",
            "set": [{"id": collection_name, }],
            "timestamp": int(time.time())
        }
        await self.emit_add_layers(sid, [layer])

    async def emit_done(self, sid, collection_name):
        message = {
            "query": {
                "id": f'busy-{collection_name}',
            }
        }
        await self.sio.emit('remove-layers', json.dumps(message), room=sid)

    async def emit_menu(self, sid, icon, title, nav_link, aliases=None, short_link=None):
        """
        Sends menu layer from server to the client side
        """

        layer = {
            "id": f"{self.plugin_id}_menu_{nav_link}",
            "collectionName": "menus",
            "set": [
                {
                    "id": f"{self.plugin_id}_{nav_link}",
                    "icon": icon,
                    "title": title,
                    "navLink": nav_link,
                    "aliases": aliases,
                    "shortLink": short_link
                }
            ],
            "timestamp": int(time.time())
        }

        await self.emit_add_layers(sid, [layer])

    async def emit_page(self, sid, path, element):
        """
        Sends main page content from server to the client side
        """

        layer = {
            "id": f"{self.plugin_id}_page_{path}",
            "collectionName": "pages",
            "set": [
                {
                    "id": path,
                    "element": element
                }
            ],
            "timestamp": int(time.time())
        }

        await self.emit_add_layers(sid, [layer])

    async def emit_documents(self, sid, collection_name, documents):

        layer = {
            "id": f"{self.plugin_id}_{collection_name}",
            "collectionName": collection_name,
            "set": documents,
            "timestamp": int(time.time())
        }

        await self.emit_add_layers(sid, [layer])

    async def emit_add_layers(self, sid, layers):
        message = {
            "layers": layers
        }

        await self.sio.emit('add-layers', json.dumps(message), room=sid)
