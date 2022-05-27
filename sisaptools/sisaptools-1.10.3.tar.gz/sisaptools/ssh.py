# -*- coding: utf8 -*-

"""
Utilitats per SSH.
"""

import paramiko

from .aes import AESCipher
from .services import SSH_SERVERS


class Credentials(object):
    """Captura les credencials de l'alias."""

    def __init__(self, alias):
        self.host = SSH_SERVERS[alias]['host']
        self.port = SSH_SERVERS[alias]['port']
        self.user = SSH_SERVERS[alias]['user']
        self.pwd = AESCipher().decrypt(SSH_SERVERS[alias]['password'])


class SSH(Credentials, paramiko.SSHClient):
    """Execució de cmd per SSH."""

    def __init__(self, alias):
        """Inicialització."""
        Credentials.__init__(self, alias)
        paramiko.SSHClient.__init__(self)
        self.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.connect(self.host, self.port, self.user, self.pwd)

    def execute(self, command):
        """Execució."""
        stdin, stdout, stderr = self.exec_command(command)
        status = stdout.channel.recv_exit_status()
        if status != 0:
            raise SystemError(stderr.read())
        else:
            return stdout.read()


class SFTP(Credentials):
    """Pujar, baixar i eliminar fitxers remots per SFTP."""

    def __init__(self, alias, banner_timout=None):
        """Inicialització."""
        Credentials.__init__(self, alias)
        self.transport = paramiko.Transport((self.host, self.port))
        if not (banner_timout is None):
            self.transport.banner_timout = banner_timout
        self.transport.connect(username=self.user, password=self.pwd)
        self.ls = paramiko.SFTPClient.from_transport(self.transport).listdir
        self.get = paramiko.SFTPClient.from_transport(self.transport).get
        self.put = paramiko.SFTPClient.from_transport(self.transport).put
        self.remove = paramiko.SFTPClient.from_transport(self.transport).remove
        self.chdir = paramiko.SFTPClient.from_transport(self.transport).chdir
        self.mkdir = paramiko.SFTPClient.from_transport(self.transport).mkdir

    def __enter__(self):
        """Context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager."""
        self.transport.close()
