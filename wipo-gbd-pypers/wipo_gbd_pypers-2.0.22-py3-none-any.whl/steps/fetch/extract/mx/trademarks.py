import os
import base64
import glob
from xml.dom.minidom import parse
from pypers.utils import xmldom
from pypers.steps.base.extract import ExtractBase


class Trademarks(ExtractBase):
    """
    Extract MXTM archive
    """
    spec = {
        "version": "2.0",
        "descr": [
            "Returns the directory with the extraction"
        ]
    }

    def add_xml_file(self, filename, fullpath):
        data_dom = parse(fullpath)
        appnum = xmldom.get_nodevalue('ApplicationNumber', dom=data_dom)
        if not appnum:
            return
        # sanitize appnum
        appnum = appnum.strip()
        self.manifest['data_files'].setdefault(appnum, {})
        self.manifest['data_files'][appnum]['ori'] = os.path.relpath(
            fullpath, self.extraction_dir
        )
        # image extraction
        img_type = xmldom.get_nodevalue('MarkImageFileFormat', dom=data_dom)
        img_data = xmldom.get_nodevalue('MarkImageBinary', dom=data_dom)

        has_img = img_type and img_data

        if has_img:
            img_dest = os.path.join(self.extraction_dir, '%s.%s' % (
                filename, img_type))
            with open(img_dest, 'wb') as fh:
                fh.write(base64.b64decode(img_data))
            self.add_img_file(appnum, img_dest)

    def process(self):
        pass