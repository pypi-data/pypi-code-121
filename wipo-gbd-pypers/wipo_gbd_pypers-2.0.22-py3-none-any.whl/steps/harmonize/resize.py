import os
import shutil
from pypers.utils.img import Convert as convert, \
    Generate as generate
from pypers.utils import img
from pypers.utils.utils import rename_file
from pypers.core.interfaces import db

from pypers.steps.base.step_generic import EmptyStep


class Resize(EmptyStep):
    spec = {
        'version': '2.0',
        'descr': [
            'Convert Images to jpg, crop, create thumbnails and icon files'
        ],
        "args":
        {
            "inputs": [
                {
                    "name": "img_files",
                    "descr": "input structured data",
                    "iterable": True
                },
                {
                    "name": "extraction_dir",
                    "descr": "the extraction dir",
                    "iterable": True
                }
            ],
            'outputs': [
                {
                    'name': 'img_files',
                    'descr': 'output processed data'
                }
            ],
            "params": [
                {
                    'name': 'crop',
                    'type': 'int',
                    'value': 1,
                    'descr': 'crop white edges of images'
                },
                {
                    'name': 'high_ext',
                    'descr': 'the extension of high img file',
                    'type': 'str',
                    'value': 'png'
                },
                {
                    'name': 'compress',
                    'descr': 'a flag whether to compress the images',
                    'type': 'int',
                    'value': 0
                }
            ]
        }
    }

    # self.img_files {'123': [{'ori': _}, {'ori: _'}], '234': [{'ori': _}]}
    def process(self):
        if not self.img_files:
            return

        _faded = []
        _corrupt = []
        _cropped = []

        for appnum, data in self.img_files.items():
            # can have multiple images
            for idx, files in enumerate(data):
                img_ori = os.path.join(self.extraction_dir, files['ori'])

                img_name, img_ext = os.path.splitext(os.path.basename(img_ori))

                # cv2 cannot work with gif => transform to png
                # convert gif to png
                # ------------------
                img_ori = convert.from_gif(img_ori)

                # convert whatever the whatever-hi.%img_ext%
                # --------------------------------------------
                try:
                    img_hgh = convert.to_hgh(img_ori, '%s-hi' % (img_name),
                                             img_ext=self.high_ext)
                except Exception as e:
                    _corrupt.append(appnum)
                    self.logger.error('cannot convert img for %s' % img_ori)
                    continue

                # cropping image
                # --------------
                if self.crop:
                    # -1: no change
                    # 0: cropped
                    # 1: faded
                    # 2: corrupt
                    try:
                        result = img.crop(img_hgh, img_hgh)
                        if result == 0:
                            _cropped.append(appnum)
                        elif result == 1:
                            _faded.append(appnum)
                            continue
                        elif result == 2:
                            _corrupt.append(appnum)
                            continue
                    except Exception as e:
                        _corrupt.append(appnum)
                        continue


                # check if it is a zero-size image
                if os.stat(img_hgh).st_size == 0:
                    _corrupt.append(appnum)
                    continue

                # high image resize after crop
                # ----------------------------
                try:
                    generate.high(img_hgh)
                except Exception as e:
                    _corrupt.append(appnum)
                    continue

                # image compression
                # -----------------
                if self.compress:
                    try:
                        img.compress(img_hgh)
                    except Exception as e:
                        _corrupt.append(appnum)
                        continue

                # high image generated => get its crc
                # -----------------------------------
                crc = img.get_crc(img_hgh)

                # rename high to use crc
                img_hgh = rename_file(img_hgh, '%s-hi' % crc)

                # rename ori to use crc
                img_ori = rename_file(img_ori, crc)

                # generating thumbnail
                # --------------------
                try:
                    img_thm = generate.thumbnail(img_hgh, crc)
                except Exception as e:
                    _corrupt.append(appnum)
                    self.logger.error('cannot generate thumbnail for %s' % img_ori)
                    continue

                # generating icon  (64 x 64)
                # --------------------------
                img_ico = generate.icon(img_hgh, crc)


                # update the
                self.img_files[appnum][idx]['crc']  = crc
                self.img_files[appnum][idx]['ori']  = os.path.relpath(img_ori, self.extraction_dir)
                self.img_files[appnum][idx]['icon'] = os.path.relpath(img_ico, self.extraction_dir)
                self.img_files[appnum][idx]['thum'] = os.path.relpath(img_thm, self.extraction_dir)
                self.img_files[appnum][idx]['high'] = os.path.relpath(img_hgh, self.extraction_dir)


        report = []
        if len(_faded):
            self.logger.warning('Images faded:')
            self.logger.warning('\n'.join(_faded))
            report.extend([{'type': 'faded', 'appnum': app}
                           for app in _faded])
        if len(_corrupt):
            self.logger.warning('Images corrupted:')
            self.logger.warning('\n'.join(_corrupt))
            report.extend([{'type': 'corrupted', 'appnum': app}
                           for app in _corrupt])
        # Needs to update to have a line in the reporting even if there are no errors
        db.get_db().update_process_report(self.run_id, self.collection, report)

    def postprocess(self):
        self.img_files = [self.img_files]
