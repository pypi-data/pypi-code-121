# Copyright (C) 2014 Ipsilon project Contributors, for license see COPYING

import logging
import pwd
import os
import socket
import subprocess

from ipsilon.helpers.common import EnvHelpersInstaller


IPA_CONFIG_FILE = '/etc/ipa/default.conf'
HTTPD_IPA_KEYTAB = '/etc/httpd/conf/ipa.keytab'
IPA_COMMAND = '/usr/bin/ipa'
IPA_GETKEYTAB = '/usr/sbin/ipa-getkeytab'
HTTPD_USER = 'apache'

NO_CREDS_FOR_KEYTAB = """
Valid IPA admin credentials are required to get a keytab.
Please kinit with a pivileged user like 'admin' and retry.
"""

FAILED_TO_GET_KEYTAB = """
A pre-existing keytab was not found and it was not possible to
successfully retrieve a new keytab for the IPA server. Please
manually provide a keytab or resolve the error that cause this
failure (see logs) and retry.
"""


class Installer(EnvHelpersInstaller):

    def __init__(self, *pargs):
        super(Installer, self).__init__()
        self.name = 'ipa'
        self.ptype = 'helper'
        self.logger = None

    def install_args(self, group):
        group.add_argument('--ipa', choices=['yes', 'no', 'auto'],
                           default='auto',
                           help='Helper for IPA joined machines')

    def conf_init(self, opts):
        logger = self.logger
        # Do a simple check to see if machine is ipa joined
        if not os.path.exists(IPA_CONFIG_FILE):
            logger.info('No IPA configuration file. Skipping ipa helper...')
            if opts['ipa'] == 'yes':
                raise Exception('No IPA installation found!')
            return

    def _check_output(self, args, **kwargs):
        env = os.environ.copy()
        # enforce English to disable i18n
        env['LC_ALL'] = env['LANG'] = 'en_US.utf8'
        return subprocess.check_output(
            args, env=env, stderr=subprocess.STDOUT, **kwargs
        )

    def get_keytab(self, opts):
        logger = self.logger
        # Check if we have need ipa tools
        if not os.path.exists(IPA_GETKEYTAB):
            logger.info('ipa-getkeytab missing. Will skip keytab creation.')
            if opts['ipa'] == 'yes':
                raise Exception('No IPA tools found!')

        # Check if we already have a keytab for HTTP
        if 'gssapi_httpd_keytab' in opts:
            msg = "Searching for keytab in: %s" % opts['gssapi_httpd_keytab']
            if os.path.exists(opts['gssapi_httpd_keytab']):
                logger.info("%s... Found!", msg)
                return
            else:
                logger.info("%s... Not found!", msg)

        msg = "Searching for keytab in: %s" % HTTPD_IPA_KEYTAB
        if os.path.exists(HTTPD_IPA_KEYTAB):
            opts['gssapi_httpd_keytab'] = HTTPD_IPA_KEYTAB
            logger.info("%s... Found!", msg)
            return
        else:
            logger.info("%s... Not found!", msg)

        us = socket.gethostname()
        princ = 'HTTP/%s' % us

        # Check we have credentials to access server (for keytab)
        try:
            logger.debug('Try to ping IPA server')
            self._check_output([IPA_COMMAND, 'ping'])
        except subprocess.CalledProcessError as e:
            logger.error('Cannot connect to server: %s', e)
            raise Exception('Unable to connect to IPA server: %s' % e)
        else:
            logger.debug("... Succeeded!")

        # Force is set to True so a DNS A record is not required for
        # adding the service.
        try:
            self._check_output(
                [IPA_COMMAND, 'service-add', princ, '--force']
            )
        except subprocess.CalledProcessError as e:
            if 'already exists' in e.output:
                logger.debug('Principal %s already exists', princ)
            else:
                logger.error('%s', e)
                raise Exception(e.output)

        msg = "Trying to fetch keytab[%s] for %s" % (
              opts['gssapi_httpd_keytab'], princ)
        logger.info(msg)
        gktcmd = [
            IPA_GETKEYTAB, '-p', princ, '-k', opts['gssapi_httpd_keytab']
        ]
        try:
            self._check_output(gktcmd)
        except subprocess.CalledProcessError as e:
            # unfortunately this one is fatal
            logger.error(FAILED_TO_GET_KEYTAB)
            logger.info('Error trying to get HTTP keytab:')
            logger.info('Cmd> %s\n%s', gktcmd, e.output)
            raise Exception(
                'Missing keytab: [Command \'%s\' returned non-zero'
                ' exit status %d]' % (gktcmd, e.returncode)
            )

        # Fixup permissions so only the ipsilon user can read these files
        pw = pwd.getpwnam(HTTPD_USER)
        os.chown(opts['gssapi_httpd_keytab'], pw.pw_uid, pw.pw_gid)

    def configure_server(self, opts, changes):
        if opts['ipa'] != 'yes' and opts['ipa'] != 'auto':
            return
        if opts['ipa'] != 'yes' and opts['gssapi'] == 'no':
            return

        self.logger = logging.getLogger()

        self.conf_init(opts)

        self.get_keytab(opts)

        # Forcibly use gssapi then pam modules
        if 'lm_order' not in opts:
            opts['lm_order'] = []
        opts['gssapi'] = 'yes'
        if 'gssapi' not in opts['lm_order']:
            opts['lm_order'].insert(0, 'gssapi')
        opts['form'] = 'yes'
        opts['info_sssd'] = 'yes'
        if not any(lm in opts['lm_order'] for lm in ('form', 'pam')):
            opts['lm_order'].append('form')
