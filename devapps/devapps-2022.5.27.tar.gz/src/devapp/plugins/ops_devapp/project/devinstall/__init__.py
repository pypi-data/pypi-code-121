"""
Project scaffolding tool.

Creates files from blueprints pulled from `files_base`, replacing some variables.

Ignores files which are already present -> delete them to have new ones created.

Assumptions:

    - gitlab repos, if not gitlab.com are deemed as private
    - gitlab pages server on http


"""

import json
import os
import readline
import sys
from datetime import date
from functools import partial

import requests
import toml
import yaml

from devapp.app import app, do
from devapp.tools import exists, get_deep, read_file, write_file

today = date.today()
here = lambda: os.getcwd()
g = lambda k, v, d=None: getattr(k, v, d)


def do(*a, d=do, **kw):
    kw['ll'] = kw.get('ll', 10)
    return d(*a, **kw)


files_base = 'https://raw.githubusercontent.com/axiros/docutools/master/'
get_file_master = lambda fn: requests.get(files_base + fn).text

Files = [
    'make',
    'environ',
    'mkdocs.yml',
    'pyproject.toml',
    'scripts/conda.sh',
    'scripts/self_update',
    'docs/mdreplace.py',
    'docs/about/changelog.md',
    'docs/about/coverage.md',
    'docs/about/credits.md',
    'docs/about/todo.md',
    'docs/about/navigation.md',
    'config/coverage.lp.ini',
    'config/coverage.pytest.ini',
    'config/pytest.ini',
]


class vars:
    have = {}
    variables = set()

    class project_name:
        pyproj_key = 'tool.poetry.name'
        env_key = 'PROJECT'
        dflt = lambda: os.path.basename(here())

    class project_description:
        pyproj_key = 'tool.poetry.description'

    class pyver:
        env_key = 'pyver'
        pyproj_key = 'tool.poetry.dependencies.python'
        dflt = lambda: '%s.%s' % (sys.version_info.major, sys.version_info.minor)

        def validate(v):
            l = v.split('.', 1)  # ^3.5 -> 3.
            return l[0][-1] + '.' + l[1]

    class version:
        pyproj_key = 'tool.poetry.version'
        dflt = lambda: '%s.%02d.%02d' % (today.year, today.month, today.day)

    class author:
        pyproj_key = 'tool.poetry.authors'

        def dflt(_=lambda k: os.popen('git config --get user.%s' % k).read().strip()):
            return '%s <%s>' % (_('name'), _('email'))

        def validate(v: str):
            if isinstance(v, list):
                v = v[0]
            assert '@' in v and '<' in v and '>' in v, 'Require valid email'
            return v

    class license:
        pyproj_key = 'tool.poetry.license'
        dflt = 'Commercial'

    class repository:
        pyproj_key = 'tool.poetry.repository'
        exmpl = [
            'https://github.com/mycompany/myproject',
            'https://gitlab.mycompany.com/mycompany/myproject',
        ]

        def validate(v):
            assert v.startswith('https://'), 'Must start with https://'
            return v

    class dependencies:
        pyproj_key = 'tool.poetry.dependencies'
        dflt = lambda: get_toppest_devapp_pgk(['devapps'])

        def validate(v):
            if isinstance(v, str):
                v = (v, '*')
            if isinstance(v, tuple):
                v = {v[0]: '^' + v[1]}
            return v


for k in dir(vars):
    if isinstance(g(vars, k), type) and not k[0] == '_':
        vars.variables.add(g(vars, k).__name__)


class Have:
    git = {}
    environ = {}
    pyproject = {}
    mkdocs = {}
    prev_answers = {}

    def load_previous_answers():
        a = json.loads(read_file(fn_answ(), dflt='{}'))
        if a:
            app.info('Using previous answers at', fn=fn_answ(), **a)
        Have.prev_answers.update(a)

    def read_environ_files():
        # for f in 'environ', 'environ.personal':
        #     fn = here() + '/' + f
        #     if os.path.exists(fn):
        #         dependent on /bin/sh, too unreliable - he has to source it:
        #         p = os.popen('source "%s" only; env' % fn).read().splitlines()
        #         for line in p:
        #             l = line.split('=', 1)
        #             Have.environ[l[0]] = l[1]
        Have.environ.update(os.environ)

    def load_pyproject_toml():
        fn = here() + '/pyproject.toml'
        if exists(fn):
            Have.pyproject.update(toml.load(fn))

    def load_mkdocs():
        fn = here() + '/mkdocs.yml'
        if exists(fn):
            s = read_file(fn)
            y = yaml.load(s, Loader=yaml.Loader)
            Have.mkdocs.update(y)


def fn_answ():
    return '/tmp/ops_proj_answers_%s.json' % today


def ask(k, ex=''):
    answers = Have.prev_answers
    v = answers.get(k)
    if v:
        return v
    if ex:
        if isinstance(ex, str):
            ex = [ex]
        s = '' if len(ex) == 1 else 's'
        print('Example%s: ' % s + ', '.join(ex))
    r = input('Require value for \x1b[1;32m%s\x1b[0m [q: quit]: ' % k)
    if r in ('', 'q'):
        app.info('bye...')
        sys.exit(1)
    answers[k] = r
    write_file(fn_answ(), s=json.dumps(answers, indent=4, sort_keys=True))
    return r


def get_toppest_devapp_pgk(p, version=None):
    from pip._internal.commands.show import search_packages_info

    while True:
        for k in search_packages_info(p):
            f = k.required_by
            if f:
                return get_toppest_devapp_pgk(f)
            return k.name, k.version


def set_var(V):
    cls, v = g(vars, V), None
    k = g(cls, 'pyproj_key')
    if k:
        v = get_deep(k, Have.pyproject, dflt='')
    if not v:
        k = g(cls, 'env_key')
        if k:
            v = Have.environ.get(k)
    if not v:
        v = g(cls, 'dflt', lambda: None)
        if callable(v):
            v = v()
    exampl = g(cls, 'exmpl', '')
    if not v:
        v = ask(V, ex=exampl)
    val = g(cls, 'validate')
    if val:
        while 1:
            try:
                v = val(v)
                break
            except Exception as ex:
                Have.prev_answers.pop(V, 0)
                app.error('Cannot validate', key=V, value=v, reason=str(ex))
                v = ask(V, exampl)
    app.info(V, value=v)
    vars.have[V] = v


def homepage(repo):
    l = repo.split('/')
    h, g, n = l[-3], l[-2], l[-1]
    if 'gitlab' in repo:
        return 'http://%s.%s/%s' % (g, h.replace('gitlab', 'pages'), n)
    elif 'github' in repo:
        return 'https://%s.github.io/%s/' % (g, n)
    app.warn('Cannot derive docu homepage - using repo', homepage=repo)
    return repo


def ymldict(nav):
    d = {}
    for m in nav:
        d[list(m.keys())[0]] = list(m.values())[0]
    return d


def is_private():
    r = vars.have['repository']
    if '//gitlab' in r and not 'gitlab.com' in r:
        return True


def private_pypi():
    fn = os.environ['HOME'] + '/.config/pypoetry/config.toml'
    if not exists(fn):
        return app.info('No private pypi config found', fn=fn)
    t = toml.load(fn)
    return [
        {'name': k, 'secondary': True, 'url': v['url']}
        for k, v in t.get('repositories', {}).items()
        if v['url'].endswith('simple/')
    ]


class files:
    written = []
    skipped = []

    def adapt_environ(s):
        lines = s.splitlines()
        for k, n in [['PROJECT', 'project_name'], ['pyver', 'pyver']]:
            r = []
            while lines:
                l = lines.pop()
                if l.startswith(k + '='):
                    l = k + '="%s"' % vars.have[n]
                r.append(l)
            lines = r
        return '\n'.join(lines)

    def adapt_mkdocs_yml(s):
        y = yaml.load(s, Loader=yaml.Loader)
        h = vars.have
        y['repo_name'] = h['project_name']
        y['repo_url'] = h['repository']
        y['site_description'] = h['project_description']
        y['site_name'] = h['project_name']
        y['site_url'] = do(homepage, h['repository'])
        n = ymldict(y['nav'])['About']
        y['nav'] = [{'Overview': 'index.md'}]
        y['nav'].append({'About': n})
        return yaml.dump(y)

    def adapt_pyproject_toml(s):
        h = vars.have
        t = toml.loads(s)
        T = t['tool']['poetry']
        # fmt:off
        T['authors']      = [h['author']]
        T['dependencies'] = h['dependencies']
        T['description']  = h['project_description']
        T['homepage']     = do(homepage, h['repository'])
        T['license']      = h['license']
        T['name']         = h['project_name']
        T['packages']     = [{'from': 'src', 'include': h['project_name']}]
        T['repository']   = h['repository']
        if is_private():
            T['source']       = private_pypi()
        T['version']      = h['version']
        # fmt:on
        T['dependencies'].update({'python': '^' + h['pyver']})
        T['dev-dependencies'] = {'docutools': '*'}
        return toml.dumps(t)

    def write(fn):
        s = get_file_master(fn)
        if not '\n' in s:
            s = get_file_master(s)
        if not '\n' in s:
            app.die('Cannot get master file', fn=fn)

        f = g(files, 'adapt_' + fn.replace('.', '_').replace('/', '_'))
        if f:
            s = f(s)
        write_file(fn, s, mkdir=True)
        files.written.append(fn)

    def write_all():
        for fn in Files:
            if exists(here() + '/' + fn):
                app.debug('ignoring (exists already)', fn=fn)
                files.skipped.append(fn)
                continue
            do(files.write, fn, ll=20)
        app.info(
            'Change report', json={'skipped': files.skipped, 'created': files.written}
        )


def dev_install():
    do(Have.load_previous_answers)
    do(Have.read_environ_files)
    do(Have.load_pyproject_toml)
    do(Have.load_mkdocs)
    for V in sorted(vars.variables):
        do(set_var, V)
    do(files.write_all)
    sys.exit(1)
    # mk_file.write
    # write_env_file(proj_vars)
    # write_mkdocs_yml

    # app.debug('finding base package')
    # have = get_current_dir_state_vars()
    # p = get_toppest_devapp_pgk(['devapps',])
    # app.debug('base package', name=p)

    # breakpoint()  # FIXME BREAKPOINT
    # print('foo')
