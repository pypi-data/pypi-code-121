import os
import codecs
import shutil
import xml.etree.ElementTree as ET
from pypers.steps.base.extract_step import ExtractStep


class Designs(ExtractStep):
    """
    Extract WOID archives
    """
    spec = {
        "version": "0.1",
        "descr": [
            "Returns the directory with the extraction"
        ]
    }

    def get_raw_data(self):
        xml_files = []
        archive_uid, archive_path, archive_name = self.get_path()
        if archive_uid == None:
            return []
        shutil.copy(archive_path, os.path.join(self.dest_dir[0], archive_name))
        for r, d, files in os.walk(self.dest_dir[0]):
            for f in files:
                xml_files.append(os.path.join(r, f))
        return xml_files

    def process_xml_data(self, xml_files):
        extraction_data = []
        dgn = 'http://www.wipo.int/standards/XMLSchema/ST96/Design'
        com = 'http://www.wipo.int/standards/XMLSchema/ST96/Common'
        ET.register_namespace('dgn', dgn)
        ET.register_namespace('com', com)
        xml_count = 0
        for xml_file in xml_files:
            context = ET.iterparse(xml_file, events=('end', ))
            for event, elem in context:
                if elem.tag[0] == "{":
                    uri, tag = elem.tag[1:].split("}")
                else:
                    tag = elem.tag
                if tag == 'HagueExpressTransaction':
                    sub_output = {}
                    try:
                        regnum = elem.find(
                            '{%(dgn)s}HagueCurrent/'
                            '{%(dgn)s}HagueRegistration/'
                            '{%(com)s}InternationalRegistrationNumber' % {
                                'dgn': dgn, 'com': com}).text
                    except Exception as e:
                        try:
                            regnum = elem.find(
                                '{%(dgn)s}HagueHistory/'
                                '{%(com)s}InternationalRegistrationNumber' % {
                                    'dgn': dgn, 'com': com}).text
                            first_child = elem.find(
                                '{%(dgn)s}HagueCurrent' % {
                                    'dgn': dgn,
                                    'com': com}).getchildren(
                            )[0].tag[1:].split("}")[1]
                            self.logger.info(
                                '[%s] %s: missing HagueRegistration '
                                'under HagueCurrent. Found %s instead.' % (
                                    self.archive_name[0], regnum, first_child))
                        except Exception as e:
                            continue
                    regnum = regnum.replace('M/', '')
                    # only write the Design element
                    appxml_file = os.path.join(self.dest_dir[0], '%s.xml' % (
                        regnum))
                    self.logger.info('%s' % regnum)
                    xml_count += 1
                    with codecs.open(appxml_file, 'w', 'utf-8') as fh:
                        fh.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                        fh.write(ET.tostring(elem, 'utf-8').decode("utf-8"))
                    sub_output['appnum'] = '%s' % regnum
                    sub_output['xml'] = os.path.relpath(appxml_file,
                                                        self.dest_dir[0])
                    extraction_data.append(sub_output)
                    elem.clear()
            os.remove(xml_file)
        self.output_data = [extraction_data]
        return xml_count, 0
