import os
import mimetypes
from pypers.steps.base.extract import ExtractBase

class Trademarks(ExtractBase):
    """
    Extract IPAS archive
    """
    spec = {
        "version": "2.0",
        "descr": [
            "Returns the directory with the extraction"
        ]
    }

    def file_in_archive(self, file, path, archive_name=None):
        fname, ext = os.path.splitext(os.path.basename(file))
        # path: <archive>/KHM01368334/
        # file: KHM01368334_biblio.xml
        if ext.lower() == '.xml':
            appnum = os.path.basename(path)
            self.add_xml_file(appnum, os.path.join(path, file))

        # path: <archive>/KHM01368334/ATTACHMENT/
        # file: logo.jpeg
        else:
            # get appnum
            file_mime = mimetypes.guess_type(file)[0]
            if (file_mime or '').startswith('image/'):
                appnum = os.path.basename(os.path.dirname(path))
                self.add_img_file(appnum, os.path.join(path, file))
            elif (file_mime or '').startswith('video/'):
                appnum = os.path.basename(os.path.dirname(path))
                self.add_video_file(appnum, os.path.join(path, file))
            elif file_mime == 'application/zip':
                self.archive_in_archive(file, path)

    def add_video_file(self, appnum, fullpath):
        pass

    def process(self):
        pass
