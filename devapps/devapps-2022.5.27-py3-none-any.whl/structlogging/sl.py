"""
SuperLight Structured Logging
-----------------------------

Stdlib Free Fast Logging, Using Structlog Only

Usage:
    axlog.setup_logging()  once per app
    axlog.get_logger('axwifi').info('foo', bar=baz)

    The app may use flags: --log_level=20
"""


import json
import os
import sys
import time

import structlog

# class F:
#     log_fmt = 'plain'
#     log_level = 10
#     log_time_fmt = '%m-%d %H:%M:%S'
#     log_add_thread_name = True
#     log_dev_fmt_coljson = []
#     log_dev_coljson_style = ('paraiso-dark',)
try:
    import ujson
except Exception as ex:
    pass  # that's ok - app to the app to depend on it
from pygments.styles import get_all_styles
from structlog import BoundLoggerBase, PrintLogger, wrap_logger
from structlog.exceptions import DropEvent
from structlogging import stacktrace

# -- Setup for a stdlib logging free, getattr free use:
from structlog.processors import JSONRenderer
from structlogging import processors as ax_log_processors

from devapp.tools import FLG, define_flags

pygm_styles = list(get_all_styles())
pygm_styles.extend(['light', 'dark'])


class flags(stacktrace.flags):
    autoshort = ''

    class log_level:
        n = 'Log level (10: debug, 20: info, ...). You may also say log_level=error'
        d = '20'

    class log_time_fmt:
        n = 'Log time format. Shortcuts: "ISO", "dt"'
        d = '%m-%d %H:%M:%S'

    class log_fmt:
        n = 'Force a log format. 0: off, 1: auto, 2: plain, 3: plain_no_colors, 4: json. '
        n += 'Note: This value can be set away from auto via export log_fmt as well.'
        d = 'auto'

    class log_add_thread_name:
        n = 'Add name of thread'
        d = False

    class log_dev_fmt_coljson:
        n = 'List of keys to log as json.'
        d = 'json,payload'
        t = list

    class log_dev_coljson_style:
        n = 'Pygments style for colorized json. To use the 16 base colors and leave it '
        n += 'to the terminal palette how to render choose light or dark'
        t = sorted(pygm_styles)
        d = 'dark'


define_flags(flags)

# fmt:off
log_levels = {
    'fatal'     : 70,
    'critical'  : 60,
    'error'     : 50,
    'exception' : 50,
    'err'       : 50,
    'warn'      : 40,
    'warning'   : 40,
    'info'      : 20,
    'debug'     : 10,
}
# fmt:on

log_store = []
_log_store_printer = [0]


def enable_log_store():
    p = structlog.get_config()['processors']
    p.insert(-1, add_to_log_store)
    _log_store_printer[0] = p[-1]


def add_to_log_store(_, lev, ev):
    keep = ev.pop('store_log', None)
    if keep is None:
        ll = log_levels.get(lev, None)
        if ll is None:
            return ev
        if ll > 20:
            keep = True
    if keep:
        log_store.append(dict(ev))
    return ev


def print_log_store(title='Stored Logs', p=_log_store_printer):
    print(title, file=sys.stderr)
    [print(p[0]('_', l.get('level'), l)) for l in log_store]


def storing_testlogger(dub_to=None, store=None):
    """for tests - stores into array, optionally dubs to existing logger"""
    store = [] if store is None else store

    def add_log_to_store(logger, _meth_, ev, store=store, log=dub_to):
        d = dict(ev)
        d['_meth_'] = _meth_
        store.append(d)
        if log:
            getattr(log, _meth_)(ev.pop('event'), **ev)
        raise structlog.DropEvent

    gl = structlog.get_logger
    l, m = ('dub', gl) if dub_to is None else (dub_to, structlog.wrap_logger)
    r = m(l, processors=[add_log_to_store])
    r.reset = r.clear = lambda s=store: s.clear()
    r.store = store
    return r


def log_flags():
    flog = get_logger('flag')
    m = FLG.flag_values_dict()
    for k in sorted(m.keys()):
        flog.debug('', **{k: m[k]})


class AXLogger(BoundLoggerBase):
    """A Bound Logger is a concrete one, e.g. stdlib logger"""

    def log(self, event, kw, _meth_od):
        # the frame will allow *pretty* powerful parametrization options
        # todo: allow that for the user
        # the lambda below is also a frame:
        # kw['_frame_'] = sys._getframe().f_back.f_back
        try:
            args, kw = self._process_event(_meth_od, event, kw)
        except DropEvent:
            return
        return self._logger.msg(*args, **kw)


class AppLogLevel:
    """Intermediate resets of devapp app loglevel

    with AppLogLevel(30):
        do_lots_of_stuff()

    """

    def __init__(self, level):
        from devapp.app import app

        self.app = app
        self.level = level
        try:
            self.was_level = app.log._logger.level
        except Exception as ex:

            print('init_app_parse_flags not yet ran')
            raise

    def __enter__(self):
        self.app.log._logger.level = self.level

    def __exit__(self, *a, **kw):
        self.app.log._logger.level = self.was_level


# setting all level methods, like log.warn into the logger:
for l, nr in log_levels.items():
    setattr(AXLogger, l, lambda self, ev, _meth_=l, **kw: self.log(ev, kw, _meth_))


def get_logger(name, level=None, **ctx):
    """supports name and level conventions - matches the processor chain"""
    if not structlog.is_configured():
        setup_logging()

    FLG.log_level = int(log_levels.get(FLG.log_level, FLG.log_level))
    level = level or FLG.log_level
    log = wrap_logger(PrintLogger(file=sys.stderr), wrapper_class=AXLogger)
    log._logger.name = name
    log._logger.level = level
    return log.bind(**ctx)


def filter_by_level(logger, _meth_, ev):
    if log_levels[_meth_] < logger.level:
        raise DropEvent
    return ev


censored = ['password', 'access_token']


def censor_passwords(_, __, ev, _censored=censored):
    """
    Supports to deliver the censor structure in ev or at setup:
    log.info('MyMsg', data={'foo': {'pw': ..}}, censor=('token', ('data', 'pw')))
    """
    censored = ev.pop('censor', _censored)
    for pkw in censored:
        # nested censored value?
        if isinstance(pkw, (list, tuple)):
            pw = ev
            for part in pkw:
                try:
                    pw = pw.get(part)
                except Exception as ex:
                    pw = None
                if not pw:
                    break
        else:
            pw = ev.get(pkw)
        if pw:
            # TODO: does only work with ONE censored field
            k = min(len(pw) - 1, 3)
            v = pw[:k] + '*' * min((len(pw) - k), 10)
            if isinstance(pkw, (list, tuple)):
                cur = ev
                for part in pkw[:-1]:
                    cur = ev[part]
                cur[pkw[-1]] = v

            else:
                ev[pkw] = v
    return ev


def add_logger_name(logger, _, ev):
    # TODO parametrizeable frame info extraction.
    # ev.pop('_frame_')
    ev['logger'] = '%s' % (logger.name)
    return ev


# dest 'json' or term
def std_processors(dest=None, c=[0]):
    if c[0]:
        return c[0]  # once set up: fixed, in use
    if dest is None:
        dest, l = 'term', stacktrace.log_stack_cfg
        if not l[0]:
            stacktrace.set_log_stack_cfg(FLG)

    c[0] = [
        filter_by_level,
        # structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        censor_passwords,
        add_logger_name,
        stacktrace.stack_info(dest),
    ]
    return c[0]


def fmt_to_int(fmt):
    if str(fmt) in ('auto', '1'):
        fmt = os.environ.get('log_fmt', fmt)
    if fmt.isdigit():
        return int(fmt)
    m = {'off': 0, 'auto': 1, 'plain': 2, 'plain_no_colors': 3, 'json': 4}
    return m.get(fmt, 1)


def log_dropper(*a):
    raise structlog.DropEvent


def to_str(obj):
    try:
        return obj.decode('utf-8')
    except:
        return str(obj)


def safe_dumps(obj, to_str=to_str, default=None):
    try:
        # fails when objects are in, e.g. connection sockets:
        # can dump tuple keys
        return ujson.dumps(obj, ensure_ascii=False, reject_bytes=False)
    except:
        try:
            return json.dumps(obj, default=default)
        except Exception as ex:
            return json.dumps(
                {
                    'event': 'cannot log-serialize: %s' % str(obj),
                    'level': 'error',
                    'logger': 'sl',
                    'timestamp': time.time(),
                }
            )


def setup_logging(
    name=None,
    level=None,
    processors=None,
    censor=(),
    # these come from the app. should not overwrite flags except if not given
    log_dev_fmt_coljson=None,
    log_time_fmt=None,
    get_renderer=False,
):
    """
    pygmentize: Those keys, if present, will be rendered as colored json
    This requires app.run done.
    If not: Say FLG(sys.argv)
    """
    # try:
    #     log_fmt = FLG.log_fmt
    # except:
    #     breakpoint()  # FIXME BREAKPOINT
    #     FLG = F

    # are we a real app, or just a test program:
    # fmt:off
    log_fmt                 = FLG.log_fmt
    log_time_fmt            = FLG.log_time_fmt
    log_add_thread_name     = FLG.log_add_thread_name
    log_dev_coljson_style   = FLG.log_dev_coljson_style
    log_dev_fmt_coljson_flg = FLG.log_dev_fmt_coljson
    # fmt:on
    stacktrace.set_log_stack_cfg(FLG)

    if censor:
        censor = [censor] if isinstance(censor, str) else censor
        [censored.append(c) for c in censor if not c in censored]

    fmt = fmt_to_int(log_fmt)
    tty = sys.stdout.isatty()
    if fmt == 4 or (fmt == 1 and not tty):
        dest = 'json'
        rend = JSONRenderer(serializer=safe_dumps)
    else:
        fmt_vals, val_formatters = {}, {}
        # log.info('Response', json=... ) auto formats:
        lc = log_dev_fmt_coljson_flg
        if log_dev_fmt_coljson:
            lc.extend(log_dev_fmt_coljson)
        for k in lc:
            fmt_vals[k] = 'f_coljson'
        fmt_vals['stack'] = 'print_stack'

        # fmt_vals['stack'] = 'f_coljson'  # stack tracebacks always
        s = log_dev_coljson_style
        val_formatters['f_coljson'] = {'formatter': 'coljson', 'style': s}
        val_formatters['print_stack'] = {'formatter': 'stack'}

        # console renderer. colors?
        colors = fmt != 3
        dest = 'term'
        from structlogging import renderers

        rend = renderers.ThemeableConsoleRenderer(
            colors=colors, fmt_vals=fmt_vals, val_formatters=val_formatters
        )

    if get_renderer:
        return rend

    p = processors or std_processors(dest)
    if log_add_thread_name:
        p.insert(1, ax_log_processors.add_thread_name)
    if log_time_fmt:
        p.insert(1, ax_log_processors.TimeStamper(fmt=log_time_fmt))
    p.append(rend)
    if fmt == 0:
        p.insert(0, log_dropper)

    structlog.configure(
        processors=p,
        context_class=dict,
        wrapper_class=AXLogger,
        cache_logger_on_first_use=True,
    )
    # all in one:
    if name is not None:
        return get_logger(name, level=level)


# .
