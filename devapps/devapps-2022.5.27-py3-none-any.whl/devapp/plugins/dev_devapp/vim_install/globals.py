from devapp.tools import sys_args, read_file, write_file, FLG, os
from time import ctime, time as now
import json, sys

have_term = sys.stdout.isatty() and sys.stdin.isatty()


H = os.environ['HOME']


class S:
    pass


class Dir:
    share = lambda: H + '/.local/share'
    work = lambda: FLG.workdir

    class dflt:
        work = lambda: Dir.share() + '/nvim_manager'


fn_settings = lambda w=None: (FLG.workdir if w is None else w) + '/configs.json'


def settings(workdir=None, name=None):
    d = json.loads(read_file(fn_settings(workdir), '{}'))
    return d.get(name, {}) if name is not None else d


all_flags = []

t0 = now()


def set_defaults(Flags):
    n, wd = sys_args(['--name', '-n', 'default'], ['--workdir', '-w', Dir.dflt.work()])
    d = settings(wd, name=n).get('flags', {})
    for k in dir(Flags):
        if k == 'Actions' or k[0] == '_':
            continue
        v = getattr(Flags, k)
        all_flags.append(k)  # so that we can create a new settings entry after install
        setattr(v, 'd', d.get(k, v.d)) if hasattr(v, 'd') else 0


def write_settings():
    d = settings(FLG.workdir)
    f = {k: getattr(FLG, k, '') for k in all_flags}
    m = {}
    m['dt'] = round(now() - t0, 2)
    m['ts'] = int(now())
    m['ts_pretty'] = ctime()
    d[FLG.name] = {'flags': f, 'meta': m}
    write_file(fn_settings(FLG.workdir), json.dumps(d, indent=4, sort_keys=True))
