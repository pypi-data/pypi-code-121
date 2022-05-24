import os

from . import merge_data_img_files

from pypers.core.interfaces.storage.backup import Backup
from pypers.core.interfaces.db.cache import CachedCopy

from pypers.steps.base.step_generic import EmptyStep


class Organize(EmptyStep):
    """
    Organize files into subdirectories.
    Rename files and logos to appnum
    """
    spec = {
        "version": "2.0",
        "descr": [
            "Returns the directory with the extraction"
        ],
        "args":
        {
            "inputs": [
                {
                    "name": "data_files",
                    "descr": "the data files to organize",
                    "iterable": True
                },
                {
                    "name": "img_files",
                    "descr": "the img files to organize",
                    "iterable": True
                },
                {
                    "name": "extraction_dir",
                    "descr": "the extraction dir",
                    "iterable": True
                },
                {
                    "name": "gbd_extraction_date",
                    "descr": "the extraction date",
                    "iterable": True
                }
            ],
            "outputs": [
                {
                    "name": "data_files",
                    "descr": "the extracted data organized by appnum"
                },
                {
                    "name": "img_files",
                    "descr": "the extracted data organized by appnum"
                }
            ],
            "params": [
                {
                    "name": "disabled_backup",
                    "type": "str",
                    "descr": "List of collections for which the ori backup file is disabled",
                    "value": "cutm, woptm, kgtm, kztm, whoinn, woao, wo6ter"
                }
            ]
        }
    }

    # self.data_files { appnum : { "gbd": _, "ori": _, "qc" : [], "st13": _}, appnum ... }
    # self.img_files  { appnum : [{ "crc": _, "high": _, "icon" : _, "ori": _, "thum": _ }, ...], appnum ... }
    # self.extraction_dir ORIFILES_DIR/type/collection/office_extraction_date/archive_name
    def process(self):
        # nothing has been extracted
        if not len(self.data_files.keys()):
            return

        self.office_extraction_date, self.archive_name = self.extraction_dir.split(os.sep)[-2:]

        self.collection_name = self.collection.replace('harmonize_', '')

        self.backup = Backup(self.pipeline_type, self.collection_name)

        appnum_files = merge_data_img_files(self.data_files, self.img_files)

        # [{ "appnum": _,
        #    "data": { "gbd": _, "ori": _, "qc" : [], "st13": _},
        #    "img": [{ "crc": _, "high": _, "icon" : [], "ori": _, "thum": ...} ...]}
        #  { ... }]
        appnum_files_flat = [data for _, data in appnum_files.items()]

        cached_keys = []
        for entry in self.worker_parallel(appnum_files_flat, self._process_record):
            if entry:
                cached_keys.append(entry)
        dydb_docs_copies_tbl = CachedCopy(self.output_dir, None)
        dydb_docs_copies_tbl.save_db_documnet(cached_keys)

    def postprocess(self):
        self.data_files = [self.data_files]
        self.img_files  = [self.img_files]

    #  { "appnum": _,
    #    "data": { "gbd": _, "ori": _, "qc" : [], "st13": _},
    #    "img": [{ "crc": _, "high": _, "icon" : [], "ori": _, "thum": ...} ...]}
    def _process_record(self, record_data):
        if not (record_data or {}).get('data', None):
            return None

        img_info = record_data.get('img', [])
        data_info = record_data.get('data', {})
        qc_info = data_info.get('qc', None)
        st13 = data_info.get('st13', None)

        # data file failed to transform => skip data & images
        if not st13:
            return None

        # data file failed to run QC => skip data & images
        if qc_info is '__FAIL__':
            return None

        # a copy record for dynamodb
        dydb_copy = {'st13': st13, 'run_id': self.run_id,
                     'archive': self.archive_name,
                     'gbd_collection': self.collection_name,
                     'gbd_type': self.pipeline_type,
                     'office_extraction_date': self.office_extraction_date,
                     'gbd_extraction_date': self.gbd_extraction_date,
                     'biblio': os.path.basename(data_info.get('ori'))}

        # add biblio name to dynamodb copy

        # back up and delete original data file
        ori_doc_file = os.path.join(self.extraction_dir, data_info.get('ori'))
        # check if the collection is not amoung the collection with disable ori backup
        backup_ori = self.collection_name not in self.disabled_backup
        if backup_ori:
            self.backup.store_doc_ori(ori_doc_file, self.archive_name, hard=True)

        for img in img_info:
            # failed to transform => skip
            if not img.get('high', None):
                continue

            # add img name to dynamodb copy
            dydb_copy.setdefault('logo', [])
            dydb_copy['logo'].append(os.path.basename(img.get('ori')))

            # back up and delete original logo files
            ori_img_file = os.path.join(self.extraction_dir, img.get('ori'))
            if backup_ori and os.path.exists(ori_img_file):
                self.backup.store_img_ori(ori_img_file, st13, hard=True)

        # saving the copy
        key = "%s_%s_%s" % (self.collection_name, st13, self.office_extraction_date)
        CachedCopy(self.output_dir, key, document=dydb_copy)

        return key

