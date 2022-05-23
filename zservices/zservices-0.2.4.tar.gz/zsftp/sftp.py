from zsftp import logger
from zsftp.config import Config
import paramiko


class SFTP:
    def __init__(self, connection_parameter=None):
        logger.debug('[SFTP]: Initiating Sftp Connection Class')
        self._connection_parameter = connection_parameter
        if self._connection_parameter:
            self.set_connection_parameter(**connection_parameter)
        self._client = None
        self._allow_agent = False
        self._look_for_keys = False

    def set_connection_parameter(self, **kwargs):
        self._connection_parameter = {
            'hostname': Config.SFTP['hostname'] if not kwargs.get('hostname') else kwargs.get('hostname'),
            "username": Config.SFTP['username'] if not kwargs.get('username') else kwargs.get('username'),
            "password": Config.SFTP['password'] if not kwargs.get('password') else kwargs.get('password'),
        }

    def get_connection_parameter(self):
        return self._connection_parameter

    @property
    def connection(self):
        if self._client is None:
            self.connect()
        return self._client

    def connect(self):
        if self._connection_parameter is None:
            self.set_connection_parameter()
        try:
            logger.debug('[SFTP]: Creating Sftp Connection')
            sftp_client = paramiko.SSHClient()
            sftp_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            sftp_client.connect(hostname=self._connection_parameter['hostname'],
                                username=self._connection_parameter['username'],
                                password=self._connection_parameter['password'],
                                allow_agent=self._allow_agent, look_for_keys=self._look_for_keys)
            sftp = sftp_client.open_sftp()
            sftp.listdir()
            self._client = sftp
            return sftp
        except Exception as e:
            self._client = None
            logger.error(f'[SFTP]: Connection issue, conn={self._client}', exc_info=True)
            raise Exception(f'[SFTP]: Connection error {self._connection_parameter["hostname"]}. error={e}')
