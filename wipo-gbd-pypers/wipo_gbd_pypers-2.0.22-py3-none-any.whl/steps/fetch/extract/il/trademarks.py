import os
import math
import codecs
import xml.etree.ElementTree as ET
import xml.dom.minidom as md
from pypers.utils.xmldom import clean_xmlfile
from pypers.utils import utils
from pypers.steps.base.extract import ExtractBase


class Trademarks(ExtractBase):
    """
    Extract ILTM archives
    """
    spec = {
        "version": "2.0",
        "descr": [
            "Returns the directory with the extraction"
        ]
    }

    def preprocess(self):
        self.data_files = {}
        self.img_files = {}
        self.media_files = {}
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

        self.manifest = {'archive_name': archive_name,
                         'archive_file': archive_name,
                         'archive_date': extraction_date,
                         'extraction_dir': self.extraction_dir,
                         'data_files': {},
                         'img_files': {},
                         'media_files': {}}

        for archive in sorted(archives):
            self.collect_files(self.unpack_archive(archive, self.extraction_dir))

    def add_img_file(self, appnum, fullpath):
        if os.environ.get('GBD_DEV_EXTRACT_LIMIT', None):
            if len(self.manifest['img_files'].keys()) >= int(
                    os.environ.get('GBD_DEV_EXTRACT_LIMIT')):
                return

        path = os.path.relpath(fullpath, self.extraction_dir)
        self.img_files[appnum] = path

    def process(self):
        pass

    def add_xml_file(self, filename, fullpath):
        xml_count = 0
        self.logger.info('\nprocessing file: %s' % filename)
        context = ET.iterparse(fullpath, events=('end', ))
        for event, elem in context:
            tag = elem.tag
            if tag == 'TMBRAND':
                xml_count += 1
                sub_output = {}
                appnum = elem.find('DETAILS/OFFICENUMBER').text
                appnum = appnum.zfill(4)
                sub_output['appnum'] = appnum

                # 1000 in a dir
                xml_subdir = str(int(math.ceil(
                    xml_count/1000 + 1))).zfill(4)
                tmxml_dest = os.path.join(self.extraction_dir,
                                          xml_subdir)
                tmxml_file = os.path.join(tmxml_dest, '%s.xml' % appnum)
                if not os.path.exists(tmxml_dest):
                    os.makedirs(tmxml_dest)

                with codecs.open(tmxml_file, 'w', 'utf-8') as fh:
                    fh.write(md.parseString(
                        ET.tostring(elem, 'utf-8')).toprettyxml())
                clean_xmlfile(tmxml_file, overwrite=True)
                # now find the image
                img_tag = elem.find('IMAGEFILE').text
                if img_tag:
                    # grrr windows path sep
                    img_tag = img_tag.replace('\\', '/')
                    img_tag = os.path.basename(img_tag)
                    # incase it was present without an extention. happens!
                    img_tag = '%s.' % img_tag
                    img_name = img_tag[0:img_tag.index('.')]
                    img_file = self.img_files.get(img_name)
                    if img_file:
                        self.manifest['img_files'].setdefault(appnum, [])
                        self.manifest['img_files'][appnum].append(
                            {'ori': img_file}
                        )
                    else:
                        self.logger.info('%s - %s' % (
                            appnum, 'err [%s]' % img_name))
                else:
                    self.logger.info('%s - %s' % (appnum, ''))
                self.manifest['data_files'].setdefault(appnum, {})
                self.manifest['data_files'][appnum]['ori'] = os.path.relpath(
                    tmxml_file, self.extraction_dir
                )
        # remove the file when done with it
        os.remove(fullpath)
