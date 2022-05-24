import os
import json
import shutil

from . import get_storage

from pypers.core.interfaces.config.pypers_storage import ARCHIVES_BUCKET, RAW_DOCUMENTS, \
    RAW_IMAGES_BUCKET, GBD_DOCUMENTS, IMAGES_BUCKET, IDX_BUCKET


"""
Back up utility for gbd-assets
"""
class Backup:
    def __init__(self, pipeline_type, collection):
        self.pipeline_type = pipeline_type
        self.collection = collection

        self.storage = get_storage()


    # hard => store and delete
    def _do_store(self, file, bucket_name, bucket_path, hard):
        if not os.path.exists(file):
            return False

        _, file_name = os.path.split(file)

        # set the location for storage
        bucket_file = os.path.join(bucket_path, file_name)

        self.storage.do_store(file, bucket_name, bucket_file)

        if hard:
            try:
                os.remove(file)
            except:
                pass
        return True

    # ori data files go into STORAGE_DOCS_GBD/type/collection/archive/st13.ext
    def store_doc_ori(self, ori_file, archive_name, hard=False):
        bucket_name = RAW_DOCUMENTS
        bucket_path = os.path.join(self.pipeline_type,
                                   self.collection,
                                   archive_name)

        return self._do_store(ori_file, bucket_name, bucket_path, hard)

    # ori img files go into STORAGE_IMGS_ORI/type/collection/st13/crc.ext
    def store_img_ori(self, ori_file, st13, hard=False):
        bucket_name = RAW_IMAGES_BUCKET
        bucket_path = os.path.join(self.pipeline_type,
                                   self.collection,
                                   st13)

        return self._do_store(ori_file, bucket_name, bucket_path, hard)

    # gbd data files go into STORAGE_DATA_GBD/type/collection/st13/run_id.json
    def store_doc_gbd(self, gbd_file, st13, hard=False):
        bucket_name = GBD_DOCUMENTS
        bucket_path = os.path.join(self.pipeline_type,
                                   self.collection,
                                   st13)

        return self._do_store(gbd_file, bucket_name, bucket_path, hard)

    # gbd img files go into STORAGE_IMGS_GBD/type/collection/st13/run_id.json
    def store_img_gbd(self, img_file, st13, hard=False):
        bucket_name = IMAGES_BUCKET
        bucket_path = os.path.join(self.pipeline_type,
                                   self.collection,
                                   st13)

        return self._do_store(img_file, bucket_name, bucket_path, hard)

    # ori img files go into STORAGE_IMGS_ORI/type/collection/archive.zip
    def store_archive(self, archive, hard=False):
        bucket_name = ARCHIVES_BUCKET
        bucket_path = os.path.join(self.pipeline_type,
                                   self.collection)

        return self._do_store(archive, bucket_name, bucket_path, hard)


    # idx files go into STORAGE_DATA_IDX/type/collection/st13/idx.json
    def store_doc_idx(self, idx_file, st13, hard=False):
        bucket_name = IDX_BUCKET
        bucket_path = os.path.join(self.pipeline_type,
                                   self.collection,
                                   st13)
        return self._do_store(idx_file, bucket_name, bucket_path, hard)

