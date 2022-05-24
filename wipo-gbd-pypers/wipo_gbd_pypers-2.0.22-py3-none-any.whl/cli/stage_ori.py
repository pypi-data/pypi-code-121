import json
import os
import shutil
from pypers.cli import STAGE, StageBase
from pypers.core.interfaces.config.pypers_storage import RAW_DOCUMENTS, RAW_IMAGES_BUCKET


class StageOri(StageBase):

    def stage(self):
        download_folder = os.path.join('./', 'download')
        os.makedirs(download_folder, exist_ok=True)
        with open(self.snapshot, 'r') as f:
            snapshot_data = json.loads(f.read())
        for item in snapshot_data:
            # Data mapping
            st13 = item['st13']
            gbd_extraction_date = item['gbd_extraction_date']
            pipeline_type = item['gbd_type']
            collection = item['gbd_collection']
            archive_date = item['office_extraction_date']
            archive_name = item['archive']
            manifest = self.get_manifest_per_archive(archive_date,
                                                      archive_name,
                                                      gbd_extraction_date)
            # Folder structure
            ori_path = os.path.join(os.environ.get('ORIFILES_DIR'),
                                    # mandatory ENV VARIABLE - we do not want to make defaults
                                    self.run_id,
                                    pipeline_type,
                                    collection,
                                    archive_date,
                                    archive_name,
                                    st13)
            os.makedirs(ori_path, exist_ok=True)
            # Data retrival
            if self.stage_type in [STAGE.All, STAGE.Images]:
                for img in item.get('ori_logo'):
                    if not os.path.exists(os.path.join(ori_path, img)):
                        # Need to rename the "ori" image as it is already coverted to the high name, thus
                        # resize will overrite the original.
                        new_img_name = "ori_%s" % img
                        img_src_path = os.path.join(RAW_IMAGES_BUCKET, pipeline_type, collection, st13, img)
                        download_path = os.path.join(download_folder, new_img_name)
                        self.storage.get_file(img_src_path, download_path)
                        self._move_object(ori_path, download_folder, new_img_name)
                    if st13 not in manifest['img_files'].keys():
                        manifest['img_files'][st13] = []
                    manifest['img_files'][st13].append({
                        'ori': os.path.join(st13, new_img_name)
                    })
            if self.stage_type in [STAGE.All, STAGE.Documents]:
                doc = item.get('ori_document')
                if not os.path.exists(os.path.join(ori_path, doc)):
                    doc_src_path = os.path.join(RAW_DOCUMENTS, pipeline_type, collection, archive_name, doc)
                    download_path = os.path.join(download_folder, doc)
                    self.storage.get_file(doc_src_path, download_path)
                    self._move_object(ori_path, download_folder, doc)
                manifest['data_files'][st13] = {
                    'ori': os.path.join(st13, doc)
                }
        # Build manifest in each archive
        for archive_date in self.manifests.keys():
            for archive_name in self.manifests[archive_date].keys():
                ori_path = os.path.join(os.environ.get('ORIFILES_DIR'),
                                        # mandatory ENV VARIABLE - we do not want to make defaults
                                        self.run_id,
                                        pipeline_type,
                                        collection,
                                        archive_date,
                                        archive_name)
                os.makedirs(ori_path, exist_ok=True)
                manifest_payload = self.manifests[archive_date][archive_name]
                with open(os.path.join(ori_path, 'manifest.json'), 'w') as f:
                    f.write(json.dumps(manifest_payload))
        shutil.rmtree(download_folder)

    def get_manifest_per_archive(self, archive_date, archive_name, gbd_extraction_date):
        if archive_date not in self.manifests.keys():
            self.manifests[archive_date] = {}
        manifest = self.manifests[archive_date]
        if archive_name not in manifest.keys():
            manifest[archive_name] = {
                'gbd_extraction_date': gbd_extraction_date,
                'data_files': {},
                'img_files': {}
            }
        manifest = manifest[archive_name]
        return manifest

