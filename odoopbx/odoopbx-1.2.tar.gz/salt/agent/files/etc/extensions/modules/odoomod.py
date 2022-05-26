import logging
import os
from salt.utils import json
import time

__virtualname__ = 'odoo'

# Import third party libs
try:
    import odoorpc
    HAS_LIBS = True
except ImportError:
    HAS_LIBS = False

log = logging.getLogger(__name__)


def __virtual__():
    '''
    Only load if celery libraries exist.
    '''
    if not HAS_LIBS:
        msg = 'OdooRPC lib not found, odoo module not available.'
        log.warning(msg)
        return False, msg
    # Return virtual module name:
    return 'odoo'


def ping():
    return 'pong'


def _get_odoo(host=None, port=None, user=None, password=None, db=None,
              protocol=None):
    """
    This is helper function to login into Odoo and share the connection.
    """
    odoo = __context__.get('odoo_client')
    if not odoo:
        # Set connection options.
        if not host:
            host = __salt__['config.get']('odoo_host', 'localhost')
        if not port:
            port = int(__salt__['config.get']('odoo_port', 8069))
        if not db:
            # Get database from ENV or config.
            db = os.environ.get('ODOO_DB',
                __salt__['config.get']('odoo_db', 'demo'))
        if not user:
            user = __salt__['config.get']('odoo_user', 'admin')
        if not password:
            password = __salt__['config.get']('odoo_password', 'admin')
        if not protocol:
            protocol = 'jsonrpc+ssl' if __salt__['config.get'](
                'odoo_use_ssl') else 'jsonrpc'
        # Create an OdooRPC object and login.
        odoo = odoorpc.ODOO(host, port=port, protocol=protocol)
        odoo.login(db, user, password)
        # Keep the connection object in salt context.
        __context__['odoo_client'] = odoo
    return odoo


def execute(model, method, args, kwargs={}, log_error=True):
    """
    Execute Odoo method.

    CLI example: odoo.execute res.partner search '[[["name","ilike","admin"]]]'
    """
    # Trace request / response
    if __salt__['config.get']('odoo_trace_rpc'):
        # Hack not to trace file operations is it makes screen not readable
        if method == 'call_recording_data':
            log.info('Odoo execute: %s.%s', model, method)
        else:
            log.info('Odoo execute: %s.%s %s %s', model, method, args, kwargs)
    else:
        log.debug('Odoo execute: %s.%s %s %s', model, method, args, kwargs)
    # Try to parse args
    if type(args) is str:
        args = json.loads(args)
    args = tuple(args)
    try:
        odoo = _get_odoo()
        res = getattr(odoo.env[model], method)(*args, **kwargs)
        if __salt__['config.get']('odoo_trace_rpc'):
            log.info('Odoo result: %s', res)
        return res
    except Exception as e:
        if log_error:
            log.error('Odoo RPC %s.%s error: %s', model, method, e)
        if __salt__['config.get']('odoo_raise_exception', False):
            raise


def notify_user(uid, message, title='Notification',
                warning=False, sticky=False):
    """
    Send notification to Odoo user by his uid.

    CLI examples:
        salt asterisk odoo.notify_user 2 'Hello admin!'
        salt asterisk odoo.notify_user 2 'Error' warning=True sticky=True
    """    
    log.debug('Notify user %s: %s', uid, message)
    odoo = _get_odoo()
    __salt__['odoo.execute'](
        'asterisk_common.settings', 'bus_sendone',
        ['remote_agent_notification_{}'.format(uid), {
            'message': message,
            'warning': warning,
            'sticky': sticky,
            'title': title
        }])
