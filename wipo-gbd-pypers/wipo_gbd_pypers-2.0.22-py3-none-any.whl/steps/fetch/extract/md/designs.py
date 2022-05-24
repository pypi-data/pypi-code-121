import os
import re
import codecs
import xml.etree.ElementTree as ET
from pypers.steps.base.extract_step import ExtractStep
from pypers.utils import utils


class Designs(ExtractStep):
    """
    Extract MDID archives
    """
    spec = {
        "version": "2.0",
        "descr": [
            "Returns the directory with the extraction"
        ],
        "args":
        {
            "outputs": [
                {
                    "name": "del_list",
                    "descr": "del file that contains a list of application"
                             " numbers to be deleted"
                }
            ],
        }
    }

    def _get_sub_folder(self, archive):
        return self.common_get_sub_folder(archive)

    def _xml_walker(self, r, d, files, xml_files, img_map):
        for f in files:
            xml_files.append(os.path.join(r, f))

    def _img_walker(self, r, d, files, xml_files, img_map):
        self.appnum_re = re.compile(r'.*(MD\d+-\d{4}).*')
        for f in files:
            image_name = os.path.splitext(f)[0]
            image_appnum = self.appnum_re.match(image_name).group(1)
            img_map.setdefault(image_appnum, [])
            img_map[image_appnum].append(os.path.join(r, f))

    def get_raw_data(self):
        return self.get_xmls_files_with_xml_and_img_path(
            xml_walker=self._xml_walker, img_walker=self._img_walker)

    def process_xml_data(self, data):
        extraction_data = []
        xml_files = data[0]
        img_files = data[1]
        self.del_list = []
        ns = 'http://md.oami.europa.eu/schemas/design'
        ET.register_namespace('', ns)
        img_count = 0
        xml_count = 0
        for xml_file in xml_files:
            xml_count += 1
            context = ET.iterparse(xml_file, events=('end', ))
            for event, elem in context:
                if elem.tag[0] == "{":
                    uri, tag = elem.tag[1:].split("}")
                else:
                    tag = elem.tag
                if tag == 'Design':
                    sub_output = {}
                    dsgnum = elem.find(
                        '{%(ns)s}DesignIdentifier' % {'ns': ns}).text
                    appnum = self.appnum_re.match(
                        os.path.basename(xml_file)).group(1)

                    upd_mode = elem.attrib.get('operationCode', None)

                    if upd_mode == 'Delete':
                        self.del_list.append({
                            'id': 'MDID.%s' % appnum,
                            'fname': appnum,
                            'fdir': utils.appnum_to_subdirs(appnum)})

                    # only write the Design element
                    appxml_file = os.path.join(self.subfolders['xml'],
                                               '%s.xml' % (dsgnum))
                    with codecs.open(appxml_file, 'w', 'utf-8') as fh:
                        fh.write(ET.tostring(elem, 'utf-8').decode("utf-8"))

                    sub_output['appnum'] = dsgnum
                    sub_output['xml'] = os.path.relpath(appxml_file,
                                                        self.dest_dir[0])
                    sub_output['img'] = []
                    self.logger.info('%s' % dsgnum)
                    for idx, img_file in enumerate(
                            sorted(img_files.pop(appnum, []))):
                        self.logger.info('  %s: %s' % (idx+1, img_file))
                        # the image has been processed in a parallel extraction
                        # good enough !
                        if not os.path.exists(img_file):
                            continue
                        _, img_ext = os.path.splitext(img_file)
                        img_dest_name = '%s.%s%s' % (dsgnum, idx+1, img_ext)
                        img_dest_file = os.path.join(self.subfolders['img'],
                                                     img_dest_name)
                        os.rename(img_file, img_dest_file)
                        img_count += 1
                        sub_output['img'].append(os.path.relpath(
                            img_dest_file, self.dest_dir[0]))
                    extraction_data.append(sub_output)
                    elem.clear()
            os.remove(xml_file)
        self.output_data = [extraction_data]
        return xml_count, img_count
