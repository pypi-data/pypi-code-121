import os
import urllib
import requests
import codecs
import math
import xml.etree.ElementTree as ET
from pypers.utils import utils
from pypers.utils import xmldom
from pypers.steps.base.extract import ExtractBase
from pypers.core.interfaces.db import get_pre_prod_db
from pypers.core.interfaces.storage import get_storage
from pypers.core.interfaces.config.pypers_storage import RAW_DOCUMENTS

class Trademarks(ExtractBase):
    """
    Extract USTM archive
    """
    spec = {
        "version": "2.0",
        "descr": [
            "Returns the directory with the extraction"
        ],
        "args":
        {
            "inputs": [
                {
                    "name": "img_ref_dir",
                    "descr": "the directory that contains previous extractions,"
                             "for looking at images that are referenced in the"
                             "mark files but not present in the archive",
                    "value": "/data/brands/collections/ustm"
                }
            ]
        }
    }

    def preprocess(self):
        self.data_files = {}
        self.img_files = {}
        self.media_files = {}
        self.manifest = {}
        # self.archives is a tuple of (date, {archive_name: xxx, archives[]})

        if not len(self.archives):
            return

        extraction_date = self.archives[0]
        archive_name = self.archives[1]['name']
        archives = self.archives[1]['archives']
        # prepare destination dir under pipeline scratch dir
        self.extraction_dir = os.path.join(
            self.meta['pipeline']['output_dir'],
            '__scratch',
            extraction_date,
            archive_name
        )

        # deletes the directory if prev exists
        utils.mkdir_force(self.extraction_dir)
        self.xml_count = 0
        self.manifest = {'archive_name': archive_name,
                         'archive_file': archive_name,
                         'archive_date': extraction_date,
                         'extraction_dir': self.extraction_dir,
                         'data_files': {},
                         'img_files': {},
                         'media_files': {}}
        # Get images first
        for archive in sorted(archives, reverse=True):
            self.collect_files(self.unpack_archive(archive, self.extraction_dir))

    def add_img_file(self, appnum, fullpath):
        if os.environ.get('GBD_DEV_EXTRACT_LIMIT', None):
            if len(self.manifest['img_files'].keys()) >= int(
                    os.environ.get('GBD_DEV_EXTRACT_LIMIT')):
                return

        path = os.path.relpath(fullpath, self.extraction_dir)

        self.img_files.setdefault(appnum, [])
        self.img_files[appnum].append(
            {'ori': path}
        )

    def add_xml_file(self, filename, fullpath):
        self.logger.info('\nprocessing file: %s' % filename)
        context = ET.iterparse(fullpath, events=('end', ))
        for event, elem in context:
            if event == 'end' and elem.tag == 'case-file':
                self.xml_count += 1
                try:
                    appnum = elem.find('serial-number').text
                except Exception as e:
                    continue

                drawcode = elem.find(
                    'case-file-header').find('mark-drawing-code').text

                # 1000 in a dir
                xml_subdir = str(int(
                    math.ceil(self.xml_count/1000 + 1))).zfill(4)

                xml_dest = os.path.join(self.extraction_dir, xml_subdir)
                tmxml_file = os.path.join(xml_dest, '%s.xml' % appnum)
                if not os.path.exists(xml_dest):
                    os.makedirs(xml_dest)

                with codecs.open(tmxml_file, 'w', 'utf-8') as fh:
                    fh.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
                    fh.write(ET.tostring(elem).decode('utf-8'))

                # compress the ustm tm application file
                current_path = os.path.abspath(os.path.dirname(__file__))
                xmldom.transform(
                    tmxml_file,
                    os.path.join(current_path, 'ustm-compress.xsl'),
                    tmxml_file)

                # use pop to remove what we find
                img_match = self.img_files.pop(appnum, None)
                if img_match:
                    self.manifest['img_files'].setdefault(appnum, [])
                    self.manifest['img_files'][appnum] = img_match
                    self.logger.info("Found image in archive for %s" % appnum)
                else:
                    if drawcode and drawcode[:1] not in ['1', '4', '6']:
                        img_uri = 'http://tsdr.uspto.gov/img/%s/large' % appnum
                        self.add_img_url(appnum, img_uri)
                self.manifest['data_files'].setdefault(appnum, {})
                self.manifest['data_files'][appnum]['ori'] = os.path.relpath(
                    tmxml_file, self.extraction_dir
                )
                elem.clear()
        os.remove(fullpath)

    def to_st13(self, appnum):
        # The only way to deduce the st13 without the date is to query partial st13 and office from solr
        solr_url = os.environ.get('SLRW_URL')
        if solr_url.endswith('/'):
            solr_url = solr_url[0:len(solr_url)-1]
        params = {
            'fl': 'st13',
            'indent': 'true',
            'wt': 'csv',
            'q.op': 'AND',
            'q': 'office:US applicationNumberSynonyms:%s' % appnum
        }

        url = "%s/brand/select?%s" % (solr_url, urllib.parse.urlencode(params))
        with requests.session() as session:
            page = session.get(url)
            content = page.content.decode('UTF-8')
            lines = content.split('\n')[1:]
            for line in lines:
                if line != '':
                    return line
            return None

    def process(self):
        # see what else we have in the img_map
        # these are updated images without their xml
        for imgname in self.img_files.keys():
            appnum = self.to_st13(imgname)
            if not appnum:
                continue
            # get the archive name from dynamo
            doc_meta = get_pre_prod_db().get_document(appnum)
            if not doc_meta:
                continue
            archive_name = doc_meta.get('archive', None)
            if not archive_name:
                continue

            # get the file name from s3
            ori_doc_path = os.path.join(RAW_DOCUMENTS,
                                        'brands',
                                        'ustm',
                                        archive_name,
                                        "%s.xml" % appnum)
            xml_subdir = str(int(
                math.ceil(self.xml_count / 1000 + 1))).zfill(4)
            xml_dest = os.path.join(self.extraction_dir, xml_subdir)
            if not os.path.exists(xml_dest):
                os.makedirs(xml_dest)
            self.xml_count += 1
            tmxml_file = os.path.join(xml_dest, '%s.xml' % appnum)
            self.logger.info('xml with updated image %s' % tmxml_file)
            get_storage().get_file(ori_doc_path, tmxml_file)
            self.manifest['img_files'].setdefault(appnum, [])
            self.manifest['img_files'][appnum] = self.img_files[imgname]
            self.manifest['data_files'].setdefault(appnum, {})
            self.manifest['data_files'][appnum]['ori'] = os.path.relpath(
                tmxml_file, self.extraction_dir
            )
