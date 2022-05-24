import os
import json
import math
import codecs
import dicttoxml
from xml.dom.minidom import parseString
from pypers.steps.base.extract import ExtractBase
from pypers.utils import utils


class Trademarks(ExtractBase):
    """
    Extract ISTM marks information from api
    """
    spec = {
        "version": "0.2",
        "descr": [
            "Returns the directory with the extraction"
        ],
        "args":
        {
            "inputs": [
                {
                    "name": "input_json",
                    "type": "file",
                    "descr": "the xmls to extract",
                    "iterable": True
                }
            ]
        }
    }

    def preprocess(self):
        self.data_files = {}
        self.img_files = {}
        self.media_files = {}
        # self.archives is a tuple of (date, file)

        if not len(self.input_json):
            return

        archive = os.path.basename(self.input_json)
        extraction_date = archive.split(".TO.")[1]
        archive_name = archive

        # prepare destination dir under pipeline scratch dir
        self.extraction_dir = os.path.join(
            self.meta['pipeline']['output_dir'],
            '__scratch',
            extraction_date,
            archive_name
        )

        # deletes the directory if prev exists
        utils.mkdir_force(self.extraction_dir)

        self.manifest = { 'archive_name': archive_name,
                          'archive_file': archive,
                          'archive_date': extraction_date,
                          'extraction_dir': self.extraction_dir,
                          'data_files': {},
                          'img_files': {},
                          'media_files': {}}
        # getting files from their api
        # extracting information from the json file
        with open(self.input_json, 'r') as fh:
            lines = fh.readlines()
            # remove those start-of-text and end-of-text bytes
            lines = [line.replace('\\u0002', '').replace('\\u0003', '').strip() for line in lines]
            marks_data = json.loads(''.join(lines))
        
        self.logger.info('\nprocessing file: %s' % self.input_json)
        count = 0
        # collect application numbers for update
        for mark in marks_data:
            # very few files have this bug in istm
            # we skip them
            appnum = mark['vmid']

            if mark['applicationNumber'] == '0':
                self.logger.info('vmid %s - has no application'
                                 ' number - skipping' % appnum)
                continue
            img_uri = (mark.get(
                'orginalImagePath', mark.get(
                    'imagePath', '')) or '').strip()

            self.logger.info('vmid %s - %s' % (appnum, img_uri))
            sub_dir = str(int(math.ceil(count / 10000 + 1))).zfill(5)
            dest_sub_dir = os.path.join(self.extraction_dir, sub_dir)
            if not os.path.exists(dest_sub_dir):
                os.makedirs(dest_sub_dir)

            mark_file = os.path.join(dest_sub_dir, '%s.xml' % appnum)

            mark_xml = dicttoxml.dicttoxml(
                mark, attr_type=False, custom_root='mark')

            # with open(mark_file, 'w') as fh:
            with codecs.open(mark_file, 'w', 'utf-8') as fh:
                fh.write(parseString(mark_xml).toprettyxml())
            self.add_xml_file(appnum, mark_file)

            if not img_uri == '':
                self.add_img_url(appnum, img_uri)
            count += 1
        os.remove(self.input_json)

    def process(self):
        pass
