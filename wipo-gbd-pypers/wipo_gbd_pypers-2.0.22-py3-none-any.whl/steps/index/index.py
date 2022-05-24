import os
import subprocess

from pypers.core.interfaces import db
from pypers.core.interfaces.storage.backup import Backup
from pypers.utils.utils import clean_folder, delete_files
from pypers.steps.base.step_generic import EmptyStep


class Index(EmptyStep):
    """
    Index / Backup / DyDb publish
    """
    spec = {
        "version": "2.0",
        "descr": [
            "Returns the directory with the extraction"
        ],
        "args":
        {
            'inputs': [
                {
                    'name': 'files',
                    'descr': 'files to be indexed',
                    'iterable': True
                }
            ],
            'outputs': [
                {
                    'name': 'flag',
                    'descr': 'flag for done'
                }
            ]
        }
    }

    # "files" : {
    #     "st13" : {
    #         "idx" : "000/st13/idx.json",
    #         "latest" : "000/st13/latest.json"
    #     },
    #     ...
    # }
    def process(self):
        if not len(self.files.keys()):
            return

        self.collection_name = self.collection.replace('index_', '')

        # stage_root  GBDFILES_DIR/run_id/type/collection/
        stage_root = os.path.join(os.environ.get('GBDFILES_DIR'),
                                  self.run_id,
                                  self.pipeline_type,
                                  self.collection_name)

        # rewrite paths to absolute paths
        st13s = []
        for st13, record in self.files.items():
            if record.get('latest', None):
                record['latest'] = os.path.join(stage_root, record['latest'])
            record['idx'] = os.path.join(stage_root, record['idx'])
            st13s.append(st13)

        # index the files
        failed_log = os.path.join(self.output_dir, 'failed.index')
        jar_file = os.environ.get('INDEXER_JAR').strip()

        # write fofn file
        fofn_file = os.path.join(self.output_dir, 'findex.fofn')

        with open(fofn_file, 'w') as f:
            f.write('\n'.join([record['idx'] for _, record in self.files.items()]))
        cmd = 'java -jar %s --fofn %s --logFile %s --collection %s --type %s --extension .json'
        cmd = cmd % (jar_file,
                     fofn_file,
                     failed_log,
                     self.collection_name,
                     self.pipeline_type)

        proc = subprocess.Popen(cmd.split(' '),
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                close_fds=True)
        stdout, stderr = proc.communicate()

        rc = proc.returncode
        if rc != 0:
            self.logger.error(str(stderr))
            db.get_db_error().send_error(self.run_id,
                                         self.collection_name,
                                         {'source': 'image_analysis'},
                                         str(stderr))
            return


        with open(failed_log, 'r') as f:
            for line in f.readlines():
                st13 = os.path.basename(os.path.dirname(line))
                self.logger.info("Failed indexing on %s" % st13)
                st13s.remove(st13)

        if self.release != 1:
            self._del_files(st13s)
        else:
            # backup what has been indexed of idx files
            self._backup_files(st13s)

            # publish what has been indexed of latest files
            self._dydb_files(st13s, stage_root)

        clean_folder(stage_root)



    def postprocess(self):
        failed_log = os.path.join(self.output_dir, 'failed.index')
        if os.path.exists(failed_log):
            os.remove(failed_log)
        self.flag = [1]

    # -------------
    # FILES BACKUP
    # -------------
    def _backup_files(self, st13s):
        backup = Backup(self.pipeline_type, self.collection_name)

        for st13 in st13s:
            idx_file = self.files[st13]['idx']
            backup.store_doc_idx(idx_file, st13, hard=True)

    # -------------
    # DYDB PUBLISH
    # -------------
    def _dydb_files(self, st13s, stage_root):
        items_for_dynamo = [self.files[key]['latest'] for key in st13s]
        db.get_pre_prod_db().put_items(items_for_dynamo)
        delete_files(stage_root, patterns=['latest.json'])

    def _del_files(self, st13s):
        for st13 in st13s:
            idx_file = self.files[st13]['idx']
            os.remove(idx_file)