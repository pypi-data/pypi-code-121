import os
import codecs
import xml.etree.ElementTree as ET
import xml.dom.minidom as md
from pypers.utils import xmldom
from pypers.steps.base.extract import ExtractBase
import mimetypes


class TrademarksPending(ExtractBase):
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
    counter = 0

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
        context = ET.iterparse(xml_file, events=('end',))

        for event, elem in context:
            tag = elem.tag

            if tag == 'MARKGR':
                self.counter += 1

                appnum = 'PEND%s' % (str(self.counter).zfill(6))
                img_name = elem.find('./CURRENT/IMAGE').attrib['NAME']
                tmxml_file = os.path.join(xml_dir, '%s.xml' % appnum)

                with codecs.open(tmxml_file, 'w', 'utf-8') as fh:
                    fh.write(md.parseString(
                        ET.tostring(elem, 'utf-8')).toprettyxml())

                # transform to ST66
                current_path = os.path.abspath(os.path.dirname(__file__))
                xmldom.transform(
                    tmxml_file,
                    os.path.join(current_path, 'xsl', 'wipo.romarin.gbd.xsl'),
                    tmxml_file)

                xmldom.create_element(tmxml_file, 'WO_Pending_Number', appnum)

                self.manifest['data_files'].setdefault(appnum, {})
                self.manifest['data_files'][appnum]['ori'] = os.path.relpath(
                    tmxml_file, self.extraction_dir
                )

                img_match = self.img_map.get(img_name, None)
                if img_name != '':
                    if img_match:
                        img_subpath = os.path.relpath(img_match, self.extraction_dir)
                        self.manifest['img_files'].setdefault(appnum, [])
                        self.manifest['img_files'][appnum].append({
                            'ori': img_subpath})
                    else:
                        img_name = 'https://www.wipo.int/madrid/monitor/api/v1/image/WO50%s' % img_name.zfill(
                            len('000000000000'))
                        self.add_img_url(appnum, img_name)

                elem.clear()
        os.remove(xml_file)

    def process(self):
        pass
