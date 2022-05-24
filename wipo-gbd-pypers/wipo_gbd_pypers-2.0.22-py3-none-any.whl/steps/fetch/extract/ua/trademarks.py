import os
import json
import math
import codecs
import dicttoxml
from xml.dom.minidom import parseString
from pypers.steps.base.extract import ExtractBase


class Trademarks(ExtractBase):
    """
    Extract UATM marks information from api
    """
    spec = {
        "version": "2.0",
        "descr": [
            "Returns the directory with the extraction"
        ]
    }

    # unpacking a json of jsons
    # unpacks and collects
    def unpack_archive(self, archive, dest):

        # to collect img urls
        base_url = self.meta['pipeline']['input']['from_api']['url']

        with open(archive, 'r') as fh:
            marks_data = json.load(fh)

        self.logger.info('\nprocessing file: %s' % archive)

        # collect application numbers for update
        for mark in marks_data:
            # no need to keep this verbose element
            mark.pop('data_payments', None)
            appnum = mark['app_number']
            # sanitize appnum : 97314/SU -> 97314SU
            appnum = appnum.replace('/', '')

            # save data file
            mark_file = os.path.join(dest, '%s.xml' % appnum)
            mark_xml = dicttoxml.dicttoxml(
                mark, attr_type=False, custom_root='mark')

            with codecs.open(mark_file, 'w', 'utf-8') as fh:
                fh.write(parseString(mark_xml).toprettyxml())

            self.add_xml_file(appnum, mark_file)
            img_uri = (mark.get('data', {}) or {}).get('MarkImageDetails', {}).get('MarkImage', {}).get(
                'MarkImageFilename', None)
            
            if img_uri:
                img_url = base_url + img_uri
                self.add_img_url(appnum, img_url)

    def collect_files(self, dest):
        pass

    def process(self):
        pass

