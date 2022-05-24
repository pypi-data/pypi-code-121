import os
import json

from gbdtransformation.parser import Parser

from pypers.steps.base.step_generic import EmptyStep


class Transform(EmptyStep):
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
            'inputs': [
                {
                    'name': 'files',
                    'descr': 'output data to transform for indexer',
                    'iterable': True
                }
            ],
            'outputs': [
                {
                    'name': 'data_files',
                    'descr': 'data_files dictionary with an extra idx file'
                }
            ]
        }
    }

    # ------------------------------------------
    # Generate idx file from gbdfile where found
    # ------------------------------------------

    # "files" : {
    #     "st13" : {
    #         # get either idx of gbd
    #         "data_files" : {
    #             "idx" : "000/st13/idx.json",
    #             "gbd" : "000/st13/run_id.json",
    #             "latest" : "000/st13/latest.json"
    #         },
    #         "feature": "..."
    #         "img_files" : [...]
    #     },
    #     ...
    # }
    def process(self):
        if not len(self.files.keys()):
            return

        self.collection_name = self.collection.replace('analyze_', '')

        # stage_root  GBDFILES_DIR/run_id/type/collection/
        stage_root = os.path.join(os.environ.get('GBDFILES_DIR'),
                                  self.run_id,
                                  self.pipeline_type,
                                  self.collection_name)

        # transform to idx file
        parser = Parser('solrjtm', type=self.pipeline_type)

        # [ {'st13': _, 'latest': _, 'idx': _},
        #   {'st13': _, 'latest': _, 'idx': _} ]
        self.data_files = []

        for st13, record in self.files.items():
            # no gbd file is set => nothing to transform
            if not record['data_files'].get('gbd'):
                continue

            gbd_file = os.path.join(stage_root, record['data_files']['gbd'])

            # attempt the transformation to an idx file
            idx_file = os.path.join(os.path.dirname(gbd_file), 'idx.json')
            try:
                idx_data = json.loads(parser.run(gbd_file, raise_errors=True))

                # amend the index data with collection
                idx_data['collection'] = self.collection_name
                # amend the index data with runid
                idx_data['runid'] = self.run_id
                # amend the index data with imgs crc
                for img_info in record.get('img_files', []):
                    idx_data.setdefault('logo', [])
                    idx_data['logo'].append(img_info['crc'])

                # (re)write the idx file
                with open(idx_file, 'w') as f:
                    json.dump(idx_data, f, indent=2)

                # success in transform => add to data_files
                data_record = { 'st13': st13,
                                'latest': record['data_files']['latest'],
                                'idx': os.path.relpath(idx_file, stage_root) }

                self.data_files.append(data_record)

                # done with original file
                os.remove(gbd_file)
            except Exception as e:
                self.logger.error("Error in transforming %s to solr: %s" % (st13, e))

