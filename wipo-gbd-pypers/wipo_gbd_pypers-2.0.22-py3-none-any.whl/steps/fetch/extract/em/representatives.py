import os
import codecs
import xml.etree.ElementTree as ET
from pypers.utils.xmldom import clean_xmlfile
from pypers.steps.base.extract import ExtractBase


class Representatives(ExtractBase):
    """
    Extract EM_REPRESENTATIVE archive
    """
    spec = {
        "version": "2.0",
        "descr": [
            "Returns the directory with the extraction"
        ],
    }

    def add_xml_file(self, _, xml_file):
        if os.environ.get('GBD_DEV_EXTRACT_LIMIT', None):
            if len(self.manifest['data_files'].keys()) >= int(
                    os.environ.get('GBD_DEV_EXTRACT_LIMIT')):
                return
        xml_dir = os.path.join(self.extraction_dir, 'xml')
        os.makedirs(xml_dir, exist_ok=True)
        ns = 'http://www.euipo.europa.eu/EUTM/EUTM_Download'
        ET.register_namespace('', ns)
        clean_xmlfile(xml_file, overwrite=True)
        context = ET.iterparse(xml_file, events=('end',))
        for event, elem in context:
            if elem.tag[0] == "{":
                uri, tag = elem.tag[1:].split("}")
            else:
                tag = elem.tag
            if tag == 'Representative':
                uid = elem.find('{%(ns)s}RepresentativeIdentifier' % {
                    'ns': ns}).text
                upd_mode = elem.attrib['operationCode']

                # only write the Design element
                app_file = os.path.join(xml_dir, '%s.xml' % (uid))
                with codecs.open(app_file, 'w', 'utf-8') as fh:
                    fh.write(ET.tostring(elem, 'utf-8').decode("utf-8"))
                self.manifest['data_files'].setdefault(uid, {})
                self.manifest['data_files'][uid]['ori'] = os.path.relpath(
                    app_file, self.extraction_dir
                )
                self.manifest['data_files'][uid]['to_delete'] = (upd_mode.lower() == 'delete')
                # self.logger.info('%s: %s [%s]' % (
                #    uid, upd_mode.lower(), app_file))
                elem.clear()

        # remove original xml file
        os.remove(xml_file)

    def process(self):
        pass