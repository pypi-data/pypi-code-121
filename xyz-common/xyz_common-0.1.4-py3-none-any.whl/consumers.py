# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals
import json

from celery.result import AsyncResult
from channels.generic.websocket import AsyncWebsocketConsumer
from six import text_type

import logging

log = logging.getLogger("django")


class AsyncResultConsumer(AsyncWebsocketConsumer):
    async def send_message(self, message):
        await self.send(('%s\r' % json.dumps(message)).encode('utf8'))

    def pm(self, body):
        try:
            if body['status'] in ['FAILURE', 'REVOKED']:
                body['result'] = text_type(body['result'])
            self.send_message(body)
        except Exception:
            import traceback
            log.error("AsyncResultConsumer dump json error, body: %s; error: %s", body, traceback.format_exc())

    async def connect(self):
        self.task_id = self.scope['url_route']['kwargs']['task_id']
        rs = AsyncResult(self.task_id)
        try:
            r = rs.get(on_message=self.pm, propagate=False)
        except Exception as e:
            body = {'status': 'FAILURE', 'result': text_type(e)}
            self.send_message({'message': body})
        await self.accept()

    async def send_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))
