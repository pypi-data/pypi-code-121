#!/usr/bin/env python
import os, sys
from devapp.app import do, system, app
from dev_devapp import vim_install  # done by devapp plugin system
from subprocess import call, check_output, STDOUT
from devapp.tools import write_file, unlink
from functools import partial

unlink = partial(unlink, not_exist_ok=True, log=app.info)
exists = vim_install.exists

# class Flags:
#     class distri_astrovim_repo:
#

d_packer = vim_install.H + '/.local/share/nvim/site/pack/packer'
state = vim_install.S
vi_headless = vim_install.vi_headless
exec_ = vim_install.exec_


def ensure_assets_inst():
    unlink(state.distri.symlink() + '/lua/user')
    vim_install.link_assets(vim_install.S.distri)
    do(ensure_packer_installed)
    return do(ensure_astro_packages_installed)


def ensure_packer_installed():
    install_path = d_packer + '/start/packer.nvim'

    if not exists(install_path):
        cmds = [
            'git',
            'clone',
            '--depth',
            '1',
            '"https://github.com/wbthomason/packer.nvim"',
            install_path,
        ]
        exec_(' '.join(cmds), 'Installing packer')

    cmd = vi_headless() + '''-u NONE -c 'lua require("packer")' -c quitall'''
    if call(cmd):
        msg = 'Packer was not installed automatically by AstroVim - sth went wrong'
        app.die(msg)


def call(cmd):
    r = check_output(cmd, shell=True, stderr=STDOUT, executable='/bin/bash')
    return r.decode('utf-8')


def backup_cmd():
    r = state.distri
    d = r.workdir
    fn = r.fn_assets_backup
    unlink(fn, not_exist_ok=True, log=app.info)
    fnb = os.path.basename(r.d_assets)
    return f'cd "{d}" && tar cf "{fn}" "{fnb}"'


def ensure_astro_packages_installed():
    nvi = vi_headless()
    cmd = nvi + '''-c 'lua require("packer").sync()' -c quitall 2>&1'''
    d = vim_install.S.distri.pth
    for i in (1, 2):
        if not os.popen(cmd).read().lower().strip():
            return  # no error, all in sync
        fn = d + '/lua/packer_compiled.lua'
        unlink(fn)
        write_file(fn, '')
        sync_cmd = nvi + "-c 'autocmd User PackerComplete quitall' -c 'PackerSync'"
        exec_(sync_cmd, 'Packer Sync - Please stand by...')
        exec_(backup_cmd(), 'Backing up distri pkgs')
    return True  # we installed sth -> pack


# d = os.path.dirname
# sys.path.insert(0, d(d(__file__)))
# from ..tools import exists, env, d_proj, os, vim_install, logger, OS, utf
#
# # tgz version works also in containers and chroots (w/o kernel fuse module loaded):
# nvim_url = 'https://github.com/neovim/neovim/releases/download/v0.6.1/nvim-linux64.tar.gz'
# # need fast(!) way to check if astro PackerSync was run:
#
#
# call = lambda *a, **kw: utf(OS.call(*a, **kw))
# nvim_ver = lambda dflt=None: call(vim_install(dflt), '-v')
#
#
# class ensures:
#     def nvim_installed():
#         dflt = env['HOME'] + '/nvim-linux64/bin/nvim'
#         if nvim_ver(dflt):
#             return
#         logger.info('Downloading neovim', url=nvim_url)
#         exec_('cd && wget "%s" -O - | tar xfvz -' % nvim_url)
#         env['nvim'] = dflt
#
#     def astro_linked():
#         d_cfg = env['HOME'] + '/.config/nvim'
#         if exists(d_cfg):
#             return
#         os.makedirs(os.path.dirname(d_cfg), exist_ok=True)
#         logger.info('Symlink', frm=d_proj, to=d_cfg)
#         os.symlink(d_proj, d_cfg)
#
#
# def ensure_astro_installed():
#     ensure = lambda what: getattr(ensures, what)() and logger.info(what)
#     ensure('nvim_installed')
#     ensure('astro_linked')
#     ensure('packer_installed')
#     ensure('astro_packages_installed')
#
#
# import argparse
#
#
# def vim_install():
#
#     parser = argparse.ArgumentParser(prog='AstroVim Installer')
#     # parser = argparse.ArgumentParser(prog='PROG', usage='%(prog)s [options]')
#     # parser.add_argument('--foo', nargs='?', help='foo help', default=)
#
#     parser.add_argument(
#         '-ll',
#         '--log-level',
#         choices=['debug', 'info', 'warning', 'error'],
#         default='info',
#     )
#
#     subparsers = parser.add_subparsers(help='sub-command help')
#
#     ia = subparsers.add_parser('install-astrovim', aliases=['ia'])
#
#     it = subparsers.add_parser('install-astrovim-testbed', aliases=['it'])
#
#     # create the parser for the "b" command
#     b = subparsers.add_parser('b', help='b help')
#     b.add_argument('--baz', choices='XYZ', help='baz help')
#
#     print(parser.parse_args(sys.argv[1:]))
#
#
# if __name__ == '__main__':
#     vim_install()
