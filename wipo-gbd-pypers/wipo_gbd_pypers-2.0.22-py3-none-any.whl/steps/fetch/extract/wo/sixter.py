import os
import re
import mimetypes
import shutil
from pypers.utils.xmldom import clean_xmlfile
from pypers.steps.base.extract import ExtractBase


class ArticleSixter(ExtractBase):
    """
    Extract 6ter_XML archive
    """
    spec = {
        "version": "2.0",
        "descr": [
            "Returns the directory with the extraction"
        ]
    }

    def file_in_archive(self, file, path):
        # data file in data archive
        if file.lower().endswith('.xml'):
            if file.lower().startswith('6ter'):
                return
            self._add_xml_file(file, path)
        file_mime = mimetypes.guess_type(file)[0]
        if (file_mime or '').startswith('image/'):
            if 'THUMB' in path:
                return
            self._add_img_file(file, path)

    # identify app num from image name
    def _add_img_file(self, file, path):
        # translate file name to appnum
        nb_without_padding = ''.join(re.findall(r'\d+', file))
        nb_with_padding = nb_without_padding
        while len(nb_with_padding) < 4:
            nb_with_padding = '0' + nb_with_padding
        appnum = file.replace(nb_without_padding, nb_with_padding).split('.')[0]
        # Move each file to it's own folder to avoid errors when organizing the same image with different names
        copy_path = os.path.join(path, appnum)
        os.makedirs(copy_path, exist_ok=True)
        shutil.move(os.path.join(path, file), os.path.join(copy_path, file))
        self.add_img_file(appnum, os.path.join(copy_path, file))

    # xml of xmls => split to files
    def _add_xml_file(self, file, path):
        appnum = file.split('.')[0]
        clean_xmlfile(os.path.join(path, file), overwrite=True, readenc='ISO-8859-1')
        self.add_xml_file(appnum, os.path.join(path, file))


    def process(self):
        pass
