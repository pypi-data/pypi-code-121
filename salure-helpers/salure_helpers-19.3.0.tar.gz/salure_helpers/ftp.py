import os
import ftplib
import pysftp
import time
from ftplib import FTP


class FTPS:
    def __init__(self, host, username, password):
        self.host = host
        self.username = username
        self.password = password


    def upload_file(self, local_path, filename, remote_path):
        """
        Upload a file from the client to another client or server
        :param local_path: the path where the upload file is located
        :param filename: The file which should be uploaded
        :param remote_path: The path on the destination client where the file should be saved
        :return: a status if the upload is succesfull or not
        """
        with FTP(host=self.host, user=self.username, passwd=self.password) as ftp:
            ftp.cwd(remote_path)
            with open(local_path + filename, 'rb') as fp:
                # This runs until upload is successful, then breaks
                while True:
                    try:
                        ftp.storbinary("STOR " + filename, fp)
                    except ftplib.error_temp as e:
                        # this catches 421 errors (socket timeout), sleeps 10 seconds and tries again. If any other exception is encountered, breaks.
                        if str(e).split()[0] == '421':
                            time.sleep(10)
                            continue
                        else:
                            raise
                    break
            ftp.close()
            return 'File is transferred'

    def upload_multiple_files(self, local_path, remote_path):
        """
        Upload all files in a directory from the client to another client or server
        :param local_path: the path from where all the files should be uploaded
        :param remote_path: The path on the destination client where the file should be saved
        :return: a status if the upload is succesfull or not
        """
        ftp = FTP(host=self.host, user=self.username, passwd=self.password)
        ftp.cwd(remote_path)
        for filename in os.listdir(local_path):
            file = local_path + filename
            if os.path.isfile(file):
                with open(file, 'rb') as fp:
                    # This runs until upload is successful, then breaks
                    while True:
                        try:
                            ftp.storbinary("STOR " + filename, fp)
                        except ftplib.error_temp as e:
                            # this catches 421 errors (socket timeout), sleeps 10 seconds and tries again. If any other exception is encountered, breaks.
                            if str(e).split()[0] == '421':
                                time.sleep(10)
                                continue
                            else:
                                raise
                        break
        ftp.close()
        return 'All files are transferred'

    def download_file(self, local_path, remote_path, filename, remove_after_download=False):
        """
        Returns a single file from a given remote path
        :param local_path: the folder where the downloaded file should be stored
        :param remote_path: the folder on the server where the file should be downloaded from
        :param filename: the filename itself
        :param remove_after_download: Should the file be removed on the server after the download or not
        :return: a status
        """
        with FTP(host=self.host, user=self.username, passwd=self.password) as ftp:
            with open('{}/{}'.format(local_path, filename), 'wb') as fp:
                res = ftp.retrbinary('RETR {}/{}'.format(remote_path, filename), fp.write)
                if not res.startswith('226 Successfully transferred'):
                    # Remove the created file on the local client if the download is failed
                    if os.path.isfile('{}/{}'.format(local_path, filename)):
                        os.remove('{}/{}'.format(local_path, filename))
                else:
                    if remove_after_download:
                        ftp.delete(filename)

                return res

    def make_dir(self, dir_name):
        """
        Create a directory on a remote machine
        :param dir_name: give the path name which should be created
        :return: the status if the creation is successfull or not
        """
        with FTP(host=self.host, user=self.username, passwd=self.password) as ftp:
            status = ftp.mkd(dir_name)
            return status

    def list_directories(self, remote_path=''):
        """
        Give a NoneType of directories and files in a given directory. This one is only for information. The Nonetype
        can't be iterated or something like that
        :param remote_path: give the folder where to start in
        :return: a NoneType with folders and files
        """
        with FTP(host=self.host, user=self.username, passwd=self.password) as ftp:
            ftp.cwd(remote_path)
            return ftp.dir()

    def make_dirs(self, filepath: str):
        """
        shadows os.makedirs but for ftp
        :param filepath: filepath that you want to create
        :return: nothing
        """
        filepath = filepath.split('/')
        with FTP(host=self.host, user=self.username, passwd=self.password) as ftp:
            ftp.cwd('/')
            for subpath in filepath:
                if subpath != '':
                    file_list = []
                    ftp.retrlines('NLST', file_list.append)
                    if subpath in file_list:
                        ftp.cwd(subpath)
                    else:
                        ftp.mkd(subpath)
                        ftp.cwd(subpath)

    def list_files(self, remote_path=''):
        """
        Give a list with files in a certain folder
        :param remote_path: give the folder where to look in
        :return: a list with files
        """
        with FTP(host=self.host, user=self.username, passwd=self.password) as ftp:
            ftp.cwd(remote_path)
            return ftp.nlst()


class SFTP:
    def __init__(self, host, username, port=22, private_key=None, private_key_pass=None, password=None):
        """
        Init the SFTP class
        :param host: The hostname of the other party. Without the sftp:// part
        :param username: your username
        :param private_key: Optional: the location of the private key
        :param private_key_pass: Optional: the password of the private key
        :param password: Optional: When there is no private key, give a password
        """
        self.host = host
        self.port = port
        self.username = username
        self.private_key = private_key
        self.private_key_pass = private_key_pass
        self.password = password
        self.cnopts = pysftp.CnOpts()
        self.cnopts.hostkeys = None

    def upload_file(self, local_filepath, remote_filepath, confirm=True):
        """
        Upload a single file to a remote location. If there is no Private key
        :param local_filepath: The file and the full path on your local machine
        :param remote_filepath: The path and filename on the remote location
        :return: status
        """
        if self.private_key == None:
            connection = pysftp.Connection(host=self.host, port=self.port, username=self.username, password=self.password, cnopts=self.cnopts)
        else:
            connection = pysftp.Connection(host=self.host, port=self.port, username=self.username, private_key=self.private_key, private_key_pass=self.private_key_pass, cnopts=self.cnopts)
        response = connection.put(local_filepath, remote_filepath, confirm=confirm)
        connection.close()
        return response

    def list_dir(self, remote_filepath):
        """
        Read the files and folders an a certain location
        :param remote_filepath: The full path where you want to get the content from
        :return: a list with files and folders in the given location
        """
        if self.private_key == None:
            connection = pysftp.Connection(host=self.host, port=self.port, username=self.username, password=self.password, cnopts=self.cnopts)
        else:
            connection = pysftp.Connection(host=self.host, port=self.port, username=self.username, private_key=self.private_key, private_key_pass=self.private_key_pass, cnopts=self.cnopts)
        with connection.cd(remote_filepath):
            list_files = connection.listdir()
        connection.close()
        return list_files

    def download_file(self, remote_path, remote_file, local_path):
        """
        Download a single file
        :param remote_path: the path where the remote file exists
        :param remote_file: the remote file itself
        :return: a file object
        """
        if self.private_key == None:
            connection = pysftp.Connection(host=self.host, port=self.port, username=self.username, password=self.password, cnopts=self.cnopts)
        else:
            connection = pysftp.Connection(host=self.host, port=self.port, username=self.username, private_key=self.private_key, private_key_pass=self.private_key_pass, cnopts=self.cnopts)
        file = connection.get(remotepath=f'{remote_path}{remote_file}', localpath=f'{local_path}/{remote_file}')
        connection.close()
        return file

    def make_dir(self, remote_path, new_dir_name):
        """
        Create a new folder on a remote location
        :param remote_path: The location where you want to create the new folder
        :param new_dir_name: The name of the new folder
        :return: a status if creating succeeded or not
        """
        if self.private_key == None:
            connection = pysftp.Connection(host=self.host, port=self.port, username=self.username, password=self.password, cnopts=self.cnopts)
        else:
            connection = pysftp.Connection(host=self.host, port=self.port, username=self.username, private_key=self.private_key, private_key_pass=self.private_key_pass, cnopts=self.cnopts)
        with connection.cd(remote_path):
            response = connection.mkdir(new_dir_name)
        connection.close()
        return response

    def remove_file(self, remote_file):
        """
        Remove a file on a remote location
        :param remote_file: the full path of the file that needs to be removed
        :return: a status if deleting succeeded or not
        """
        if self.private_key == None:
            connection = pysftp.Connection(host=self.host, port=self.port, username=self.username, password=self.password, cnopts=self.cnopts)
        else:
            connection = pysftp.Connection(host=self.host, port=self.port, username=self.username, private_key=self.private_key, private_key_pass=self.private_key_pass, cnopts=self.cnopts)
        response = connection.remove(remotefile=remote_file)
        connection.close()
        return response

