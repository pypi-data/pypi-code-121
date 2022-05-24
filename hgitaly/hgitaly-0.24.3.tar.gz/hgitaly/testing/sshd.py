# Copyright 2021 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import attr
import os
import pwd
import socket
import subprocess

from . import TEST_DATA_DIR


@attr.s
class SSHServer:
    host_pub_key_path = attr.ib()
    host_priv_key_path = attr.ib()
    config_template_path = attr.ib()
    working_dir = attr.ib()
    authorized_keys_path = attr.ib()
    host_ipv4 = attr.ib(default='127.0.0.1')
    """IPv4 local address for the server to bind to.

    Domain names and IPv6 addresses are not supported (not even `::1`).

    Forcing the communication to be over IPv4 is lame, but it is the most
    reliable current way:
    - only one type of address avoids lots of complications which are not
      relevant for these tests.
    - there are contexts where IPv6 is not available, whereas those where
      the IPv4 loopback is not are excessively rare.
    """
    port = attr.ib(default=None)
    sshd_exe_path = attr.ib(default='/usr/sbin/sshd')
    initialized = False

    def init(self):
        self.user_name = pwd.getpwuid(os.getuid()).pw_name
        self.init_address()
        self.host = self.host_ipv4
        self.init_config()
        self.initialized = True

    def init_address(self):  # pragma no cover (depends on tests invocation)
        """Determine the port for the server to bind to.

        For best reliability in controlled environment such as CI,
        the port is read from the `HGITALY_TESTS_SSHD_PORT` environment
        variable.

        Otherwise, for developer convenience, we determine an available port.
        This is inherently racy, as the port may well not be available any
        more when the SSH server actually starts.
        """
        from_env = os.environ.get('HGITALY_TESTS_SSHD_PORT')
        if from_env is not None:
            self.port = int(from_env)
        else:
            sock = socket.create_server((self.host_ipv4, 0),
                                        family=socket.AF_INET)
            self.port = sock.getsockname()[1]
            sock.close()

    def init_config(self):
        config_path = self.sshd_config_path = self.working_dir / 'sshd_config'
        config_path.write_text(
            self.config_template_path.read_text().format(
                user=self.user_name,
                host=self.host,
                port=self.port,
                authorized_keys_path=self.authorized_keys_path),
            encoding='ascii')

        perms = 0o600  # not tracked by hg, won't look as a file modification
        self.host_pub_key_path.chmod(perms)
        self.host_priv_key_path.chmod(perms)

    def start(self):
        self.process = subprocess.Popen((self.sshd_exe_path,
                                         '-h', self.host_priv_key_path,
                                         '-c', self.host_pub_key_path,
                                         '-f', self.sshd_config_path,
                                         '-D', '-e',
                                         ),
                                        )

    def stop(self):
        self.process.terminate()
        self.process.wait()


def hg_ssh_setup(working_dir):
    server = SSHServer(
        host_pub_key_path=TEST_DATA_DIR / 'ssh_host_ecdsa_key.pub',
        host_priv_key_path=TEST_DATA_DIR / 'ssh_host_ecdsa_key',
        config_template_path=TEST_DATA_DIR / 'sshd_config',
        authorized_keys_path=TEST_DATA_DIR / 'authorized_keys',
        working_dir=working_dir,
    )
    server.init()
    client_key = (TEST_DATA_DIR / 'id_ecdsa_user').read_text()
    known_hosts = (TEST_DATA_DIR / 'known_hosts').read_text().format(
        host=server.host, port=server.port)
    server.start()
    yield server, client_key, known_hosts

    server.stop()
