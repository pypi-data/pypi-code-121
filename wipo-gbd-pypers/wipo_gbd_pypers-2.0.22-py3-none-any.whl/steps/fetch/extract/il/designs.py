import os
import mimetypes
import codecs
import xml.etree.ElementTree as ET
from pypers.utils.xmldom import clean_xmlfile
from pypers.steps.base.extract_step import ExtractStep


class Designs(ExtractStep):
    """
    Extract ILID archive
    """
    spec = {
        "version": "2.0",
        "descr": [
            "Returns the directory with the extraction"
        ]
    }

    def _walker(self, r, d, files, xml_files, img_files):
        # skip application images -- not necessary
        for file in files:
            name, ext = os.path.splitext(file)
            path = os.path.join(r, file)
            if ext == '.xml':
                xml_files.append(path)
            else:  # not an xml, then most probably image
                file_mime = mimetypes.guess_type(file)[0]
                if (file_mime or '').startswith('image/'):
                    name = name[name.rfind('\\') + 1:]
                    num = name[0:name.find('_')]
                    img_files.setdefault(num, [])
                    img_files[num].append(path)

    def get_raw_data(self):
        return self.get_xmls_files_with_path(self._walker)

    def process_xml_data(self, data):
        extraction_data = []
        xml_files = data[0]
        img_files = data[1]
        xml_count = 0
        img_count = 0

        for xml_file in xml_files:
            clean_xmlfile(xml_file, overwrite=True)

            namespaces = {
                "com": "http://www.wipo.int/standards/XMLSchema/ST96/Common",
                "dgn": "http://www.wipo.int/standards/XMLSchema/ST96/Design"
            }
            for key, val in namespaces.items():
                ET.register_namespace(key, val)

            context = ET.iterparse(xml_file, events=('end', ))

            for event, elem in context:
                if elem.tag == '{http://www.wipo.int/standards/XMLSchema/' \
                               'ST96/Design}DesignApplication':
                    xml_count += 1
                    dsgnum = elem.find('*/com:ApplicationNumberText',
                                       namespaces).text
                    design_name = "%s.xml" % dsgnum
                    design_file = os.path.join(self.dest_dir[0], design_name)
                    with codecs.open(design_file, 'wb', 'utf-8') as fh:
                        fh.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
                        fh.write(ET.tostring(elem, 'utf-8').decode("utf-8"))

                    sub_output = {}
                    sub_output['appnum'] = "%s-0001" % dsgnum
                    sub_output['xml'] = os.path.relpath(design_file,
                                                        self.dest_dir[0])
                    sub_output['img'] = []

                    self.logger.info(dsgnum)
                    for idx, img_file in enumerate(sorted(
                            img_files.pop(dsgnum, []))):
                        img_count += 1

                        self.logger.info('  %s: %s' % (idx+1, img_file))

                        _, img_ext = os.path.splitext(img_file)
                        img_dest_name = '%s-0001.%s%s' % (
                            dsgnum, idx+1, img_ext)
                        img_dest_file = os.path.join(self.dest_dir[0],
                                                     img_dest_name)
                        os.rename(img_file, img_dest_file)

                        sub_output['img'].append(
                            os.path.relpath(img_dest_file, self.dest_dir[0]))

                    extraction_data.append(sub_output)
                    elem.clear()
            # done with it
            os.remove(xml_file)
        self.output_data = [extraction_data]
        return xml_count, img_count
