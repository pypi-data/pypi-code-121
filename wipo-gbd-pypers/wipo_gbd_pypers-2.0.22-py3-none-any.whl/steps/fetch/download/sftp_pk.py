import os
import time
import paramiko
import stat
from pypers.steps.base.fetch_step import FetchStep


class SFTP_PK(FetchStep):
    spec = {
        "version": "2.0",
        "descr": [
            "Fetch archives from either a local dir or SFTP server"
        ],
        "args":
        {
            "params": [
                {
                    "name": "sleep_secs",
                    "type": "int",
                    "descr": "secs to sleep to check if SSH dir is hot",
                    "value": 5
                }
            ],
        }
    }

    from_type = 'from_sftp'

    def connect(self):
        # getting files from sftp
        self.sftp_params = self.fetch_from['from_sftp']
        self.logger.info('getting %s files from sftp %s %s' % (
            'all' if self.limit == 0 else self.limit,
            self.sftp_params['sftp_server'],
            self.sftp_params['sftp_dir']))
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(self.sftp_params['sftp_server'],
                         username=self.sftp_params['sftp_user'],
                         key_filename=self.sftp_params['sftp_pkey'],
                         passphrase=self.sftp_params['sftp_phrase'])
        return self.ssh.open_sftp()

    def sftp_walk(self, sftp, remotepath):
        path = remotepath
        files = []
        folders = []
        for f in sftp.listdir_attr(remotepath):
            if stat.S_ISDIR(f.st_mode):
                folders.append(f.filename)
            else:
                files.append(f.filename)
        if files:
            yield path, files
        for folder in folders:
            new_path = os.path.join(remotepath, folder)
            for x in self.sftp_walk(sftp, new_path):
                yield x

    def specific_process(self):
        self.output_files = []
        sftp = self.connect()

        sftp_dir = self.sftp_params['sftp_dir']
        self.logger.info('going to dir %s' % sftp_dir)
        sftp.chdir(sftp_dir)

        flist = []
        # looks for files recursively
        for path, files in self.sftp_walk(sftp, sftp_dir):
            for f in files:
                if self.rgx.match(f):
                    flist.append(os.path.join(path, f))

        # look for directories where files are present
        upload_dirs = [os.path.dirname(os.path.relpath(f, sftp_dir))
                       for f in flist]
        # check if uploading is still active on every upload dir
        for upload_dir in set(upload_dirs):
            size_1 = sftp.stat(upload_dir).st_mtime
            time.sleep(self.sleep_secs)
            size_2 = sftp.stat(upload_dir).st_mtime

            if size_1 != size_2:
                sftp.close()
                self.ssh.close()
                raise Exception(
                    'SSH folder [%s] is HOT. Exit.' % os.path.join(sftp_dir,
                                                                   upload_dir))

            self.logger.info('SSH folder [%s] is cold' % os.path.join(
                sftp_dir, upload_dir))

        self.logger.info('get the files')

        count = 0
        for f in sorted(flist, reverse=True):
            filename = os.path.basename(f)  # 123.zip
            filepath = os.path.relpath(f, sftp_dir)  # dir/123.zip

            if self.limit and count == self.limit:
                break
            if filepath in self.done_archives:
                continue

            count += 1
            self.logger.info('[sftp] %s: %s' % (count, f))

            dest_dir = os.path.join(self.output_dir, os.path.dirname(filepath))
            dest_file = os.path.join(dest_dir, filename)

            try:
                os.makedirs(dest_dir)
            except Exception as e:
                pass

            sftp.get(f, dest_file)
            self.output_files.append(dest_file)

        sftp.close()
        self.ssh.close()
