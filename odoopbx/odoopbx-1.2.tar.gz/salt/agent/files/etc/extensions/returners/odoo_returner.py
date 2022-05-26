import logging
import salt.utils.event

__virtualname__ = "odoo"

log = logging.getLogger(__name__)


def __virtual__():
    return __virtualname__


def returner(ret):
    event = salt.utils.event.MinionEvent(__opts__)
    event.fire_event({
        'model': 'asterisk_plus.salt_job',
        'method': 'returner',
        'args': [ret]
    }, 'odoo_execute')
    log.debug('Return has been sent to Odoo: %s', ret)
