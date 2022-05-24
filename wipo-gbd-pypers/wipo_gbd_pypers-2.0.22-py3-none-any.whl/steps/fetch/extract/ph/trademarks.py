import os
import math
import subprocess
from pypers.utils import utils
import xml.etree.ElementTree as ET
import xml.dom.minidom as md
from pypers.utils.xmldom import clean_xmlfile
from pypers.utils.utils import which
from pypers.steps.base.extract import ExtractBase


class Trademarks(ExtractBase):
    """
    Extract PHTM archives
    """
    spec = {
        "version": "2.0",
        "descr": [
            "Returns the directory with the extraction"
        ]
    }


    def preprocess(self):
        self.counter_xml = 0
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
        rars = [rar for rar in archives
                if rar.lower().endswith('.rar')]
        md5s = [md5 for md5 in archives
                if md5.lower().endswith('.md5')]

        #self._validate_archive(rars, md5s)
        self.manifest = {'archive_name': archive_name,
                         'archive_file': archive_name,
                         'archive_date': extraction_date,
                         'extraction_dir': self.extraction_dir,
                         'data_files': {},
                         'img_files': {},
                         'media_files': {}}
        for archive in rars:
            self.collect_files(self.unpack_archive(archive, os.path.join(self.extraction_dir, os.path.basename(archive))))

    def _validate_archive(self, rars, md5s):
        # validating rars with their md5
        # the input is sorted, so the order of zip is guaranteed
        for executable in ['md5sum', 'md5']:
            cmd_prefix = which(executable)
            if cmd_prefix:
                break

        for md5, rar in zip(md5s, rars):
            # calculating checksum on our side
            cmd = [cmd_prefix, rar]
            proc = subprocess.Popen(cmd,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
            stdout, stderr = proc.communicate()
            rc = proc.returncode
            if rc != 0:
                raise Exception('Could not create md5sum for %s. '
                                'Something is wrong' % rar)

            checksum_calc = stdout.decode('utf-8').split(' ')[0].lower()
            # compare it with checksum we got
            with open(md5, 'r') as fh:
                checksum_orig = fh.read().rstrip().lower()
                print(checksum_calc)
                print(checksum_orig)

                if not checksum_calc == checksum_orig:
                    raise Exception('Checksum does not check '
                                    'for file [%s]. Aborting.' % rar)

    def add_xml_file(self, filename, fullpath):
        self.logger.info('\nprocessing file: %s' % (filename))
        clean_xmlfile(fullpath, readenc='utf-16le',
                      writeenc='utf-8', overwrite=True)

        # sometimes it happens that we get
        # an empty update. ex: 20151225
        with open(fullpath, 'r') as fh:
            lines = fh.readlines()
            if len(lines) < 1:
                return
        context = ET.iterparse(fullpath, events=('end', ))
        for event, elem in context:
            tag = elem.tag
            if tag == 'RECORD':
                self.counter_xml += 1
                appnum = elem.find('APPNO').text
                # sanitize appnum : S/123(8) -> S123-8
                appnum = appnum.replace(
                    '/', '').replace(
                    '-', '').replace(
                    '(', '-').replace(
                    ')', '')

                # 1000 in a dir
                xml_subdir = str(int(math.ceil(
                    self.counter_xml/1000 + 1))).zfill(4)
                tmxml_dest = os.path.join(self.extraction_dir, xml_subdir)
                tmxml_file = os.path.join(tmxml_dest, '%s.xml' % appnum)
                if not os.path.exists(tmxml_dest):
                    os.makedirs(tmxml_dest)

                with open(tmxml_file, 'wb') as fh:
                    fh.write(md.parseString(ET.tostring(
                        elem, encoding='utf-8')).toprettyxml(
                        encoding='utf-8'))

                # now find the image
                """
                img_tag = None
                if elem.find('LOGO/LOGO') is not None:
                    img_tag = elem.find('LOGO/LOGO').text
                    if img_tag:
                        # incase it was present without an
                        # extention. happens!
                        img_tag = '%s.' % img_tag
                        img_name = img_tag[0:img_tag.index('.')]
                        img_file = img_map.get(img_name)
                        if img_file:
                            img_count += 1
                            sub_output['img'] = os.path.relpath(
                                img_file, self.dest_dir[0])
                """
                elem.clear()
                self.manifest['data_files'].setdefault(appnum, {})
                self.manifest['data_files'][appnum]['ori'] = os.path.relpath(
                    tmxml_file, self.extraction_dir
                )
        # remove the file when done with it
        os.remove(fullpath)


    def process(self):
        pass

