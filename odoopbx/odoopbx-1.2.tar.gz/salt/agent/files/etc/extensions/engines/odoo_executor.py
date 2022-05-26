'''
This is Asterisk PBX Salt module
'''
from __future__ import absolute_import, print_function, unicode_literals
import asyncio
from aiorun import run
import concurrent.futures
import logging
import os
import sys
import time
import salt.utils.event
import salt.utils.process
from salt.utils import json

# Import third party libs
try:
    import odoorpc
    HAS_LIBS = True
except ImportError:
    HAS_LIBS = False


log = logging.getLogger(__name__)


def __virtual__():
    if not HAS_LIBS:
        msg = 'OdooRPC lib not found, Odoo Executor module not available.'
        log.warning(msg)
        return False, msg
    return True


class OdooExecutor:
    def connect(self):
        host = __salt__['config.get']('odoo_host', 'localhost')
        port = int(__salt__['config.get']('odoo_port', 8069))
        # Get database from ENV or config.
        db = os.environ.get('ODOO_DB',
            __salt__['config.get']('odoo_db', 'demo'))
        user = __salt__['config.get']('odoo_user', 'admin')
        password = __salt__['config.get']('odoo_password', 'admin')
        protocol = 'jsonrpc+ssl' if __salt__['config.get'](
            'odoo_use_ssl') else 'jsonrpc'
        while self.loop.is_running():
            try:
                log.info(
                    'Connecting to Odoo %s://%s@%s:%s/%s...', protocol, user, host, port, db)
                self.odoo = odoorpc.ODOO(host, port=port, protocol=protocol)
                self.odoo.login(db, user, password)
                log.info('Logged into Odoo.')
                # Set minion's ID & timezone upon connect.
                minion_id = __salt__['config.get']('id')
                timezone = None
                try:
                    timezone = __salt__['timezone.get_zone']()
                except Exception as e:
                    log.error('Timezone get error: %s', e)
                self.odoo.env['asterisk_plus.server'].set_minion_data(
                    minion_id, timezone)
                break
            except Exception as e:
                log.error('Cannot connect to Odoo: %s', e)
                time.sleep(1)


    async def start(self):
        # Set trace option
        self.odoo_trace_rpc = __salt__['config.get']('odoo_trace_rpc')
        # Set process name
        salt.utils.process.appendproctitle(self.__class__.__name__)
        self.loop = asyncio.get_event_loop()
        # Create event loop to receive actions as events.
        self.connect()
        await self.execute_event_loop()

    async def execute_event_loop(self):
        log.debug('Odoo Execute event loop started.')
        event = salt.utils.event.MinionEvent(__opts__)
        while True:
            evdata = event.get_event(tag='odoo_execute',
                                     no_block=True)
            # TODO: Connect to Salt's tornado eventloop.
            try:
                await asyncio.sleep(0.01)
            except concurrent.futures._base.CancelledError:
                return
            if evdata:
                _stamp = evdata.pop('_stamp', False) # Remove this.
                reply_tag = evdata.pop('_reply_tag', False)
                try:
                    res = await self.execute(evdata)
                    if reply_tag:
                        # Send back the result over salt event bus
                        event.fire_event_async({"result": res}, reply_tag)
                except Exception as e:
                    log.error('Execute %s error: %s', evdata, e)

    async def execute(self, data):
        model = data.get('model')
        method = data.get('method')
        args = data.get('args', [])
        kwargs = data.get('kwargs', {})
        if self.odoo_trace_rpc:
            log.info('Odoo execute: %s', data)
        res = getattr(self.odoo.env[model], method)(*args, **kwargs)
        if self.odoo_trace_rpc:
            log.info('Odoo execute result: %s', res)
        return res


def start():
    log.info('Starting Odoo Executor engine.')
    run(OdooExecutor().start())
