'''
This is Asterisk PBX Salt module
'''
from __future__ import absolute_import, print_function, unicode_literals
import asyncio
from aiorun import run
import concurrent.futures
import logging
import salt.utils.event
import salt.utils.process
from salt.utils import json
try:
    from panoramisk import Manager
    from panoramisk.message import Message as AsteriskMessage
    HAS_LIBS = True
except ImportError:
    HAS_LIBS = False
import time

__virtualname__ = 'asterisk_ami'

log = logging.getLogger(__name__)


def __virtual__():
    if not HAS_LIBS:
        msg = 'Panoramisk lib not found, asterisk module not available.'
        log.warning(msg)
        return False, msg
    return True


class AmiClient:
    events_map = []    

    async def start(self):
        self.event = salt.utils.event.MinionEvent(__opts__)
        self.security_reactor_events = __salt__['config.get']('security_reactor_events')
        # Set trace option
        self.odoo_trace_ami = __salt__['config.get']('odoo_trace_ami')
        # Set process name
        salt.utils.process.appendproctitle(self.__class__.__name__)
        manager_disconnected = asyncio.Event()
        # Get events map from Odoo
        await self.download_events_map()
        # Ok let's connect to Asterisk and process events.
        self.loop = asyncio.get_event_loop()
        # Create event loop to receive actions as events.
        self.loop.create_task(self.action_event_loop())
        host = __salt__['config.get']('ami_host', 'localhost')
        port = int(__salt__['config.get']('ami_port', '5038'))
        login = __salt__['config.get']('ami_login', 'salt')
        ping_interval = __salt__['config.get']('ami_ping_interval', 10)
        self.manager = Manager(
            loop=self.loop,
            host=host,
            port=port,
            username=login,
            ping_interval=ping_interval,
            secret=__salt__['config.get']('ami_secret', 'stack'),
            on_disconnect=self.on_disconnect,
        )
        log.info('AMI connecting to %s@%s:%s...', login, host, port)
        # Register events
        for ev_name in __salt__['config.get']('ami_register_events', []):
            log.info('Registering for AMI event %s', ev_name)
            self.manager.register_event(ev_name, self.on_asterisk_event)
        try:
            await self.manager.connect()
            log.info('Connected to AMI.')
        except Exception as e:
            log.error('Cannot connect to Asterisk AMI: %s', e)
        await manager_disconnected.wait()

    def on_disconnect(self, manager, exc):
        log.warning('Asterisk AMI disconnect: %s', str(exc))

    def true_or_match(self, setting, value):
        if isinstance(setting, bool) and setting or (
           isinstance(setting, list) and value in setting):
            return True
        else:
            return False


    async def download_events_map(self):
        while True:
            # We do it forever until we finally receive it.
            try:
                events_map = __salt__['odoo.execute'](
                    'asterisk_plus.event',
                    'search_read',
                    [[['is_enabled', '=', True], ['source', '=', 'AMI']]],
                    {'fields': ['name','model', 'method', 'delay', 'condition']},
                    log_error=True
                )
                if not events_map:
                    log.error('Cannot download the events map, retrying...')
                    await asyncio.sleep(1)
                    continue
                self.events_map = events_map
                log.info('Downloaded handlers for events: %s',
                         json.dumps(events_map, indent=2))
                return True
            except Exception as e:
                log.error('Events map not loaded: %s', e)
                # Wait 1 second before next attempt
                await asyncio.sleep(1)

    async def on_asterisk_event(self, manager, event):
        event = dict(event)
        trace_events = __opts__.get('ami_trace_events')
        if self.true_or_match(trace_events, event['Event']):
            log.info('AMI Event: %s', json.dumps(event, indent=2))
        # Inject system name in every message
        event['SystemName'] = __grains__['id']
        # Send event to Salt's event bus
        if event['Event'] in self.security_reactor_events and __salt__['config.get']('security_reactor_enabled'):
            __salt__['event.send']('ami_event/{}'.format(event['Event']), event)
        # Check if it is a special OdooExecute UserEvent
        if event['Event'] == 'UserEvent' and event['UserEvent'] == 'OdooExecute':
            self.event.fire_event({
                'model': event['model'],
                'method': event['method'],
                'args': json.loads(event['args']),
                'kwargs': json.loads(event.get('kwargs', "{}")),
            }, 'odoo_execute')
            log.info('Event OdooExecute has been sent to Odoo')
        # Send the event to Odoo if required
        asyncio.ensure_future(self.send_event_to_odoo(event), loop=self.loop)

    async def send_event_to_odoo(self, event):
        """
        Send AMI event to Odoo according to events map.
        """
        event_name = event.get('Event')
        # Iterate over Asterisk events and select only current event handlers.
        handlers = [k for k in self.events_map if k['name'] == event_name]
        # Call handlers.
        for handler in handlers:
            asyncio.ensure_future(self.event_handler(handler, event))

    async def event_handler(self, handler, event):
        event_name = event.get('Event')
        # Check for event condition
        if handler.get('condition'):
            # Handler has a condition so evaluate it first.
            try:
                # TODO: Create a more secure eval context.
                res = eval(handler['condition'],
                           None, {'event': event})
                if not res:
                    # The confition evaluated to False so do not send.
                    if self.odoo_trace_ami:
                        log.info(
                            'Event %s condition evaluated to False',
                            event_name)
                    return
            except Exception:
                log.exception(
                    'Error evaluating condition: %s, event: %s',
                    handler['condition'], event)
                # The confition evaluated to error so do not send.
                return
        # Trace?
        if self.odoo_trace_ami:
            log.info('AMI -> Odoo event: %s', json.dumps(event, indent=2))
        # Sometimes it's required to send event to Odoo with a delay.
        if handler.get('delay'):
            if self.odoo_trace_ami:
                log.info('AMI -> Odoo event %s sleep %s before %s...',
                         event_name, handler['delay'], handler['method'])
            await asyncio.sleep(int(handler['delay']))
            if self.odoo_trace_ami:
                log.info('AMI -> Odoo event %s wakeup for %s.',
                         event_name, handler['method'])
        # Finally send event to Odoo.
        try:
            self.event.fire_event({
                'model': handler['model'],
                'method': handler['method'],
                'args': [event]
            }, 'odoo_execute')
            log.debug('Event %s has been sent to Odoo', event_name)
        except Exception as e:
            log.error('Event %s handler failure: %s', event_name, e)

    async def action_event_loop(self):
        log.debug('AMI action event loop started.')
        event = salt.utils.event.MinionEvent(__opts__)
        trace_actions = __opts__.get('ami_trace_actions')
        while True:
            try:
                evdata = event.get_event(tag='ami_action',
                                         no_block=True)
                # TODO: Connect to Salt's tornado eventloop.
                try:
                    await asyncio.sleep(0.01)
                except concurrent.futures._base.CancelledError:
                    return
                if evdata:
                    # Remove salt's event item
                    evdata.pop('_stamp', False)
                    timeout = evdata.pop('timeout', 0.1)
                    as_list = evdata.pop('as_list', None)
                    reply_channel = evdata.pop('reply_channel', False)
                    # Trace the request if set.
                    if self.true_or_match(trace_actions, evdata['Action']):
                        log.info('AMI Action: %s', evdata)
                    else:
                        log.debug('AMI Action: %s', evdata)
                    try:
                        # Check if this is a custom ReloadEvents action :-)
                        if evdata.get('Action') == 'ReloadEvents':
                            log.info('Reloading the event map.')
                            res = {
                                'Response': await self.download_events_map()}
                        else:
                            # Send action and get action result.
                            res = await asyncio.wait_for(
                                self.manager.send_action(
                                    evdata, as_list=as_list), timeout=timeout)
                            if self.true_or_match(trace_actions, evdata['Action']):
                                log.info('AMI Result: %s', res)
                            else:
                                log.debug('AMI Result: %s', res)
                    except asyncio.TimeoutError:
                        log.error('Send action timeout: %s', evdata)
                        res = {'Message': 'Action Timeout',
                               'Response': 'Error'}
                    except concurrent.futures._base.CancelledError:
                        log.info('AMI action event loop quitting.')
                        return
                    except Exception as e:
                        log.exception('Send action error:')
                        res = str(e)
                    # Make a list of results to unify.
                    if not isinstance(res, list):
                        res = [res]
                    if reply_channel:
                        # Send back the result.
                        __salt__['event.fire'](
                            {'Reply': [dict(k) for k in res]},
                            'ami_reply/{}'.format(reply_channel))

            except Exception as e:
                if "'int' object is not callable" in str(e):
                    # Reaction on CTRL+C :-)
                    log.info('AMI events action lister quitting.')
                    return
                else:
                    log.exception('AMI action event loop error:')
                    await asyncio.sleep(1)  # Protect log flood.


def start():
    run(AmiClient().start())
