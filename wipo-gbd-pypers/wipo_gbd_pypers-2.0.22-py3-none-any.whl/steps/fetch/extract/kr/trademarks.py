import os
import re
import mimetypes
import xml.etree.ElementTree as ET
from pypers.utils import utils
from pypers.steps.base.extract import ExtractBase

class Trademarks(ExtractBase):
    """
    Extract KRTM archives
    """
    spec = {
        "version": "2.0",
        "descr": [
            "Returns the directory with the extraction"
        ]
    }

    ignore_imgs = []
    appnum_re = re.compile(r'.*(KR\d+).*')

    def preprocess(self):
        self.data_files = {}
        self.img_files = {}
        self.media_files = {}
        self.manifest = {
            'data_files': {},
            'img_files': {},
        }
        # self.archives is a tuple of (date, {archive_name: xxx, archives[]})

        if not len(self.archives):
            return

        extraction_date = self.archives[0]
        archive_name = self.archives[1]['name']
        archives = self.archives[1]['archives']
        # prepare destination dir under pipeline scratch dir
        self.extraction_dir = os.path.join(
            self.meta['pipeline']['output_dir'],
            '__scratch',
            extraction_date,
            archive_name
        )

        # deletes the directory if prev exists
        utils.mkdir_force(self.extraction_dir)

        self.manifest = {'archive_name': archive_name,
                         'archive_file': archive_name,
                         'archive_date': extraction_date,
                         'extraction_dir': self.extraction_dir,
                         'data_files': {},
                         'img_files': {},
                         'media_files': {}}

        for archive in archives:
            # unpack the archives and collect the files
            if 'IMGB' in os.path.basename(archive):
                continue
            else:
                f_name, _ = os.path.splitext(os.path.basename(archive))
                dest = os.path.join(self.extraction_dir, f_name)
                os.makedirs(dest, exist_ok=True)
                self.collect_files(self.unpack_archive(archive, dest))

    def file_in_archive(self, file, path):
        fname, ext = os.path.splitext(os.path.basename(file))
        if ext.lower() == '.xml':
            self._add_xml_file(fname, os.path.join(path, file))
        else:
            file_mime = mimetypes.guess_type(file)[0]
            if (file_mime or '').startswith('image/'):
                self._add_img_file(file, os.path.join(path, file))

    # identify app num from image name
    def _add_img_file(self, file, path):
        fname, ext = os.path.splitext(os.path.basename(file))
        try:
            image_appnum = str(self.appnum_re.match(fname).group(1))
        except Exception as e:
            return
        self.add_img_file(image_appnum, path)

    # xml of xmls => split to files
    def _add_xml_file(self, file, xml_file):
        appnum_match = self.appnum_re.match(file).group(1)
        # not a file that we want
        if not appnum_match:
            return
        context = ET.iterparse(xml_file, events=('end',))
        """
        for event, elem in context:
            tag = elem.tag
            # check if it has an image
            try:
                img_tag = elem.find('KRWordMarkSpecification/ImageFileName')
                words_tag = elem.find('KRWordMarkSpecification/MarkVerbalElementText')
                if img_tag and img_tag.text and words_tag and words_tag.text:
                    self.ignore_imgs.append(str(appnum_match))
            except Exception as e:
                self.logger.info('%s: %s ' % (str(appnum_match), e))
        """
        self.add_xml_file(str(appnum_match), xml_file)

    def process(self):
        if not self.manifest['img_files']:
            return
        keys = list(self.manifest['img_files'].keys())
        for img in keys:
            if img in self.ignore_imgs:
                self.self.manifest['img_files'].pop(img, None)
