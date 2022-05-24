import os
import codecs
import mimetypes
import xml.etree.ElementTree as ET
from pypers.utils import utils
from pypers.steps.base.extract import ExtractBase


class Trademarks(ExtractBase):
    """
    Extract EMTM_XML archive
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
                    "name": "img_dest_dir",
                    "descr": "the directory that contains image extractions"
                }
            ],
            "outputs": [
                {
                    "name": "del_list",
                    "descr": "del file that contains a list of application"
                             " numbers to be deleted"
                }
            ],
        }
    }


    def preprocess(self):
        self.data_files = {}
        self.img_files = {}
        self.media_files = {}
        self.manifest = { 'data_files': {},
                         'img_files': {},
                         'media_files': {}}
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
        xml_dir = os.path.join(self.extraction_dir, 'xml')
        os.makedirs(xml_dir, exist_ok=True)

        for archive in archives:
            archive_name = os.path.basename(archive)
            dest = os.path.join(self.extraction_dir, archive_name)
            os.makedirs(dest, exist_ok=True)
            # unpack the archives and collect the files
            self.collect_files(self.unpack_archive(archive, dest))

    def add_xml_file(self, _, xml_file):
        if os.environ.get('GBD_DEV_EXTRACT_LIMIT', None):
            if len(self.manifest['data_files'].keys()) >= int(
                    os.environ.get('GBD_DEV_EXTRACT_LIMIT')):
                return
        xml_dir = os.path.join(self.extraction_dir, 'xml')
        ns = 'http://www.euipo.europa.eu/EUTM/EUTM_Download'
        ET.register_namespace('', ns)
        context = ET.iterparse(xml_file, events=('end',))
        for event, elem in context:
            if elem.tag[0] == "{":
                uri, tag = elem.tag[1:].split("}")
            else:
                tag = elem.tag
            if tag == 'TradeMark':
                appnum = elem.find(
                    '{%(ns)s}ApplicationNumber' % {'ns': ns}).text
                app_file = os.path.join(xml_dir, '%s.xml' % (appnum))
                with codecs.open(app_file, 'w', 'utf-8') as fh:
                    fh.write(ET.tostring(elem, 'utf-8').decode("utf-8"))
                self.manifest['data_files'].setdefault(appnum, {})
                self.manifest['data_files'][appnum]['ori'] = os.path.relpath(
                    app_file, self.extraction_dir
                )
                # self.logger.info('%s: %s [%s]' % (
                #    uid, upd_mode.lower(), app_file))
                elem.clear()

        # remove original xml file
        os.remove(xml_file)

    def process(self):
        pass