import os
import codecs
import base64
import xml.dom.minidom as md
import xml.etree.ElementTree as ET
from pypers.steps.base.extract import ExtractBase
from pypers.utils import utils


class Trademarks(ExtractBase):
    """
    Extract KZTM_XML archive (copied from FRTM extraction)
    """
    spec = {
        "version": "2.0",
        "descr": [
            "Returns the directory with the extraction"
        ]
    }

    # initializes the outputs
    def preprocess(self):
        self.data_files = {}
        self.img_files = {}
        self.media_files = {}
        # self.archives is a tuple of (date, file)

        if not len(self.archives):
            return

        extraction_date = self.archives[0]
        archive = self.archives[1]

        archive_name, _ = os.path.splitext(os.path.basename(archive))

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
                         'archive_file': archive,
                         'archive_date': extraction_date,
                         'extraction_dir': self.extraction_dir,
                         'data_files': {},
                         'img_files': {},
                         'media_files': {}}

        # unpack the archives and collect the files
        self.add_xml_file(archive_name, archive)

    def add_xml_file(self, filename, fullpath):
        img_dir = os.path.join(self.extraction_dir, 'img')
        xml_dir = os.path.join(self.extraction_dir, 'xml')
        os.makedirs(img_dir, exist_ok=True)
        os.makedirs(xml_dir, exist_ok=True)
        self.logger.info('\nprocessing file: %s' % filename)
        context = ET.iterparse(fullpath, events=('end',))
        for event, elem in context:
            if event == 'end' and elem.tag == 'U_ID':
                # U_ID nodes
                appnum_node = elem.find('inid_210')
                # skip it
                if appnum_node is None:
                    continue

                appnum = appnum_node.text
                img_node = elem.find('image')

                if img_node is not None:
                    img_base64 = img_node.text
                    img_name = '%s.%s' % (appnum, 'png')
                    img_dest = os.path.join(img_dir, img_name)
                    with open(img_dest, 'wb') as fh:
                        fh.write(base64.b64decode(img_base64))
                    self.add_img_file(appnum, img_dest)
                    # replace image content by a yes
                    img_node.text = 'yes'

                appxml_file = os.path.join(xml_dir, '%s.xml' % appnum)
                with codecs.open(appxml_file, 'w', 'utf-8') as fh:
                    fh.write(md.parseString(
                        ET.tostring(elem, 'utf-8')).toprettyxml())
                self.manifest['data_files'].setdefault(appnum, {})
                self.manifest['data_files'][appnum]['ori'] = os.path.relpath(
                    appxml_file, self.extraction_dir
                )
                elem.clear()
        # remove the file when done with it
        os.remove(fullpath)

    def process(self):
        pass