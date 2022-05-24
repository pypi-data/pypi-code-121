import json
import os
import boto3
import shutil
import math
from copy import deepcopy
from pypers.cli import StageBase
from pypers.core.interfaces.config.pypers_storage import IDX_BUCKET
from pypers.core.interfaces.storage import get_storage


class StageIDX(StageBase):
    nb_records_per_subdir = 1000

    def stage(self):
        download_folder = os.path.join('./', 'download')
        os.makedirs(download_folder, exist_ok=True)
        with open(self.snapshot, 'r') as f:
            snapshot_data = json.loads(f.read())
        nb_records_total = len(snapshot_data)
        nb_subdir_total = math.ceil(nb_records_total / self.nb_records_per_subdir)
        pd_subdir = max(len(str(nb_subdir_total)), 3)
        records_count = 0
        for item in snapshot_data:
            # Data mapping
            st13 = item['st13']
            pipeline_type = item['gbd_type']
            collection = item['gbd_collection']
            latest_run_id = item['latest_run_id']
            # Folder structure
            stage_root = os.path.join(os.environ.get('GBDFILES_DIR'),
                                      self.run_id,
                                      pipeline_type,
                                      collection,
                                      )
            subdir = math.floor(records_count / self.nb_records_per_subdir)
            stage_subdir = str(subdir).zfill(pd_subdir)
            stage_path = os.path.join(stage_root, stage_subdir, st13)
            os.makedirs(stage_path, exist_ok=True)
            # Data retrival
            idx_name = "idx.json"
            # IDX documents
            if not os.path.exists(os.path.join(stage_path, idx_name)):
                doc_src_path = os.path.join(IDX_BUCKET, pipeline_type, collection, st13, idx_name)
                download_path = os.path.join(download_folder, idx_name)
                self.storage.get_file(doc_src_path, download_path)
                self._move_object(stage_path, download_folder, idx_name)
            # Latests dynamodb record
            dydb_live_doc = deepcopy(item)
            dydb_live_doc.pop('ori_logo')
            dydb_live_doc.pop('ori_document')
            dydb_live_doc['latest_run_id'] = self.run_id

            with open(os.path.join(stage_path, 'latest.json'), 'w') as f:
                f.write(json.dumps(dydb_live_doc))
            records_count += 1
        shutil.rmtree(download_folder)


class StageIDXFromBucket:
    nb_records_per_subdir = 1000

    def __init__(self, type, collection, run_id):
        self.collection = collection
        self.p_type = type
        self.run_id = run_id
        self.prefix = "%s/%s/" % (self.p_type, self.collection)
        self.s3_client = boto3.resource('s3')
        self.storage = get_storage()


    def stage(self):
        download_folder = os.path.join('./', 'download')
        os.makedirs(download_folder, exist_ok=True)

        bucket = self.s3_client.Bucket(IDX_BUCKET)
        pd_subdir = 10
        records_count = 0
        for file_on_s3 in bucket.objects.filter(Prefix=self.prefix):
            st13 = file_on_s3.key.split('/')[-2]
            pipeline_type = self.p_type
            collection = self.collection
            # Folder structure
            stage_root = os.path.join(os.environ.get('GBDFILES_DIR'),
                                      self.run_id,
                                      pipeline_type,
                                      collection,
                                      )
            subdir = math.floor(records_count / self.nb_records_per_subdir)
            stage_subdir = str(subdir).zfill(pd_subdir)
            stage_path = os.path.join(stage_root, stage_subdir, st13)
            os.makedirs(stage_path, exist_ok=True)
            # Data retrival
            idx_name = "idx.json"
            # IDX documents
            if not os.path.exists(os.path.join(stage_path, idx_name)):
                doc_src_path = os.path.join(IDX_BUCKET, pipeline_type, collection, st13, idx_name)
                download_path = os.path.join(download_folder, idx_name)
                self.storage.get_file(doc_src_path, download_path)
                self._move_object(stage_path, download_folder, idx_name)
            records_count += 1

    def _move_object(self, write_root, read_root, file):
        if not file:
            return

        src_file = os.path.join(read_root, file)
        dest_file = os.path.join(write_root, file)

        dest_dir = os.path.dirname(dest_file)
        os.makedirs(dest_dir, exist_ok=True)

        shutil.move(src_file, dest_file)