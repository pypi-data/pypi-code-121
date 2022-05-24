import os
import re
import mimetypes
from pypers.steps.base.extract import ExtractBase


class Trademarks(ExtractBase):
    """
    Extract PETM archives
    """
    spec = {
        "version": "2.0",
        "descr": [
            "Returns the directory with the extraction"
        ],
        "args":
        {
            "params": [{
                "name": "dest_img",
                "descr": "the destination dir of the extractionfor images",
                "value": "/data/scratch/petm-imgs"}
            ]
        }
    }
    def file_in_archive(self, file, path):
        self.appnum_re = re.compile(r'.*(PE\d+[A-Z]*\d+).*')
        appnum, ext = os.path.splitext(os.path.basename(file))
        appnum = self.appnum_re.match(appnum).group(1)
        if ext.lower() == '.xml':
            self.add_xml_file(appnum, os.path.join(path, file))
        else:
            file_mime = mimetypes.guess_type(file)[0]
            if (file_mime or '').startswith('image/'):
                self.add_img_file(appnum, os.path.join(path, file))
            elif file_mime == 'application/zip':
                self.archive_in_archive(file, path)


    def process(self):
        pass