import os
import re
import mimetypes
import codecs
import xml.etree.ElementTree as ET

from pypers.utils import utils
from pypers.steps.base.extract import ExtractBase
from pypers.utils.xmldom import get_ns_from_xml


class Trademarks(ExtractBase):
    """
    Extract FRTM_XML archive
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

        self.manifest = {'archive_name': archive_name,
                         'archive_file': archive_name,
                         'archive_date': extraction_date,
                         'extraction_dir': self.extraction_dir,
                         'data_files': {},
                         'img_files': {},
                         'media_files': {}}

        for archive in archives:
            # unpack the archives and collect the files
            self.current_archive = os.path.basename(archive)
            self.collect_files(self.unpack_archive(archive, self.extraction_dir))


    def file_in_archive(self, file, path):
        # data file in data archive
        if self.current_archive.find('ST66') > -1:
            if file.lower().endswith('.xml'):
                self._add_xml_file(file, path)
        if self.current_archive.find('image') > -1:
            file_mime = mimetypes.guess_type(file)[0]
            if (file_mime or '').startswith('image/'):
                if file.endswith('.tif'):
                    return
                self._add_img_file(file, path)

    # identify app num from image name
    def _add_img_file(self, file, path):
        # translate file name to appnum
        _img_rgx = re.compile('fmark0*(\d*)_.*', re.IGNORECASE)
        match = _img_rgx.match(file)

        if match:
            appnum = match.group(1)
            self.add_img_file(appnum, os.path.join(path, file))

    # xml of xmls => split to files
    def _add_xml_file(self, file, path):
        xml_file = os.path.join(path, file)

        ns = get_ns_from_xml(xml_file)
        ET.register_namespace('', ns)

        context = ET.iterparse(xml_file, events=('end', ))
        for event, elem in context:
            if elem.tag[0] == "{":
                uri, tag = elem.tag[1:].split("}")
            else:
                tag = elem.tag

            if tag == 'TradeMark':
                appnum = elem.find('{%(ns)s}ApplicationNumber' % {
                    'ns': ns}).text

                # split in directories not to overwhelm the fs
                appxml_path = utils.appnum_to_dirs(path ,appnum)
                appxml_file = os.path.join(appxml_path,  '%s.xml' % appnum)

                try: os.makedirs(appxml_path)
                except: pass

                with codecs.open(os.path.join(self.extraction_dir, appxml_file), 'w', 'utf-8') as fh:
                    fh.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
                    fh.write(ET.tostring(elem).decode("utf-8"))

                self.add_xml_file(appnum, os.path.join(self.extraction_dir, appxml_file))

                elem.clear()

        # done with it
        os.remove(xml_file)

    def process(self):
        pass
