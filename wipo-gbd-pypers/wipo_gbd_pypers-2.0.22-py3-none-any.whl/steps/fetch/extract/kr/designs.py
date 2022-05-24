import os
import mimetypes
import shutil
from pypers.utils import xmldom
from xml.dom.minidom import parse
from pypers.steps.base.extract_step import ExtractStep


class Designs(ExtractStep):
    """
    Extract KRID archives
    """
    spec = {
        "version": "2.0",
        "descr": [
            "Returns the directory with the extraction"
        ]
    }

    def _walker(self, r, d, files, xml_files, img_map):
        for file in files:
            name, ext = os.path.splitext(file)
            path = os.path.join(r, file)
            file_mime = mimetypes.guess_type(file)[0]

            if (file_mime or '').endswith('/xml'):
                xml_files.append(path)
            elif (file_mime or '').startswith(
                    'image/') and ext.lower() != '.dwg':
                img_map[name] = path

    def get_raw_data(self):
        return self.get_xmls_files_with_path(self._walker)

    def process_xml_data(self, data):
        extraction_data = []
        img_counter_global = 0
        # get trademarks file
        xml_files = data[0]
        img_map = data[1]

        com_ns = 'http://www.wipo.int/standards/XMLSchema/ST96/Common'
        krdgn_ns = 'urn:kr:gov:doc:kipo:design'
        krcom_ns = 'urn:kr:gov:doc:kipo:common'

        for xml_file in xml_files:
            data_dom = parse(xml_file)

            header_dom = data_dom.getElementsByTagNameNS(
                krdgn_ns, 'DesignBibliographicData')[0]

            # registration number to get the source
            regnum = xmldom.get_nodevalue('RegistrationNumber',
                                          dom=header_dom, ns=com_ns)
            regnum = regnum.replace('/', '')

            appnum, _ = os.path.splitext(os.path.basename(xml_file))

            # an international application (hague)
            # normalize appnum: 3020177000340M001 -> 3020177000340-0001
            try:
                appnum.index('M')
                dsgnum = appnum[:appnum.rfind('M')] + '-' + appnum[appnum.rfind(
                    'M') + 1:].zfill(4)
            except Exception as e:
                dsgnum = '%s-0001' % appnum  # korean designs are single model
                pass

            drawings_dom = data_dom.getElementsByTagNameNS(krdgn_ns, 'Drawing')

            xml_dest = os.path.join(self.dest_dir[0], '%s.xml' % dsgnum)
            shutil.move(xml_file, xml_dest)

            sub_output = {}
            sub_output['appnum'] = dsgnum
            sub_output['xml'] = os.path.relpath(xml_dest, self.dest_dir[0])
            sub_output['img'] = []

            # get image name if any
            for idx, drawing_dom in enumerate(drawings_dom):
                img_counter = 0
                views_dom = drawing_dom.getElementsByTagNameNS(krdgn_ns, 'View')
                for idx, view_dom in enumerate(views_dom):
                    imgname = xmldom.get_nodevalue(
                        'ImageFileName', dom=view_dom, ns=com_ns)
                    imgformat = xmldom.get_nodevalue(
                        'FileFormatCategory', dom=view_dom, ns=krcom_ns)
                    # yes sometimes happens, we have a placeholder for image
                    # but doesn't really reference anything
                    # => skip
                    if not imgformat:
                        continue
                    img_match = img_map.pop(imgname, None)
                    if img_match:
                        img_counter_global += 1
                        img_counter += 1
                        _, img_ext = os.path.splitext(img_match)
                        img_dest = os.path.join(
                            self.dest_dir[0], '%s.%d%s' % (
                                dsgnum, img_counter, img_ext))
                        shutil.move(img_match, img_dest)
                        img_subpath = os.path.relpath(img_dest, self.dest_dir[0])
                        sub_output['img'].append(img_subpath)
                        self.logger.info('  - %s' % (img_subpath))
                    else:
                        self.logger.info(
                            '%s - %d: img missing (found %s) - %s ' % (
                                appnum, (idx+1), imgformat, imgname))
            extraction_data.append(sub_output)
        self.output_data = [extraction_data]
        return len(xml_files), img_counter_global
