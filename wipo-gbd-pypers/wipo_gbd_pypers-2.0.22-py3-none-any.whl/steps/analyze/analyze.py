import os
import glob
import json
import subprocess
from pypers.core.interfaces import db
from pypers.steps.base.step_generic import EmptyStep


class Analyze(EmptyStep):
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
                    'descr': 'output images to analyse',
                    'iterable': True
                }
            ],
            'outputs': [
                {
                    'name': 'img_files',
                    'descr': 'img_files with a new image index analysis'
                }
            ],
            "params": [
                {
                    "name": "skip_analyze_verbal_images",
                    "type": "str",
                    "descr": "List of collections for which the verbal images should NOT be analyzed",
                    "value": "emtm, frtm, krtm, vntm"
                }
            ]
        }
    }

    # --------------------------------------------------
    # update latest file with lire analysis where needed
    # --------------------------------------------------
    # "files" : {
    #     "st13" : {
    #         "data_files" : { "latest": "000/st13/latest.json" }
    #         "feature": "Word|Combined|..."
    #         "img_files" : [{
    #             "crc" : "XXXXXXXX",
    #             "img" : "000/st13/XXXXXXXX-hi.png"
    #         }]
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

        # [ {'st13': _, 'crc': _, 'idx': _},
        #   {'st13': _, 'crc': _, 'idx': _} ]
        self.img_files = []

        # dynamo db / gbd_pypers_indexer
        img_files_for_analysis = []

        # loop records to find images for analysis
        for st13, record in self.files.items():
            # no images => move on
            if not len(record.get('img_files', [])):
                continue

            # read feature from record
            feature = record.get('feature')

            # read image_analysis from latest
            latest_file = os.path.join(stage_root, record['data_files']['latest'])
            with open(latest_file, 'r') as f:
                latest_data = json.load(f)
            latest_img_analysis = latest_data.get('image_analysis', [])

            for img_info in record['img_files']:
                img_file = os.path.join(stage_root, img_info['img'])

                is_analysed = self._is_analysed(img_info['crc'],
                                                latest_img_analysis)
                is_skipped = self._skip_feature(feature)

                # will not analyse image => remove
                if is_analysed or is_skipped:
                    os.remove(img_file)
                    continue

                img_files_for_analysis.append(img_file)


        # no images to (re)analyse
        if not len(img_files_for_analysis):
            return

        # IMAGEANALYSIS STARTS HERE
        # -------------------------
        self.logger.debug('[ANALYZE][START] // %s image files to analyze' % len(img_files_for_analysis))

        # write fofn file
        fofn_file = os.path.join(self.output_dir, 'images.fofn')

        with open(fofn_file, 'w') as f:
            f.write('\n'.join(img_files_for_analysis))

        self._run_analyze_command(fofn_file)

        succeeded = len(glob.glob(os.path.join(stage_root, '*', '*', '*-hi.json'))) # stage_root/000/st13/*-hi.*
        failed = len(glob.glob(os.path.join(stage_root, '*', '*', '*-hi.error')))

        self.logger.debug('[ANALYZE][END] // %s analysis succeeded // %s analysis failed' % (succeeded, failed))

        # loop records to find images with analysis files present
        for st13, record in self.files.items():
            # no images => move on
            if not len(record.get('img_files', [])):
                continue

            for img_info in record['img_files']:
                img_path = os.path.dirname(img_info['img'])
                img_name = os.path.basename(img_info['img'])

                img_analysis_file = os.path.join(stage_root,
                                                 img_path,
                                                 img_name.replace('.png', '.json'))

                # a newly analysed image !
                if os.path.exists(img_analysis_file):
                    img_record = { 'st13': st13,
                                   'crc': img_info['crc'],
                                   'idx': os.path.relpath(img_analysis_file, stage_root) }

                    self.img_files.append(img_record)

                    # done with image file
                    img_file = os.path.join(stage_root, img_info['img'])
                    os.remove(img_file)

    def _is_analysed(self, crc, latest_img_analysis):
        for img in latest_img_analysis:
            if img.get('crc') == crc:
                return True
        return False

    def _skip_feature(self, feature):
        return feature is 'Word' and self.collection_name in self.skip_analyze_verbal_images

    def _run_analyze_command(self, fofn_file):
        jar_file = os.environ.get('IMAGEANALYSIS_JAR').strip()
        conf_url = os.environ.get('IMAGEANALYSIS_CONF_URL', '').strip()
        atac_url = os.environ.get('IMAGEANALYSIS_CLASSIF_ENDPOINT', '').strip()
        cmd = "java -jar %s --configuration %s --type %s --atac %s --fofn %s --threads 5 --outputContent index"
        cmd = cmd % (jar_file,
                     conf_url,
                     self.pipeline_type,
                     atac_url,
                     fofn_file)
        proc = subprocess.Popen(cmd.split(' '),
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                close_fds=True)
        stdout, stderr = proc.communicate()

        rc = proc.returncode

        if rc != 0:
            self.logger.error(str(stderr))
            db.get_db_error().send_error(self.run_id,
                                         self.collection_name,
                                         {'source': 'image_analysis'},
                                         str(stderr))
