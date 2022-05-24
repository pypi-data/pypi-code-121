import paramiko
import getpass
from pypers.steps.fetch.download.sftp_pk import SFTP_PK


class SFTP(SFTP_PK):

    def connect(self):
        # getting files from sftp
        self.sftp_params = self.fetch_from['from_sftp']
        self.logger.info('getting %s files from sftp %s %s' % (
            'all' if self.limit == 0 else self.limit,
            self.sftp_params['sftp_server'],
            self.sftp_params['sftp_dir']))

        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.load_system_host_keys()
        self.ssh.connect(self.sftp_params['sftp_server'],
                         username=self.sftp_params['sftp_user'],
                         password=self.sftp_params['sftp_password'])
        return self.ssh.open_sftp()

