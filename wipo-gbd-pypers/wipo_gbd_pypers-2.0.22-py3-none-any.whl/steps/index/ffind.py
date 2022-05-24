import os
import glob
import json

from pypers.steps.base.step_generic import EmptyStep

class FFind(EmptyStep):
    spec = {
        "version": "2.0",
        "descr": [
            "Returns the directory with the extraction"
        ],
        "args":
        {
            'outputs': [
                {
                    'name': 'files',
                    'descr': 'output data index'
                }
            ],
            "params": [
                {
                    "name": "fdepth",
                    "type": "int",
                    "descr": "the number of subfolders to look into",
                    "value": 1
                }
            ]
        }
    }

    def find_files(self, stage_path, stage_root):

        # doc_path stage_path/st13/
        for st13 in os.listdir(stage_path):

            doc_path = os.path.join(stage_path, st13)
            idx_file = os.path.join(doc_path, 'idx.json')
            latest_file = os.path.join(doc_path, 'latest.json')

            # we need to have latest and idx files to consider
            if not os.path.exists(idx_file):
                continue
            if not os.path.exists(latest_file) and self.release == 1:
                continue
            self.files[st13] = {'idx': os.path.relpath(idx_file, stage_root)}
            if os.path.exists(latest_file):
                self.files[st13]['latest'] = os.path.relpath(latest_file, stage_root)

    def process(self):
        self.files = {}

        self.collection_name = self.collection.replace('index_', '')

        # stage_root  GBDFILES_DIR/run_id/type/collection/
        # idx_file    stage_root/000/st13/idx.json
        # latest_file stage_root/000/st13/lastest.json

        stage_root = os.path.join(os.environ.get('GBDFILES_DIR'),
                                  self.run_id,
                                  self.pipeline_type,
                                  self.collection_name)

        # stage_path stage_root/000/, stage_root/001/ ...
        for sub_dir in os.listdir(stage_root):
            stage_path = os.path.join(stage_root, sub_dir)
            if self.fdepth > 1:
                for sub_level in os.listdir(stage_path):
                    self.find_files(os.path.join(stage_path, sub_level), stage_root)
            else:
                self.find_files(stage_path, stage_root)

    def postprocess(self):
        self.files = [self.files]
