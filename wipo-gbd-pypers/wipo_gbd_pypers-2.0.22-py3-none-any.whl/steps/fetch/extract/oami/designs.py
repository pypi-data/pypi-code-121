import os
from xml.dom.minidom import parse
from pypers.utils import xmldom
from pypers.steps.base.extract_step import ExtractStep


class Designs(ExtractStep):
    """
    Extract OAMI ID archives
    """
    spec = {
        "version": "2.0",
        "descr": [
            "Returns the directory with the extraction"
        ]
    }

    def _get_sub_folder(self, archive):
        return self.common_get_sub_folder(archive)

    def _xml_walker(self, r, d, files, xml_files, img_map):
        for f in files:
            if f.endswith('700000000000000.xml'):
                continue  # empty file
            xml_files.append(os.path.join(r, f))

    def _img_walker(self, r, d, files, xml_files, img_map):
        for f in files:
            image_name = os.path.splitext(f)[0]
            if self.meta['pipeline']['collection'] == "peid":
                image_name = image_name[image_name.find('PE'):]
            img_map[image_name] = os.path.join(r, f)

    def get_raw_data(self):
        return self.get_xmls_files_with_xml_and_img_path(
            xml_walker=self._xml_walker, img_walker=self._img_walker)

    def process_xml_data(self, data):
        extraction_data = []
        xml_files = data[0]
        img_map = data[1]
        img_counter = 0
        for xml_file in xml_files:
            xml_dom = parse(xml_file)
            appnum = xmldom.get_nodevalue('ApplicationNumber', dom=xml_dom)
            # sanitize appnum : S/123(8) -> S123-8
            appnum = appnum.replace(
                '/', '').replace('-', '').replace('(', '-').replace(')', '')

            sub_output = {}
            sub_output['appnum'] = appnum
            sub_output['xml'] = os.path.relpath(xml_file, self.dest_dir[0])
            sub_output['img'] = []
            imgfilenames_elts = xml_dom.getElementsByTagNameNS(
                '*', 'DesignImageFilename')
            for idx, elt in enumerate(imgfilenames_elts):
                img_name = elt.firstChild.nodeValue
                img_name = img_name[:img_name.index('.')]
                img_file = img_map.get(img_name, None)
                if not img_file:
                    continue
                img_counter += 1
                _, img_ext = os.path.splitext(img_file)
                img_dest_name = '%s-%s.%s%s' % (appnum, '0001', idx+1, img_ext)
                img_dest_file = os.path.join(self.dest_dir[0], img_dest_name)
                os.rename(img_file, img_dest_file)

                sub_output['img'].append(os.path.relpath(
                    img_dest_file, self.dest_dir[0]))
                self.logger.info('  - %s' % (img_dest_name))
            extraction_data.append(sub_output)
        self.output_data = [extraction_data]
        return len(xml_files), img_counter
