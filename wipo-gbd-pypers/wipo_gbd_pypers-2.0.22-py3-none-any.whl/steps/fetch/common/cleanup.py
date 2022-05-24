import os
import getpass
import shutil
import ftplib
import paramiko

from pypers.core.interfaces import db
from pypers.core.interfaces import msgbus
from pypers.core.interfaces.storage.backup import Backup
from pypers.utils.utils import delete_files, clean_folder
from pypers.steps.base.step_generic import EmptyStep


class Cleanup(EmptyStep):

    spec = {
        "version": "2.0",
        "descr": [
            "Perform cleanup after execution of pipeline"
        ],
        "args":
        {
            "inputs": [
                {
                    "name": "processed_list",
                    "descr": "list of archives that have been processed"
                },
                {
                    "name": "manifest_list",
                    "descr": "path to the manifest",
                }
            ],
            "params": [
                {
                    "name": "reset_done",
                    "type": "int",
                    "descr": "an int flag (0|1) whether to reset "
                             "done file (used when we do complete download)",
                    "value": 0
                },
                {
                    "name": "remove_orig",
                    "type": "int",
                    "descr": "an int flag (0|1) whether to "
                             "remove original files",
                    "value": 0
                },
                {
                    "name": "backup_archives",
                    "type": "int",
                    "descr": "an int flag (0|1) whether to backup downloaded archives",
                    "value": 1
                },
                {
                    "name": "chain",
                    "type": "int",
                    "descr": "an int flag (0|1) whether to "
                             "chain to the next pipeline",
                    "value": 0
                },

            ]
        }
    }

    def _get_common_path(self, path1, path2):
        path1_set = set([path1])
        path2_set = set([path2])
        while path1 != '/' and '/' in path1:
            path1 = os.path.dirname(path1)
            path1_set.add(path1)
        while path2 != '/' and '/' in path2:
            path2 = os.path.dirname(path2)
            path2_set.add(path2)
        common = path1_set.intersection(path2_set)
        if len(common):
            return sorted(list(common))[-1]
        return ""

    def process(self):
        if not len(self.processed_list):
            return

        run_id = self.meta['pipeline']['run_id']

        pipeline_input = self.meta['pipeline']['input']

        ftp_params = pipeline_input.get('from_ftp', None)
        sftp_params = pipeline_input.get('from_sftp', None)

        # this is necessary for cases like ILTM/KRTM
        # where fetch uses sub-directories:
        #   180220181/Images/B1802181.zip
        #   180220181/Xml/B1802181.zip

        # Done file in db
        # ===============================
        should_reset = self.reset_done != 0
        payload = []
        # fetch from remote
        processed_paths = [
            p.split('/')[-1]
            for p in self.processed_list]
        # add what is processed to the done file
        for processed_name in sorted(processed_paths):
            payload.append('%s\t%s' % (run_id, processed_name))

        db.get_done_file_manager().update_done(self.collection, self.run_id,
                                               processed_paths,
                                               should_reset=should_reset)

        # backup and delete processed files
        # ================================
        if self.backup_archives:
            backup = Backup(self.pipeline_type, self.collection)
            for archive in self.processed_list:
                backup.store_archive(archive, hard=True)


        # clean files from ftp location
        # =============================
        if self.remove_orig and ftp_params:
            self.logger.info('\n remove archives from ftp dir')

            ftp = ftplib.FTP(ftp_params['ftp_server'])
            ftp.login(ftp_params['ftp_user'], ftp_params['ftp_passwd'])

            for f in self.processed_list:
                ftp.cwd(ftp_params['ftp_dir'])
                fname = os.path.basename(f)
                fpath = os.path.dirname(f)
                self.logger.info('deleting %s from ftp dir %s' % (
                    f, ftp_params['ftp_dir']))
                ftp.cwd(fpath)
                ftp.delete(fname)

            ftp.quit()

        # clean files from sftp location
        # ==============================
        if self.remove_orig and sftp_params:
            ssh = paramiko.SSHClient()
            ssh.load_system_host_keys()
            ssh.connect(sftp_params['sftp_server'], username=getpass.getuser())

            sftp = ssh.open_sftp()

            for f in self.processed_list:
                sftp.chdir(sftp_params['sftp_dir'])
                fname = os.path.basename(f)
                fpath = os.path.dirname(f)
                self.logger.info('deleting %s from sftp dir %s' % (
                    f, sftp_params['sftp_dir']))
                sftp.chdir(fpath)
                sftp.remove(fname)

            ssh.close()
            sftp.close()


    def postprocess(self):
        output_dir = os.path.join(os.environ['WORK_DIR'],
                                  self.run_id,
                                  self.pipeline_type,
                                  self.collection)

        if int(self.chain):
            force_restart = self.meta['pipeline'].get('force_restart', 'False')
            msgbus.get_msg_bus().send_message(self.run_id,
                                              type=self.pipeline_type,
                                              collection="harmonize_%s" % self.collection,
                                              custom_config=['pipeline.output_dir=%s' % output_dir,
                                                             'pipeline.forced_restarted=%s' % force_restart,
                                                             'pipeline.is_operation=%s' % self.is_operation,
                                                             'steps.merge.chain=1'])

        pipeline_dir = self.meta['pipeline']['output_dir']
        delete_files(pipeline_dir, patterns=['.*_output.json', '.*_input.json'])
        clean_folder(pipeline_dir)
