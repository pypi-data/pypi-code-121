import os
import re
import mimetypes
import codecs
import shutil
import xml.etree.ElementTree as ET
import xml.dom.minidom as md
from pypers.steps.base.extract import ExtractBase


class Trademarks(ExtractBase):
    """
    Extract WOTM archive
    """
    spec = {
        "version": "2.0",
        "descr": [
            "Returns the directory with the extraction"
        ],
    }


    # image names can be different:
    # appnum = 1234567A
    # image  = 1234567
    img_map = {}

    def file_in_archive(self, file, path):
        appnum, ext = os.path.splitext(os.path.basename(file))
        if ext.lower() == '.xml':
            self.add_xml_file(appnum, os.path.join(path, file))
        else:
            file_mime = mimetypes.guess_type(file)[0]
            if (file_mime or '').startswith('image/'):
                self.img_map[appnum] = os.path.join(path, file)

    def add_xml_file(self, _, xml_file):
        if os.environ.get('GBD_DEV_EXTRACT_LIMIT', None):
            if len(self.manifest['data_files'].keys()) >= int(
                    os.environ.get('GBD_DEV_EXTRACT_LIMIT')):
                return
        xml_dir = os.path.join(self.extraction_dir, 'xml')
        os.makedirs(xml_dir, exist_ok=True)
        ns = 'http://www.wipo.int/standards/XMLSchema/trademarks'
        ET.register_namespace('', ns)
        context = ET.iterparse(xml_file, events=('end',))
        for event, elem in context:
            if elem.tag[0] == "{":
                uri, tag = elem.tag[1:].split("}")
            else:
                tag = elem.tag

            if tag == 'TradeMark':
                appnum = elem.find('{%(ns)s}ApplicationNumber' % {
                    'ns': ns}).text
                img_path_element = elem.find('{%(ns)s}MarkImageDetails' % {
                    'ns': ns})
                img_path = None
                if img_path_element:
                    img_path = img_path_element.find('{%(ns)s}MarkImage' % {
                        'ns': ns}).find('{%(ns)s}MarkImageFilename' % {
                        'ns': ns}).text
                tmxml_file = os.path.join(xml_dir, '%s.xml' % appnum)

                with codecs.open(tmxml_file, 'w', 'utf-8') as fh:
                    fh.write(md.parseString(
                        ET.tostring(elem, 'utf-8')).toprettyxml())
                self.manifest['data_files'].setdefault(appnum, {})
                self.manifest['data_files'][appnum]['ori'] = os.path.relpath(
                    tmxml_file, self.extraction_dir
                )
                # remove trailing characters when matching images
				# 779460A -> 779460
                if img_path:
                    img_match = self.img_map.get(appnum, None)
                    if img_match:
                        img_subpath = os.path.relpath(img_match, self.extraction_dir)
                        self.manifest['img_files'].setdefault(appnum, [])
                        self.manifest['img_files'][appnum].append({
                            'ori': img_subpath})
                    else:
                        self.add_img_url(appnum, img_path)

                elem.clear()
        os.remove(xml_file)

    def process(self):
        pass
