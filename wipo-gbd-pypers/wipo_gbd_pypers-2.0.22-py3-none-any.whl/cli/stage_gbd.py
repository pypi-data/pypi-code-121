import json
import os
import shutil
import math
from copy import deepcopy
from pypers.cli import StageBase, STAGE
from pypers.core.interfaces.config.pypers_storage import IMAGES_BUCKET, GBD_DOCUMENTS


class StageGBD(StageBase):
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
            if self.stage_type != STAGE.Documents:
                # Images
                for crc in item.get('logo', []):
                    img = '%s-hi.png' % crc
                    if not os.path.exists(os.path.join(stage_path, img)):
                        img_src_path = os.path.join(IMAGES_BUCKET, pipeline_type, collection, st13, img)
                        download_path = os.path.join(download_folder, img)
                        self.storage.get_file(img_src_path, download_path)
                        self._move_object(stage_path, download_folder, img)
            gbd_doc = "%s.json" % latest_run_id
            new_gbd_doc_run_id = "%s.json" % self.run_id
            # Gbd documents
            if not os.path.exists(os.path.join(stage_path, new_gbd_doc_run_id)):
                doc_src_path = os.path.join(GBD_DOCUMENTS, pipeline_type, collection, st13, gbd_doc)
                download_path = os.path.join(download_folder, new_gbd_doc_run_id)
                self.storage.get_file(doc_src_path, download_path)
                self._move_object(stage_path, download_folder, new_gbd_doc_run_id)
            # Latests dynamodb record
            dydb_live_doc = deepcopy(item)
            dydb_live_doc.pop('ori_logo')
            dydb_live_doc.pop('ori_document')
            dydb_live_doc['latest_run_id'] = self.run_id

            with open(os.path.join(stage_path, 'latest.json'), 'w') as f:
                f.write(json.dumps(dydb_live_doc))
            records_count += 1
        shutil.rmtree(download_folder)
