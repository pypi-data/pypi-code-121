from pypers.steps.fetch.download.ftp import FTP
import os
import shutil


class FTPIrd(FTP):

    def should_download(self, local_filename, remote_filename, ftp_obj):
        size = ftp_obj.size(remote_filename)
        for archive in self.done_archives:
            if str(size) in archive:
                return False
        return True

    def add_output(self, local_filename, remote_filename, ftp_obj):
        size = ftp_obj.size(remote_filename)
        filename_remote = os.path.basename(remote_filename)
        files = ftp_obj.mlsd(os.path.dirname(remote_filename))
        year = None
        month = None
        day = None
        for file in files:
            if file[0] == filename_remote:
                timestamp = file[1]['modify']
                if timestamp:
                    year = timestamp[0:4]
                    month = timestamp[4:6]
                    day = timestamp[6:8]
        filename = "%s_%s-%s-%s" % (size, year, month, day)
        new_local = "%s.zip" % filename
        shutil.move(local_filename, os.path.join(self.output_dir, new_local))
        self.output_files.append(os.path.join(self.output_dir, new_local))