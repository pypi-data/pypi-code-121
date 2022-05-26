# ©️ OdooPBX by Odooist, Odoo Proprietary License v1.0, 2020

from __future__ import absolute_import, print_function, unicode_literals
import asyncio
from aiorun import run
import concurrent.futures
import logging
import os
import time

import salt.utils.event
import salt.utils.process
from salt.utils import json

try:
    from panoramisk.fast_agi import Application
    HAS_LIBS = True
except ImportError:
    HAS_LIBS = False


log = logging.getLogger(__name__)


def __virtual__():
    if not HAS_LIBS:
        msg = 'Panoramisk lib not found, FastAGI not available.'
        log.warning(msg)
        return False, msg
    return True


@asyncio.coroutine
def tts_create_sound(request):
        log.info('FastAGI request: %s', request.headers)
        headers = dict(request.headers)
        file_name = headers['agi_arg_1']
        text = headers['agi_arg_2']
        language = headers.get('agi_arg_3', 'en-US')
        voice = headers.get('agi_arg_4', 'en-US-Wavenet-A')
        pitch = headers.get('agi_arg_5', 0)
        speaking_rate = headers.get('agi_arg_6', 1)
        __salt__['asterisk.tts_create_sound'](
            file_name, text, language=language,
            voice=voice, pitch=pitch, speaking_rate=speaking_rate)

def fastagi_start():
    loop = asyncio.get_event_loop()
    app = Application()
    app.add_route('tts_create_sound', tts_create_sound)
    coro = asyncio.start_server(
        app.handler,
        host=__salt__['config.get']('fastagi_listen_address', '127.0.0.1'),
        port=int(__salt__['config.get']('fastagi_listen_port', 4574))
    )
    server = loop.run_until_complete(coro)
    try:
        loop.run_forever()
    except KeyboardInterrupt:  # CTRL+C pressed
        pass
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()


def start():
    fastagi_start()
