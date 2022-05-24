import os
from xml.dom.minidom import parse
from pypers.utils import xmldom
from pypers.steps.base.extract_step import ExtractStep


class Designs(ExtractStep):
    """
    Extract GEID archive
    """
    spec = {
        "version": "2.0",
        "descr": [
            "Returns the directory with the extraction"
        ]
    }

    def get_raw_data(self):
        return self.get_xmls_files_with_path(self.common_walker)

    def process_xml_data(self, data):
        extraction_data = []
        xml_files = data[0]
        img_files = data[1]
        for xml_file in xml_files:
            xml_dom = parse(xml_file)

            appnum = xmldom.get_nodevalue('ApplicationNumber', dom=xml_dom)
            appuid = xmldom.get_nodevalue('DesignIdentifier',  dom=xml_dom)

            xml_dest_file = os.path.join(self.dest_dir[0], '%s.xml' % appuid)

            # rename file to match appuid.xml
            os.rename(xml_file, xml_dest_file)

            sub_output = {}
            sub_output['appnum'] = appnum
            sub_output['xml'] = os.path.relpath(xml_dest_file, self.dest_dir[0])
            sub_output['img'] = []

            imgfilenames_elts = xml_dom.getElementsByTagNameNS(
                '*', 'DesignImageFilename')
            for idx, elt in enumerate(imgfilenames_elts):
                try:
                    img_name = elt.firstChild.nodeValue
                    img_name = img_name[:img_name.index('.')]
                    img_file = img_files.get(img_name, None)
                    if not img_file:
                        continue

                    _, img_ext = os.path.splitext(img_file)
                    img_dest_name = '%s.%s%s' % (appuid, idx+1, img_ext)
                    img_dest_file = os.path.join(self.dest_dir[0],
                                                 img_dest_name)
                    os.rename(img_file, img_dest_file)

                    sub_output['img'].append(os.path.relpath(
                        img_dest_file, self.dest_dir[0]))

                    self.logger.info('%s - %s' % (appuid, img_dest_name))
                except Exception as e:
                    pass
            if not len(imgfilenames_elts):
                self.logger.info('%s - %s' % (appuid, 'no images'))
            extraction_data.append(sub_output)

        self.output_data = [extraction_data]
        return len(xml_files), len(img_files.keys())
