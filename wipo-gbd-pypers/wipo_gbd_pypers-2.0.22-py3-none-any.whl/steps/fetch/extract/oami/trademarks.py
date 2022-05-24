import os
import re
import mimetypes
from pypers.utils import utils
from pypers.steps.base.extract import ExtractBase


class Trademarks(ExtractBase):
    """
    Extract OAMI TM archives
    """
    spec = {
        "version": "2.0",
        "descr": [
            "Returns the directory with the extraction"
        ]
    }


    def preprocess(self):
        self.data_files = {}
        self.img_files = {}
        self.media_files = {}
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
        coll_name = self.meta['pipeline']['collection'][0:2].upper()
        self.appnum_re = re.compile(r'.*(%s\d+).*' % coll_name)
        self.manifest = {'archive_name': archive_name,
                         'archive_file': archive_name,
                         'archive_date': extraction_date,
                         'extraction_dir': self.extraction_dir,
                         'data_files': {},
                         'img_files': {},
                         'media_files': {}}
        for archive in archives:
            self.collect_files(self.unpack_archive(archive, os.path.join(self.extraction_dir, os.path.basename(archive))))

    def file_in_archive(self, file, path):
        if file.endswith('500000000000000.xml'):
            return
        appnum, ext = os.path.splitext(os.path.basename(file))
        appnum = self.appnum_re.match(appnum).group(1)
        if ext.lower() == '.xml':
            self.add_xml_file(appnum, os.path.join(path, file))
        else:
            file_mime = mimetypes.guess_type(file)[0]
            if (file_mime or '').startswith('image/'):
                self.add_img_file(appnum, os.path.join(path, file))
            elif file_mime == 'application/zip':
                self.archive_in_archive(file, path)

    def process(self):
        pass