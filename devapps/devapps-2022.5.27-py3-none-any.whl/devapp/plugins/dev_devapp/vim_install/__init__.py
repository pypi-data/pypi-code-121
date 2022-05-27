#!/usr/bin/env python
"""
Install (Neo)Vim Editor

- in configurable version
- with a "distri" (framwork) (currently AstroVim)
- with user_settings (from configurable repos)

The tool currently works only on Linux.
"""

import os

# Could be done far smaller.

import sys
import time, json
from devapp import tools
from devapp.app import FLG, app, do, run_app, system
from devapp.tools import exists, dirname, read_file, write_file, sys_args, unlink
from devapp.tools_http import download
from structlogging import sl
import requests
from .globals import S, set_defaults, write_settings, H, Dir, have_term


distris = {'astrovim': None}

here = os.path.dirname(__file__)
# api_nvim = 'https://api.github.com/repos/neovim/neovim/releases'
# ver_nvim = 'v0.6.1'
# # url_astro = 'https://github.com/kabinspace/AstroVim'
# d_share = H + '/.local/share/nvim'
# d_cfg = H + '/.config'
# d_cfg_nvim = d_cfg + '/nvim'
# d_cfg_nvim_p = lambda: d_cfg + '/nvim.%s' % FLG.settings
# nvim = H + '/.local/share/nvim.%s.appimage' % ver_nvim
# h = lambda s: s.replace(H, '~')
#


g = getattr


# breakpoint()  # FIXME BREAKPOINT
# r = {'nvim': {'version': FLG.nvim_version}}
# r = {'nvim': {'installed': exists(nvim), 'exe': h(nvim)}}
# r['astrovim'] = {'installed': exists(d_cfg_nvim), 'dir': h(d_cfg_nvim)}
# r['settings'] = {
#     'installed': exists(d_cfg_nvim_p()),
#     'name': FLG.settings,
#     'dir': h(d_cfg_nvim_p()),
# }
# if not FLG.status_verbose:
#     return r
# r['nvim']['versions'] = do(utils.vim_infos, api_nvim)
# return r


class Flags:
    """Install a Developer NeoVim

    We only offer nvim + AstroVim + some custom stuff at this time
    """

    autoshort = ''

    class name:
        s = 'n'
        n = 'Name of this setup'
        d = 'default'

    class workdir:
        s = 'w'
        n = 'Here we store all downloaded configs and backups. Clean up manually from time to time.'
        d = Dir.dflt.work()

    class nvim_url:
        d = 'https://github.com/neovim/neovim/releases/download/{nvim_version}/nvim-linux64.tar.gz'

    class nvim_version:
        d = 'v0.6.1'

    class distri_url:
        d = 'gh:kabinspace/AstroVim'

    class distri_version:
        d = 'latest'

    class settings_url:
        n = 'Repo containing user settings, which `distri.install_settings` can handle.'
        d = ''

    class settings_version:
        n = 'Leave empty to not checkout any version (keep main or master)'
        d = 'latest'

    # class set_alias:
    #     n = 'Adds an alias to your .bashrc or .zshrc. Will check for presence of a $HOME/.aliases file. Set to empty string to not install an alias'
    #     d = 'vi'

    class Actions:
        class legacy_install_stash:
            n = 'Clears the existing unmanaged installation by moving folders away. '
            n += 'Destination is `<workdir>/legacy_installs/backups.<name>/`. '
            n += 'You can restore them later.'
            d = False

            class delete:
                n = 'Delete instead of moving it away'
                d = False

        class legacy_install_restore:
            n = 'Restores backup with given <name>'
            d = False

        class install:
            d = False

        class status:
            d = False

            class verbose:
                s = 'sv'
                d = False

        class run:
            d = True


set_defaults(Flags)
vi = lambda: S.nvim.symlink()
vi_headless = lambda: vi() + ' --headless '


def exec_(cmd, msg, nofail=False):
    app.info(msg, cmd=cmd)
    if os.system(cmd):
        if nofail:
            return 'err'
        app.die('Fatal Error', cmd=cmd)


def ensure_d_avail(d):
    app.die('Target exists. Use --backup', dir=d) if exists(d) else 0


rm_fn = lambda fn: os.unlink(fn) if exists(fn) else False


def status():
    D = Dir.work()
    if not exists(D):
        return app.error('No setup found', hint='Run action: install', workdir=D)
    named_settings = json.loads(read_file(D + '/settings.json', dflt='{}'))
    present = {}
    r = {'named_settings': named_settings, 'present': present}
    for k in 'nvims', 'settings', 'distris':
        present[k] = os.listdir(g(Dir, k)())
    v = fn.vi()
    i = exists(v) and exists(os.readlink(v))
    r['cur'] = {'nvim': {'version': FLG.nvim_version, 'installed': i, 'fn': v}}
    S.status = r
    return r


def link(s, t):
    os.makedirs(dirname(t), exist_ok=True)
    if exists(t):
        if not os.path.islink(t):
            app.die('Expected symlink', path=t, hint='Run action: stash_legacy_install')
        if os.readlink(t) == s:
            return
        os.unlink(t)
    else:
        os.unlink(t) if os.path.islink(t) else 0  # dangling (exists false then)
    os.symlink(s, t)


def link_assets(r):
    os.makedirs(r.d_assets, exist_ok=True)
    link(r.d_assets, Dir.share() + '/nvim')


class Rsc:
    def __init__(r, version):
        # fmt:off
        r.version     = version
        r.typ         = r.__class__.__name__
        r.url         = g(FLG, r.typ + '_url')
        r.name        = r.repo_pth() + ':' + r.version
        r.workdir     = Dir.work() + '/' + r.typ + '.all'
        r.pth         = r.workdir + '/' + r.name
        r.downloaded  = exists(r.pth) or not r.url
        r.d_assets    = r.pth + '.assets'
        os.makedirs(r.workdir, exist_ok=True)
        # fmt:on
        r.post_init()

    symlink_src = lambda r: r.pth
    all_present = lambda r: os.listdir(r.workdir)

    def repo_pth(r):
        """built from url (path_reponame)"""
        s = r.url
        s = s.rsplit('.git', 1)[0] if s.endswith('.git') else s
        s = s.split(':', 1)[1] if s.startswith('git@') else s
        s = s.split('/', 3)[3] if '://' in s else s
        s = s.split(':', 1)[1] if ':' in s[:5] else s  # split off stuff like "gh:"
        s = s.replace('/', '_')
        return s

    post_init = lambda _: None
    __repr__ = lambda r: '%s %s' % (r.typ, r.name)

    def ensure_downloaded(self):
        if self.downloaded:
            return True
        do(self.download)
        self.downloaded = True

    def download(r):
        url = g(FLG, r.typ + '_url')
        if not url:
            return
        if url.startswith('gh:'):
            url = 'git@github.com:' + url[3:]
        if not url.endswith('.git'):
            url += '.git'
        D = r.pth
        while True:
            dpth = '--depth=1' if r.version == 'latest' else ''
            cmd = f'git clone {dpth} "{url}" "{D}"'
            err = do(system, cmd, no_fail=True)
            if not err:
                break
            if url.startswith('git@'):
                a, b = url[4:].split(':', 1)
                url = f'https://{a}/{b}'
                app.info('Trying https...', url=url)
                continue
            app.die('Could not git clone', url=url)
        if not r.version == 'latest':
            v = r.version
            cmd = f'cd "{D}" && git checkout "{v}"'
            exec_(cmd, 'setting version')

    def ensure_linked(r):
        t, s = r.symlink(), r.symlink_src()
        link(s, t)

    def ensure_assets_inst(r):  # overwrite
        pass

    ensure_installed = lambda r: not r.url or (
        app.info('Resource', name=r.name),
        do(r.ensure_downloaded),
        do(r.ensure_linked),
        do(r.ensure_assets_inst),
    )


class nvim(Rsc):
    symlink = lambda _: Dir.work() + '/nvim'
    repo_pth = lambda _: 'nvim'

    def download(self):
        V = self.version
        D = self.pth
        os.makedirs(D, exist_ok=True)
        url = FLG.nvim_url.format(nvim_version=V)
        if not url.rsplit('.', 1)[-1] in ['tgz', 'gz']:
            app.die('Require .tgz url', have=url)
        FN = D + '.tgz'
        rm_fn(FN)
        download(url, FN, 'u+x')
        do(system, f'tar xfz "{FN}" --directory="{D}"')
        os.unlink(FN)

    def symlink_src(self):
        D = self.pth
        v = lambda k: D + '/' + k + '/bin/nvim'
        for k in os.listdir(D):
            if exists(v(k)):
                return v(k)
        app.die('could not find bin/nvim', path=D)


from importlib import import_module


class distri(Rsc):
    symlink = lambda _: H + '/.config/nvim'

    def post_init(r):
        """
        import the distri module, for specific functions.
        We find the module by matching the name, that's a convention.
        """
        r.fn_assets_backup = r.d_assets + '.backup.tar'
        n = r.name
        _ = 'devapp.plugins.dev_devapp.vim_install.distris.'
        for k, mod in distris.items():
            if k in n.lower():
                r.module = mod or import_module(_ + k)
                break

    def ensure_assets_inst(r):
        r.module.ensure_assets_inst()


class settings(Rsc):
    symlink = lambda _: H + '/.config/nvim.user'

    def ensure_assets_inst(r):
        link(r.symlink(), S.distri.symlink() + '/lua/user')
        if exists(r.d_assets):
            link_assets(r)
        else:
            # We have not yet the assets.
            # We save a lot of time when we re-use the already existing nvim assets
            # but also we don't screw the up with ours. We can't relay on overlay
            # filesystem magic - but we have the backup:
            app.info('no assets yet - using distri assets')
            D = S.distri
            d, wd, fnb = D.d_assets, D.workdir, D.fn_assets_backup
            0 if exists(d) else app.die('expected present distri assets', dir=d)
            os.rename(d, r.d_assets)
            if not exists(fnb):
                app.error('no backup', expected=fnb)
            else:
                cmd = f'cd "{wd}" && tar xf "{fnb}"'
                exec_(cmd, 'restoring distri packages')
            link_assets(r)
        nvi = vi_headless()
        sync_cmd = nvi + "-c 'autocmd User PackerComplete quitall' -c 'PackerSync'"
        # give user configs the chance to exit early after pkg install:
        sync_cmd = 'export setup_mode=true && ' + sync_cmd
        exec_(sync_cmd, 'Packer Sync - Please stand by...')


class Action:
    def _pre():
        sl.enable_log_store()
        S.nvim = nvim(FLG.nvim_version)
        S.distri = distri(FLG.distri_version)
        S.settings = settings(FLG.settings_version)
        S.d_backups = FLG.workdir + '/legacy_installs'
        app.die = lambda *a, **kw: (app.error(*a, **kw), sys.exit(1))

    def legacy_install_stash(dirs=('.config/nvim', '.local/share/nvim')):
        from .legacy_installs import stash

        return stash(dirs)

    def legacy_install_restore():
        from .legacy_installs import unstash

        return unstash()

    def install():
        S.nvim.ensure_installed()
        S.distri.ensure_installed()
        S.settings.ensure_installed()
        write_settings()

    status = status

    def run():
        argv = sys.argv[2:]
        cmd = S.nvim.symlink() + ' ' + ' '.join(['"%s"' % a for a in argv])
        sys.exit(os.system(cmd))


main = lambda: run_app(Action, flags=Flags)


if __name__ == '__main__':
    main()


# begin_archive


#
# class inst:
#     def do():
#         S.nvim.ensure_installed()
#
#         status()
#
#         do(inst.ensure_nvim)
#         do(distris[FLG.distri].ensure_installed)
#
#     def neovim():
#         v = FLG.nvim_version
#         url_nvim = vim_infos().get(v)
#         if not url_nvim:
#             app.die('Not existing nvim release', rel=v)
#         url_nvim = url_nvim['appimg']['browser_download_url']
#         do(download, url_nvim, to=nvim, chmod='u+x', store=True)
#
#     def astrovim():
#         os.makedirs(H + '/.config', exist_ok=True)
#         ensure_d_avail(d_cfg_nvim)
#         cmd = 'git clone "%s" "%s"' % (url_astro, d_cfg_nvim)
#         do(system, cmd, store=True)
#
#     def packer_sync():
#         """Non interactive install
#         (https://github.com/wbthomason/packer.nvim/issues/502)
#         setup_mode allows the init.lua to only install plugins, so that nothing requiring
#         them crashes.
#         """
#         cmd = 'export setup_mode=true; ' + nvim
#         cmd += " --headless -c 'autocmd User PackerComplete quitall' -c 'PackerSync'"
#         do(system, cmd)
#
