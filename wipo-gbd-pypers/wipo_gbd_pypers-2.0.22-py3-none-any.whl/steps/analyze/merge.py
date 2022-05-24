import os
import json
from . import merge_data_img_files
from pypers.core.interfaces import msgbus
from pypers.utils.utils import delete_files, clean_folder
from pypers.steps.base.step_generic import EmptyStep

class Merge(EmptyStep):
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
                    "name": "data_files",
                    "descr": "input structured data"
                },
                {
                    "name": "img_files",
                    "descr": "input structured data"
                }
            ],
            "params": [
                {
                    "name": "chain",
                    "type": "int",
                    "descr": "an int flag (0|1) whether to "
                             "chain to the next pipeline",
                    "value": 0
                }
            ]
        }
    }

    # --------------------------------------------
    # Merge img analysis info into data index
    # --------------------------------------------
    # self.img_files  [ {'st13': _, 'crc': _, 'idx': _},
    #                   {'st13': _, 'crc': _, 'idx': _} ]
    # self.data_files [ {'st13': _, 'latest': _, 'idx': _},
    #                   {'st13': _, 'latest': _, 'idx': _} ]
    def process(self):
        self.collection_name = self.collection.replace('analyze_', '')

        # no images have been analysed
        # => nothing to merge
        if not len(self.img_files):
            return

        # stage_root  GBDFILES_DIR/run_id/type/collection/
        stage_root = os.path.join(os.environ.get('GBDFILES_DIR'),
                                  self.run_id,
                                  self.pipeline_type,
                                  self.collection_name)

        # { st13: { idx_img: _, idx_data: _, latest: _ },
        #   st13: { idx_img: _, idx_data: _, latest: _ }
        idx_records = merge_data_img_files(self.data_files, self.img_files)

        for st13, record in idx_records.items():
            lire_data = []
            for img in record['idx_img']:
                idx_img_file = os.path.join(stage_root, img)
                with open(idx_img_file, 'r') as f:
                    lire_data_img = json.loads(f.read())
                lire_data.append(lire_data_img)

            idx_data_file = os.path.join(stage_root, record['idx_data'])
            latest_file = os.path.join(stage_root, record['latest'])

            with open(latest_file, 'r') as f:
                latest_data = json.loads(f.read())
                latest_data['image_analysis'] = lire_data
            with open(latest_file, 'w') as f:
                f.write(json.dumps(latest_data))

            with open(idx_data_file, 'r') as f:
                idx_data = json.loads(f.read())
                # To remove when solr is ready for multi_image
                if len(lire_data) > 0:
                    idx_data.update(self.parse_lire_solr(lire_data))
            with open(idx_data_file, 'w') as f:
                f.write(json.dumps(idx_data))

            # done with image analysis file
            for img in record['idx_img']:
                idx_img_file = os.path.join(stage_root, img)
                os.remove(idx_img_file)

    def convert_keys_type(self, input_dict):
        for key in input_dict.keys():
            if isinstance(input_dict[key], list):
                input_dict[key] = set(input_dict[key])
        return input_dict

    def parse_lire_solr(self, lires):
        to_return = self.convert_keys_type(lires[0])
        for lire in lires[1:]:
            for key in lire.keys():
                if isinstance(lire[key], list):
                    to_return[key] = to_return[key].union(set(lire[key]))
                else:
                    to_return[key] = '%s,%s' % (to_return[key], lire[key])
        for key in to_return.keys():
            if isinstance(to_return[key], set):
                to_return[key] = list(to_return[key])
        return to_return

    def postprocess(self):
        output_dir = os.path.join(os.environ['WORK_DIR'],
                                  self.run_id,
                                  self.pipeline_type,
                                  self.collection_name)

        if int(self.chain):
            force_restart = self.meta['pipeline'].get('force_restart', 'False')
            msgbus.get_msg_bus().send_message(self.run_id,
                                            collection="index_%s" % self.collection_name,
                                            type=self.pipeline_type,
                                            custom_config=['pipeline.output_dir=%s' % output_dir,
                                                           'pipeline.forced_restarted=%s' % force_restart,
                                                           'pipeline.is_operation=%s' % self.is_operation,
                                                           'steps.merge.chain=1'])

        pipeline_dir = self.meta['pipeline']['output_dir']
        delete_files(pipeline_dir, patterns=['.*json'])
        clean_folder(pipeline_dir)




