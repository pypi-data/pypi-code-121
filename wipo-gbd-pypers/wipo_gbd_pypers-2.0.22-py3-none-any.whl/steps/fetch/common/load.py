import os
import json
from datetime import datetime
if os.environ.get('GITHUB_TOKEN'):
    from pypers.test import MockXMLParser as Parser
else:
    from gbdtransformation.parser import Parser
from pypers.core.interfaces import db
from pypers.core.interfaces.config.pypers_storage import RAW_DOCUMENTS
from pypers.core.interfaces.storage import get_storage
from pypers.steps.base.step_generic import EmptyStep

class Load(EmptyStep):
    """
    Load RAW XML FILES INTO DB
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
                    "name": "manifest",
                    "descr": "the manifest of extraction",
                    "iterable": True
                }
            ],
            "outputs": [
                {
                    "name": "manifest",
                    "descr": "the manifest after staging json"
                }
            ]
        }
    }

    def process(self):
        parser = None
        self.storage = get_storage()
        report = []
        to_delete = [num for num in self.manifest['data_files'].keys() if self.manifest['data_files'][num]['to_delete']]
        to_insert = []
        e_type = 'APP' if self.collection.endswith('ap') else 'REP'
        # Prepare holder for new manifets to be written when updated data arrives
        self.manifests = {}
        for num in [num for num in self.manifest['data_files'].keys() if not self.manifest['data_files'][num]['to_delete']]:
            data = self.manifest['data_files'][num]
            ori_file = os.path.join(self.manifest['extraction_dir'], data['ori'])
            if not parser:
                parser = Parser(self.collection, type=self.pipeline_type)

            # attempt the transformation
            try:
                db_data = db.get_db_entity().get_document(self.collection[0:2], num, e_type=e_type)
                if not db_data:
                    db_data = {
                        'entity_id': "%s.%s.%s" % (self.collection[0:2], e_type, num),
                        'payload': {},
                        'linked_items': []
                    }
                gbd_data = parser.run(ori_file, raise_errors=True)
                db_data['payload'] = json.loads(gbd_data)
                # write the gbd.json file
                gbd_file = ori_file.replace('.xml', '.json')
                if db_data['linked_items']:
                    for linked_item in db_data['linked_items']:
                        self._prepare_entity_upload(linked_item, e_type)
                with open(gbd_file, 'w') as f:
                    f.write(json.dumps(db_data))
                to_insert.append(gbd_file)
            except Exception as e:
                report.append({'type': 'transform',
                               'appnum': data,
                               'error': str(e)})
        db.get_db_entity().put_items(to_insert)
        db.get_db_entity().delete_items(self.collection[0:2], to_delete, e_type)
        self._write_manifets()

    def _get_manifest(self, ori_path):
        if not self.manifests.get(ori_path, None):
            self.manifests[ori_path] = {
                'gbd_extraction_date': datetime.now().strftime('%Y-%m-%d'),
                'data_files': {},
                'img_files': self.manifest['img_files']
            }
        return self.manifests[ori_path]

    def _write_manifets(self):
        for path in self.manifests.keys():
            manifest_path = os.path.join(path, 'manifest.json')
            with open(manifest_path, 'w') as f:
                json.dump(self.manifests[path], f, indent=2)

    def _prepare_entity_upload(self, st13, e_type):
        current_copy = db.get_pre_prod_db().get_document(st13)
        if current_copy:
            archive_date = self.manifest['archive_date']
            archive_name = "%s_A%s" % (archive_date, e_type)
            doc_src_path = os.path.join(RAW_DOCUMENTS,
                                        current_copy['gbd_type'],
                                        current_copy['gbd_collection'],
                                        current_copy['archive'],
                                        "%s.xml" % st13)
            ori_path = os.path.join(os.environ.get('ORIFILES_DIR'),
                                    # mandatory ENV VARIABLE - we do not want to make defaults
                                    self.run_id,
                                    current_copy['gbd_type'],
                                    current_copy['gbd_collection'],
                                    archive_date,
                                    archive_name)
            manifest = self._get_manifest(ori_path)
            xml_path = os.path.join(ori_path, 'xml')
            os.makedirs(xml_path, exist_ok=True)
            dest_path = os.path.join(xml_path, '%s.xml' % st13)
            manifest['data_files'].setdefault(st13, {})
            manifest['data_files'][st13]['ori'] = os.path.relpath(
                    dest_path, ori_path)
            if os.path.exists(dest_path):
                return
            self.storage.get_file(doc_src_path, dest_path)



    def postprocess(self):
        self.manifest = [self.manifest]
