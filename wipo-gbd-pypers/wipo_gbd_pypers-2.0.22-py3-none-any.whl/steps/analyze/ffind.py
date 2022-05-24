import os
import glob
import json

from pypers.steps.base.step_generic import EmptyStep

class FFind(EmptyStep):
    """
    Orders manifets base on office_extraction_date
    """
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
                    'descr': 'output data to transform for indexer'
                }
            ]
        }
    }

    def process(self):
        self.files = []

        self.collection_name = self.collection.replace('analyze_', '')

        # stage_root  GBDFILES_DIR/run_id/type/collection/
        # gbd_file    stage_root/000/st13/run_id.json
        # latest_file stage_root/000/st13/lastest.json
        # image_files stage_root/000/st13/crc-hi.png

        stage_root = os.path.join(os.environ.get('GBDFILES_DIR'),
                                 self.run_id,
                                 self.pipeline_type,
                                 self.collection_name)

        # stage_path stage_root/000/, stage_root/001/ ...
        for sub_dir in os.listdir(stage_root):
            files_1k = {}
            stage_path = os.path.join(stage_root, sub_dir)

            # doc_path stage_path/st13/
            for st13 in os.listdir(stage_path):
                doc_path = os.path.join(stage_path, st13)
                gbd_file = os.path.join(doc_path, '%s.json' % self.run_id)
                latest_file = os.path.join(doc_path, 'latest.json')

                # might already be there if resuming step
                idx_file = os.path.join(doc_path, 'idx.json')

                # latest has not yet been pushed to dydb
                # => transformation or analysis still needs to happen
                if os.path.exists(latest_file):
                    doc = { 'data_files' : {}, 'img_files': [] }
                    doc['data_files']['latest'] = os.path.relpath(latest_file, stage_root)

                    if os.path.exists(gbd_file):
                        doc['data_files']['gbd'] = os.path.relpath(gbd_file, stage_root)
                        # read the feature from gbd_file
                        with open(gbd_file, 'r') as f:
                            gbd_data = json.load(f)
                        doc['feature'] = gbd_data.get('markFeature')

                    # no gbd file => is there an idx file
                    # (index file created but failed to index in solr)
                    elif os.path.exists(idx_file):
                        doc['data_files']['idx'] = os.path.relpath(idx_file, stage_root)
                        # read the feature from idx_file
                        with open(idx_file, 'r') as f:
                            idx_data = json.load(f)
                        doc['feature'] = idx_data.get('markFeature')

                    # no gbd file, no idx file. only latest
                    # => not good, something went wrong on the way
                    else:
                        continue

                    # set the img_files
                    img_files = glob.glob(os.path.join(doc_path, '*-hi.png'))
                    for img_file in img_files:
                        crc = os.path.basename(img_file).replace('-hi.png', '')
                        doc.setdefault('img_files', [])
                        doc['img_files'].append({
                            'crc': crc,
                            'img': os.path.relpath(img_file, stage_root)
                        })

                    files_1k[st13] = doc

            self.files.append(files_1k)

