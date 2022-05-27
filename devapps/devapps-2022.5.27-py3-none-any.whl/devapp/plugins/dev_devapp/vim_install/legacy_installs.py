from devapp.app import app, FLG
from devapp.tools import os, exists, dirname, write_file, unlink
from dev_devapp import vim_install
import time

H = vim_install.H
S = vim_install.S
legacy_backup_dir = lambda: S.d_backups + '/backup.%s' % FLG.name


def stash(dirs):
    def is_unmanaged(d):
        d = H + '/' + d
        if not os.path.exists(d):
            return False
        if not os.path.islink(d):
            return True
        if not os.readlink(d).startswith(FLG.workdir):
            return True

    D = [d for d in dirs if is_unmanaged(d)]
    if not D:
        return app.info('No legacy install found', dirs=dirs)
    db = legacy_backup_dir()
    if exists(db):
        hint = 'Provide another --name for the backup'
        app.die('Backup "%s" already exists' % FLG.name, db=db, hint=hint)
    os.makedirs(db)
    for d in D:
        d1 = d.replace('/', '___')
        dto = db + '/' + d1
        os.rename(H + '/' + d, dto)
        app.info('stashed', dir=d, to=dto)
        write_file(db + '/README.txt', 'Created %s\n' % time.ctime())
    hint = 'Your nvim executable is left in place'
    app.info('Backup done', dir=db, hint=hint)


def unstash():
    db = legacy_backup_dir()
    if not exists(db):
        app.die('Not found', d=db)
    for k in os.listdir(db):
        if k == 'README.txt':
            continue
        d = H + '/' + k.replace('___', '/')
        app.info('Restoring', dir=d, stash=db + '/' + k)
        os.makedirs(dirname(d), exist_ok=True)
        eh = 'The directory seems not being managed. Remove manually.'
        unlink(d, not_exist_ok=True, log=app.warn, err_hint=eh)
        os.rename(db + '/' + k, d)
    if os.listdir(db) == ['README.txt']:
        os.unlink(db + '/README.txt')
        os.rmdir(db)
        app.warn('Removed backup dir', dir=db)
    hint = 'Make sure you point your neovim command to the original nvim executable'
    app.info('Backup restored', hint=hint)
