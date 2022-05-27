import os, sys, subprocess as sp
import time
from functools import partial as p
import re
import shutil

try:
    import pycond
except:
    pycond = None
try:
    import structlog
except:
    cmd = 'pip install --user structlog rich'
    print('structlog and rich required dependencies for output.\nMay I `%s`?' % cmd)
    if input('[Y|n] ').lower() not in ('', 'y'):
        print('unconfirmed - bye.') or sys.exit(1)
    sys.exit(1) if os.system(cmd) else 0
    import structlog


# fmt:off
logger = structlog.get_logger()
dbg, info = logger.debug, logger.info
utf       = lambda b: b.decode('utf-8')
stdout    = sys.stdout.isatty()
env       = os.environ
wait      = time.sleep
now       = time.time
exists    = os.path.exists
# fmt:on

d = os.path.dirname(__file__)
while not '.git' in os.listdir(d):
    d = os.path.dirname(d)
d_proj = d


# some output coloring:
_ = RESET = '\x1b[0m'
col = lambda s, col, bld=1, R=_: f'\x1b[{bld};2;38;5;{col}m%s{R}' if stdout else s
L = lambda s: col(s, 242, 0)  # grey out
H1 = lambda s: col(s, 226)  # header1
H2 = lambda s: col(s, 208)

cur_test = lambda: os.environ['PYTEST_CURRENT_TEST'].replace(' (call)', '').split('::')
session_name = lambda: cur_test()[1]


term_cols = shutil.get_terminal_size((80, 50)).columns


def vi(dflt=None):
    e = env['nvim'] = env.get('nvim', dflt)
    if e:
        return e
    raise Exception('No nvim')


class user_config:
    dirs = {}

    def clear_if_present(*dirs):
        h, t = user_config.dirs, int(now())
        for d in dirs:
            d = d.replace('~', env['HOME'])
            if exists(d):
                dn = f'{d}.backup.{t}'
                os.rename(d, dn)
                h[d] = dn
                logger.warning('Backup up', config_dir=d, backup_dir=dn)

    def restore():
        for d, dn in user_config.dirs.items():
            unlink(d) if exists(d) else 0  # all we work with are symlinks.
            os.rename(dn, d)
            logger.info('Restoring', config_dir=d, backup_dir=dn)


class OS:
    popen = lambda cmd: os.popen(cmd).read().strip()

    def call(*args, enc=None, **kw):
        cmd = ' '.join(args)
        if enc:
            cmd = cmd.encode(enc)
        rr = p(sp.check_output, shell=True, stderr=sp.STDOUT, executable='/bin/bash')
        try:
            res = rr(cmd, **kw)
        except sp.CalledProcessError:
            return b''
        except Exception as ex:
            breakpoint()  # FIXME BREAKPOINT
        return res


class C:
    d_tmp = None  # temp directory where we keep sockets and write test files


def read_file(fn, dflt=None):
    ffn = full_file_name(fn)
    if not exists(ffn):
        if dflt:
            return dflt
        raise Exception('File not found: %s' % fn)
    with open(ffn) as fd:
        return fd.read()


def unindent(s):
    if not s:
        return s
    k = s.lstrip().split('\n', 1)[0]
    ind = s.split(k, 1)[0].rsplit('\n', 1)[-1]
    return s.replace('\n' + ind, '\n').lstrip()


def write_file(fn, content):
    ffn = full_file_name(fn)
    os.makedirs(os.path.dirname(ffn), exist_ok=True)
    with open(ffn, 'w') as fd:
        fd.write(content)
    return ffn


def full_file_name(fn):
    assert fn and isinstance(fn, str)
    if fn[0] == '/':
        return fn
    return C.d_tmp + '/testfiles/' + ':'.join(cur_test()) + '/' + fn


def strip_ansi(lines, ansi_escape=re.compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]')):
    lines = lines.split('\n')
    r = []
    add = r.append
    while lines:
        line = lines.pop(0)
        add(ansi_escape.sub('', line))
    return '\n'.join(r)
