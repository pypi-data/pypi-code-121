import os
import re
import time
import ftplib
import socket
import subprocess

from pypers.utils import ftpw
from pypers.steps.base.fetch_step import FetchStep


class FTP(FetchStep):
    spec = {
        "version": "2.0",
        "descr": [
            "Fetch archives from either a local dir or FTP server"
        ],
        "args":
        {
            "params": [
                {
                    "name": "ftp_dir",
                    "type": "str",
                    "descr": "directory to look into. overrides the "
                             "pipeline input ftp_dir",
                    "value": ""
                },
                {
                    "name": "use_wget",
                    "type": "int",
                    "descr": "force use of wget to retreive file",
                    "value": 0
                },
                {
                    "name": "sleep_secs",
                    "type": "int",
                    "descr": "secs to sleep to check if FTP dir is hot",
                    "value": 5
                }
            ]
        }
    }

    from_type = 'from_ftp'

    def should_download(self, local_filename, remote_filename, ftp_obj):
        if local_filename in self.done_archives:
            return False
        return True

    def add_output(self, local_filename, remote_filename, ftp_obj):
        self.output_files.append(local_filename)

    def specific_process(self):

        # getting files from ftp serverfiles_path
        ftp_params = self.fetch_from['from_ftp']
        self.output_files = []
        self.logger.info('getting %s files from ftp %s' % (
            'all' if self.limit == 0 else self.limit, ftp_params.get('ftp_server', '')))
        if ftp_params.get('ftp_passwd', None):
            self.logger.info('Connecting to %s:%s%s@%s/%s' % (
                ftp_params['ftp_user'],
                re.sub(r'.', '*', ftp_params['ftp_passwd'][:-4]),
                ftp_params['ftp_passwd'][-4:],
                ftp_params['ftp_server'],
                self.ftp_dir or ftp_params['ftp_dir']
            ))
        else:
            self.logger.info('Connecting to %s/%s' % (
                ftp_params['ftp_server'],
                self.ftp_dir or ftp_params['ftp_dir']
            ))

        ftp = ftplib.FTP(ftp_params['ftp_server'])
        ftp.login(ftp_params.get('ftp_user', ''), ftp_params.get('ftp_passwd', ''))
        ftp.cwd('/')

        # optimize socket params for download task
        # this is for the connected not to be dropped by the remote server
        # due in inactivity (noop every 1sec)

        ftp.sock.setsockopt(socket.SOL_SOCKET,  socket.SO_KEEPALIVE,   1)
        try:
            ftp.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE,  60)
        except Exception as e:
            # On mac os TCP_KEEPIDLE dose not exists.
            pass
        ftp.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 75)

        list_1 = []
        ftp.retrlines('LIST', list_1.append)
        time.sleep(self.sleep_secs)
        list_2 = []
        ftp.retrlines('LIST', list_2.append)

        if not list_1 == list_2:
            ftp.quit()
            raise Exception('FTP folder is HOT. Exit.')

        self.logger.info('FTP folder is cold. Moving on ...')

        ftp_dir = self.ftp_dir or ftp_params['ftp_dir']
        ftpwalk = ftpw.FTPWalk(ftp)

        # looks for files recursively
        flist = []
        r = re.compile(self.file_regex, re.IGNORECASE)
        for path, files in ftpwalk.walk(path=ftp_dir):
            for f in files:
                if r.match(f):
                    flist.append(os.path.join(path, f))
        count = 0
        if self.use_wget:
            ftp.quit()  # done with ftp lib here
        else:
            ftp.set_debuglevel(2)
            ftp.voidcmd('TYPE I')
            ftp.set_pasv(True)
            ftp.cwd('/')

        for f in sorted(flist):
            filename = os.path.basename(f)  # 123.zip
            filepath = os.path.relpath(f, ftp_dir)  # dir/123.zip

            if self.limit and count == self.limit:
                break
            if not self.should_download(filepath, f, ftp):
                continue

            count += 1
            self.logger.info('[ftp] %s: %s' % (count, f))
            print('[ftp] %s: %s' % (count, f))

            dest_dir = os.path.join(self.output_dir, os.path.dirname(filepath))
            dest_file = os.path.join(dest_dir, filename)

            try:
                os.makedirs(dest_dir)
            except Exception as e:
                pass

            if self.use_wget:
                cmd = 'wget -q --no-passive-ftp --ftp-user=%s ' \
                      '--ftp-password=%s ftp://%s%s -O %s' % (
                        ftp_params['ftp_user'],
                        ftp_params['ftp_passwd'],
                        ftp_params['ftp_server'],
                        os.path.join(ftp_dir, f),
                        dest_file)
                self.logger.info('\nusing wget to retreive file')
                self.logger.info('------------------------------')
                self.logger.info('\n  '.join(cmd.split(' ')))
                self.logger.info('------------------------------')
                subprocess.check_call(cmd.split(' '))
            else:
                res = ftp.retrbinary('RETR %s' % f, open(dest_file, 'wb').write)
                self.logger.info(res)
                if not res.startswith('226'):  # 226 = success
                    os.remove(dest_file)
                    raise Exception('FTP failed to transfer successfully')
            self.add_output(dest_file, f, ftp)
        if not self.use_wget:
            ftp.quit()


