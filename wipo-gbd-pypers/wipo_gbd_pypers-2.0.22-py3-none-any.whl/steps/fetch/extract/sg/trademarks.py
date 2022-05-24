import os
import re
import mimetypes
import codecs
import xml.etree.ElementTree as ET
from pypers.utils import utils
from pypers.steps.base.extract import ExtractBase


class Trademarks(ExtractBase):
    """
    Extract SGTM archive
    """
    spec = {
        "version": "2.0",
        "descr": [
            "Returns the directory with the extraction"
        ]
    }

    ignore_imgs = []

    def file_in_archive(self, file, path):
        fname, ext = os.path.splitext(os.path.basename(file))
        if ext.lower() == '.xml':
            self._add_xml_file(fname, os.path.join(path, file))
        else:
            file_mime = mimetypes.guess_type(file)[0]
            if (file_mime or '').startswith('image/'):
                self._add_img_file(fname, os.path.join(path, file))
            elif file_mime == 'application/zip':
                self.archive_in_archive(file, path)

    # identify app num from image name
    def _add_img_file(self, file, path):
        fname, ext = os.path.splitext(os.path.basename(file))
        self.add_img_file(fname, path)

    # xml of xmls => split to files
    def _add_xml_file(self, file, xml_file):
        path = os.path.dirname(xml_file)
        context = ET.iterparse(xml_file, events=('end',))
        self.logger.info('processing %s\n' % xml_file)

        for event, elem in context:
            tag = elem.tag
            if not (tag == 'Article6ter' or
                    tag == 'Trademark' or
                    tag == 'R13'):
                continue

            appnum_tag = {
                'Article6ter': 'article_6ter_no',
                'Trademark': 'tm_no',
                'R13': 'r13_no'}
            appnum_suf = {
                'Article6ter': '6TER',
                'Trademark': 'TM',
                'R13': 'R13'}

            appnum = '%s-%s' % (elem.find(appnum_tag[tag]).text,
                                appnum_suf[tag])
            appxml_path = utils.appnum_to_dirs(path, appnum)
            appxml_file = os.path.join(appxml_path, '%s.xml' % appnum)

            try:
                os.makedirs(appxml_path)
            except:
                pass

            with codecs.open(appxml_file, 'w', 'utf-8') as fh:
                fh.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
                fh.write(ET.tostring(elem).decode("utf-8"))

            self._clean_file(appxml_file)

            is_trademark = tag == 'Trademark'
            is_r13 = tag == 'R13'
            is_6ter = tag == 'Article6ter'

            # skip trademarks with appnum starting with L
            # -- these are duplicates of R13
            if is_trademark and appnum.startswith('L'):
                self.logger.debug('skip trademark as a slogan. will have R13')
                continue
            # skip trademarks with appnum starting with A
            # -- these are duplicates of Article6ter
            if is_trademark and appnum.startswith('A'):
                self.logger.debug('skip trademark as a slogan. will have R13')
                continue

            # check if it has an image
            try:
                img_tag = elem.find('logo_details/file_name').text
                img_name, ext = os.path.splitext(img_tag)
                if is_trademark and ext.lower() == '.tif':
                    description = elem.find('mark_index/device_description')
                    if description:
                        description = description.text
                    words = elem.find('mark_description').text
                    if not description and words:
                        self.logger.info('%s: %s - ignoring because of tif' % (
                            tag.upper(), appnum))
                        self.ignore_imgs.append(appnum)
            except Exception as e:
                self.logger.info('%s: %s ' % (appnum, e))
            self.add_xml_file(appnum, os.path.join(self.extraction_dir, appxml_file))
        os.remove(xml_file)  # done with it, don't keep it

    def _clean_file(self, file):
        # arghh - solve the double escaping of entitities
        with open(file, 'r+') as f:
            content = f.read()
            f.seek(0)
            content = re.sub(r'&amp;([a-z]+;)', r'&\1', content)
            content = re.sub(r'&nbsp;', r'&#160;', content)
            content = re.sub(r'&gcaron;', 'G', content)
            f.write(content)
            f.truncate()

    def process(self):
        if not self.manifest['img_files']:
            return
        keys = list(self.manifest['img_files'].keys())
        for img in keys:
            appnum = "%s-TM" % img
            if appnum in self.ignore_imgs:
                self.manifest['img_files'].pop(img, None)
