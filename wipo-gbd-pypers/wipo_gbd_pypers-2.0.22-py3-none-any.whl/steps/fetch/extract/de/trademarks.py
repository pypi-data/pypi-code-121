import os
import codecs
import math
import xml.etree.ElementTree as ET
import xml.dom.minidom as md
from pypers.utils.xmldom import clean_xmlfile
from pypers.steps.base.extract import ExtractBase


class Trademarks(ExtractBase):
    """
    Extract DETM archive
    """
    spec = {
        "version": "2.0",
        "descr": [
            "Returns the directory with the extraction"
        ]}

    xml_count = 0

    def add_xml_file(self, f_name, fullpath):
        if os.environ.get('GBD_DEV_EXTRACT_LIMIT', None):
            if len(self.manifest['data_files'].keys()) >= int(
                    os.environ.get('GBD_DEV_EXTRACT_LIMIT')):
                return
        self.logger.info('\nprocessing file: %s' % f_name)
        clean_xmlfile(fullpath, overwrite=True)
        context = ET.iterparse(fullpath, events=('end', ))
        for event, elem in context:
            if elem.tag == 'MARKDOC':
                try:
                    appnum = elem.find('CURRENT').find('NR').text
                except Exception as e:
                    continue
                # 1000 in a dir
                xml_subdir = str(int(math.ceil(self.xml_count/1000 + 1))).zfill(4)
                xml_dest = os.path.join(self.extraction_dir, xml_subdir)
                tmxml_file = os.path.join(xml_dest, '%s.xml' % appnum)
                if not os.path.exists(xml_dest):
                    os.makedirs(xml_dest)

                with codecs.open(tmxml_file, 'w', 'utf-8') as fh:
                    fh.write(md.parseString(
                        ET.tostring(elem, 'utf-8')).toprettyxml())
                self.manifest['data_files'].setdefault(appnum, {})
                self.manifest['data_files'][appnum]['ori'] = os.path.relpath(
                    tmxml_file, self.extraction_dir
                )
                elem.clear()
                self.xml_count += 1
        os.remove(fullpath)

    def process(self):
        pass
