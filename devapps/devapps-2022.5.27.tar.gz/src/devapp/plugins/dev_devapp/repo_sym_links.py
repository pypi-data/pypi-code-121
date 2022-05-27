#!/usr/bin/env python
"""
Repolinks

Say your_repo depends on packages devapps and docutools.

You have those checked out next to your_repo:

├── devapps
│       ├── src
│            ├── devapp
│            ├── tree_builder
├── docutools
│       ├── src
│            ├── lcdoc
└── your_repo

Since you installed the package version, lcdoc is installed e.g. in

`$HOME/miniconda3/envs/devapps_py3.7/lib/python3.7/site-packages/lcdoc/`

Saying:

    dev rsl -r 'devapps,docutool,../relpath_to_other_repo,/abs/path/to/repo' link

- will move all importable(!) package folders from devapps and docutools and the 2 other
  repos to a backup dir (in site-packages/repo_sym_link_backup)
- symlink the repo versions into your site-packages dir 

Result:

> You can work on many repos at the same time w/o having to change your pyproject.yaml file.


"""

import os


# Could be done far smaller.
from datetime import datetime
from importlib import import_module

from devapp import gevent_patched, tools
from devapp.app import FLG, app, do, run_app, system
from devapp.tools import exists

# ran these & return the output of the last one (links function):
from json import dumps, loads
import devapp

d_sitep = None
d_backup = lambda: d_sitep + '/backup_repo_symlinks'


path = os.path
dirs = os.listdir
here = os.getcwd()

H = os.environ['HOME']

repl_home = lambda r: loads(dumps(r).replace(H, '~'))


class Flags:
    autoshort = ''

    class repos:
        s = 'r'
        n = 'Comma sep. repos, where we should look for packages. Those repos must have their sources within a "/src" dir - (devapp convention).\n'
        n += '- w/o "/": Must be siblings to this one.\n'
        n += '- otherwise rel. or absolute paths to them.'
        t = list

    class force:
        d = False

    class Actions:
        class list:
            d = True

        class link:
            d = False

        class restore:
            s = 'rest'
            n = 'removes links and restores original folders from backup dir'
            d = False


todos = {}

msg_deb = 'delete existing backup'


def inspect(d_repo):
    if not '.git' in dirs(here):
        app.die('Need to be in repo root')
    if d_repo == here:
        app.info('Ignoring our own repo', dir=d_repo)
        return
    todos[d_repo] = mods = []
    if not (exists(d_repo + '/.git') and exists(d_repo + '/src')):
        app.die('No repo to link', dir=d_repo)
    d_repo += '/src'
    for k in dirs(d_repo):
        ddr = d_repo + '/' + k
        if not path.isdir(ddr):
            continue
        try:
            D = {'mod': import_module(k), 'd_src': ddr, 'name': k}
            if '(namespace)' in str(D):
                mods.append(D)
            else:
                mods.insert(0, D)
        except:
            app.warning('Ignoring (not importable)', dir=k, within=d_repo)
    for mod in mods:
        f = getattr(mod['mod'], '__file__', None)
        if f:
            mod['file'] = f
        else:
            mod['file'] = d_sitep + '/%(name)s/<namespace>' % mod

    for mod in mods:
        ddr = mod['d_src']
        mod.pop('mod')
        d = mod['d_target'] = mod.pop('file').rsplit('/', 1)[0]
        mod['link_present'] = path.islink(d)
        mod['d_backup'] = dcp = d_backup() + '/%(name)s' % mod
        mod['backup_present'] = path.exists(dcp)
    return mods


def report(repo, c=[0]):
    if c[0]:
        return
    if not todos:
        app.die('Nothing to do')
    c[0] += 1
    msg = 'Will create the following symlinks'
    app.warn(msg)
    app.info('spec', json=todos)
    if not 'y' in input('Confirm todos [y|Q] ').lower():
        app.die('Unconfirmed...')


links = lambda repo: [do(link, spec=v) for v in todos[repo]]


def link(spec):
    s, t, b = spec['d_src'], spec['d_target'], spec['d_backup']
    if b:
        app.warn('unlinking existing', backup=b)
        os.system('/bin/rm -rf "%s"' % b)
    os.makedirs(os.path.dirname(b), exist_ok=True)
    app.info('moving to backup', frm=t, to=b)
    os.rename(t, b)
    app.info('symlinking', frm=s, to=t)
    os.symlink(s, t)
    return {'Linked': '%s->%s' % (s, t)}


def status():
    links = [l for l in os.listdir(d_sitep) if os.path.islink(d_sitep + '/' + l)]
    d = d_backup()
    backups = os.listdir(d) if os.path.exists(d) else []
    # if not FLG.repos: app.die('No repo matches given')
    r = {r: do(inspect, d_repo=r, ll=10) for r in FLG.repos}
    st = 'clean'
    if links:
        st = 'tainted'
        app.warn('There are symlinks present -> your installation is tainted')
    r = {
        'present': {'symlinks': links, 'backups': backups, 'site_packages': d_sitep},
        'repos': r,
        'status': st,
    }
    return r


class ActionNS:
    def _pre():
        def p(p):
            a = os.path.abspath
            if not '/' in p:
                return a('../' + p)
            return a(p)

        FLG.repos = [p(i) for i in FLG.repos]
        global d_sitep
        d_sitep = devapp.__file__.rsplit('/', 2)[0]

    def list():
        return repl_home(status())

    def link():
        st = status()
        jobs = []
        if not st['repos']:
            app.die('No repos give to link')
        for _, R in st['repos'].items():
            for mod in R:
                if mod.get('link_present'):
                    app.info('Already linked', d=mod['d_target'])
                    continue
                jobs.append(mod)
        if not jobs:
            return app.info('Nothing to do')
        app.info('Confirm links', json=jobs)

        if not FLG.force:
            if not 'y' in input('Confirm todos [y|Q] ').lower():
                app.die('Unconfirmed...')
        [link(j) for j in jobs]
        return ActionNS.list()

    def restore():
        st = status()['present']
        jobs = []
        for d in st['backups']:
            if d in st['symlinks']:
                jobs.append(d)

        if not jobs:
            app.die('Nothing to do')
        if not FLG.force:
            app.info('Confirm restore', json=jobs)
            if not 'y' in input('Confirm todos [y|Q] ').lower():
                app.die('Unconfirmed...')
        for d in jobs:
            os.unlink(d_sitep + '/' + d)
            os.rename(d_backup() + '/' + d, d_sitep + '/' + d)
        return ActionNS.list()


main = lambda: run_app(ActionNS, flags=Flags)


if __name__ == '__main__':
    main()
