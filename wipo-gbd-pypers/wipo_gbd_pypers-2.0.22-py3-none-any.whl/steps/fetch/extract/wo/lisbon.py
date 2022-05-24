import os
import codecs
import xml.etree.ElementTree as ET
from pypers.utils.xmldom import clean_xmlfile
from pypers.utils.xmldom import get_ns_from_xml

from pypers.utils import utils
from pypers.steps.base.extract import ExtractBase


class Lisbon(ExtractBase):
    """
    Extract 6ter_XML archive
    """
    spec = {
        "version": "2.0",
        "descr": [
            "Returns the directory with the extraction"
        ]
    }


    def file_in_archive(self, file, path):
        # data file in data archive
        if file.lower().endswith('.xml'):
            if file.lower().startswith('lisbon'):
                self._add_xml_file(file, path)

    # xml of xmls => split to files
    def _add_xml_file(self, file, path):
        clean_xmlfile(os.path.join(path, file), overwrite=True, readenc='ISO-8859-1')
        xml_file = os.path.join(path, file)

        ns = get_ns_from_xml(xml_file)
        ET.register_namespace('', ns)

        context = ET.iterparse(xml_file, events=('end',))
        for event, elem in context:
            if elem.tag[0] == "{":
                uri, tag = elem.tag[1:].split("}")
            else:
                tag = elem.tag

            if tag == 'LISBON':
                sub_output = {}
                appnum = elem.find('NUMBER').text

                # split in directories not to overwhelm the fs
                appxml_path = utils.appnum_to_dirs(path, appnum)
                appxml_file = os.path.join(appxml_path, '%s.xml' % appnum)

                try:
                    os.makedirs(appxml_path)
                except:
                    pass

                with codecs.open(os.path.join(self.extraction_dir, appxml_file), 'w', 'utf-8') as fh:
                    fh.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
                    fh.write(ET.tostring(elem).decode("utf-8"))

                self.add_xml_file(appnum, os.path.join(self.extraction_dir, appxml_file))
                elem.clear()

        # done with it
        os.remove(xml_file)

    def process(self):
        pass
