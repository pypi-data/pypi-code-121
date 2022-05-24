# Copyright (C) 2013 Ipsilon project Contributors, for license see COPYING

from pwd import getpwnam
from ipsilon.login.common import LoginFormBase, LoginManagerBase, \
    LoginManagerInstaller
from ipsilon.util.plugin import PluginObject
from ipsilon.util import config as pconfig
import pam
import subprocess


class Pam(LoginFormBase):

    def POST(self, *args, **kwargs):
        username = kwargs.get("login_name")
        password = kwargs.get("login_password")
        password += kwargs.get("login_otp", "")
        error = None

        if username and password:
            pam_auth = pam.pam()
            result = pam_auth.authenticate(
                username, password, service=self.lm.service_name
            )
            if result:
                # The actual username may be different from the requested
                # username. For example SSSd allows logging in with the email
                # address, but we want the actual username here.
                username = getpwnam(username).pw_name
                self.log("User %s successfully authenticated." % username)
                return self.lm.auth_successful(
                    self.trans, username, 'password'
                )
            else:
                error = pam_auth.reason
                self.error("Error %s: %s" % (pam_auth.code, error))
                return self.lm.auth_failed(self.trans, error)
        else:
            error = "Username or password is missing"
            self.error("Error: %s" % error)

        context = self.create_tmpl_context(
            username=username,
            error=error,
            error_password=not password,
            error_username=not username
        )
        self.lm.set_auth_error()
        return self._template('login/form.html', **context)


class LoginManager(LoginManagerBase):

    def __init__(self, *args, **kwargs):
        super(LoginManager, self).__init__(*args, **kwargs)
        self.name = 'pam'
        self.path = 'pam'
        self.page = None
        self.description = """
Form based login Manager that uses the system's PAM infrastructure
for authentication. """
        self.new_config(
            self.name,
            pconfig.String(
                'service name',
                'The name of the PAM service used to authenticate.',
                'ipsilon',
                readonly=True,
                ),
            pconfig.String(
                'username text',
                'Text used to ask for the username at login time.',
                'Username'),
            pconfig.String(
                'password text',
                'Text used to ask for the password at login time.',
                'Password'),
            pconfig.String(
                'help text',
                'Text used to guide the user at login time.',
                'Provide your Username and Password')
        )

    @property
    def service_name(self):
        return self.get_config_value('service name')

    @property
    def help_text(self):
        return self.get_config_value('help text')

    @property
    def username_text(self):
        return self.get_config_value('username text')

    @property
    def password_text(self):
        return self.get_config_value('password text')

    def get_tree(self, site):
        self.page = Pam(site, self, 'login/pam')
        return self.page


class Installer(LoginManagerInstaller):

    def __init__(self, *pargs):
        super(Installer, self).__init__()
        self.name = 'pam'
        self.pargs = pargs

    def install_args(self, group):
        group.add_argument('--pam', choices=['yes', 'no'], default='no',
                           help='Configure PAM authentication')
        group.add_argument('--pam-service', action='store', default='ipsilon',
                           help='PAM service name to use for authentication')

    def configure(self, opts, changes):
        if opts['pam'] != 'yes':
            return

        # Add configuration data to database
        po = PluginObject(*self.pargs)
        po.name = 'pam'
        po.wipe_data()
        po.wipe_config_values()
        config = {'service name': opts['pam_service']}
        po.save_plugin_config(config)

        # Update global config to add login plugin
        po.is_enabled = True
        po.save_enabled_state()

        # for selinux enabled platforms, ignore if it fails just report
        try:
            subprocess.call(['/usr/sbin/setsebool', '-P',
                             'httpd_mod_auth_pam=on',
                             'httpd_tmp_exec=on'])
        except Exception:  # pylint: disable=broad-except
            pass
