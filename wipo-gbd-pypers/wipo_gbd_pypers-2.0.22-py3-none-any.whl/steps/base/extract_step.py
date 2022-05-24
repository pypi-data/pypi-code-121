import os
from requests.auth import HTTPBasicAuth
import mimetypes
import re
from pypers.utils.archive_dates import ArchiveDateManagement
from pypers.core.step import FunctionStep
from pypers.steps.base import merge_spec_dict
from pypers.utils import utils
from datetime import datetime

class ExtractStep(FunctionStep):
    base_spec = {
        "args": {
            "inputs": [
                {
                    "name": "input_archive",
                    "type": "file",
                    "descr": "the archives to extract",
                    "iterable": True
                }
            ],
            "outputs": [
                {
                    "name": "output_data",
                    "descr": "the extracted data organized by appnum"
                },
                {
                    "name": "archive_name",
                    "descr": "the name of the archive that has been extracted"
                },
                {
                    "name": "archive_time",
                    "descr": "the office extract time of the archive that has been extracted"
                },
                {
                    "name": "dest_dir",
                    "descr": "the destination dir of the extraction"
                }
            ],
            "params": [
                {
                    "name": "archive_time_regex",
                    "type": "str",
                    "descr": "the archives time",
                    "value": ".*"
                }
            ]
        }
    }

    def common_get_sub_folder(self, archive):
        archive_name = os.path.basename(archive)
        try:
            # is it the IMG archive ?
            archive_name.index('IMG')
            return 'img'
        except Exception as e:
            return 'xml'

    def __init__(self, *args, **kwargs):
        merge_spec_dict(self.spec, self.base_spec)
        self.bad_files = []
        super(ExtractStep, self).__init__(*args, **kwargs)
        self.logger = self.log

    def common_walker(self, r, d, files, xml_files, img_files):
        # skip application images -- not necessary
        for file in files:
            name, ext = os.path.splitext(file)
            path = os.path.join(r, file)
            if ext.lower() == '.xml':
                xml_files.append(path)
            else:  # not an xml, then most probably image
                file_mime = mimetypes.guess_type(file)[0]
                if (file_mime or '').startswith('image/'):
                    img_files[name] = path

    def prepare_extract_output(self, xml_count, img_count):
        self.logger.info('\n\n')
        self.logger.info('> found %s xml files' % xml_count)
        self.logger.info('> found %s img files' % img_count)

    def get_connection_params(self, fetch_input=None):
        proxy_params = {
            'http': self.meta['pipeline']['input'].get('http_proxy', None),
            'https': self.meta['pipeline']['input'].get('https_proxy', None)
        }
        if fetch_input is None:
            return proxy_params
        fetch_from = self.meta['pipeline']['input']
        conn_params = fetch_from[fetch_input]
        auth = HTTPBasicAuth(conn_params.get('credentials', {}).get('user', ''),
                             conn_params.get('credentials', {}).get('password',
                                                                    ''))
        self.conn_params = conn_params
        return proxy_params, auth

    def get_path(self):
        if len(self.input_archive) == 0:
            return None, None, None
        archive_uid = next(iter(self.input_archive))
        archive_path = self.input_archive[archive_uid]
        archive_name = os.path.basename(archive_path)
        self.archive_name = [archive_uid]
        dest_dir = os.path.join(
            self.output_dir,
            archive_uid
        )
        self.dest_dir = [dest_dir]
        os.makedirs(dest_dir)
        self.logger.info('%s > %s' % (archive_name, dest_dir))
        return archive_uid, archive_path, archive_name

    def get_extracted_files(self):
        if len(self.input_archive) == 0:
            return
        archive_uid = next(iter(self.input_archive))
        dest_dir = os.path.join(self.output_dir, archive_uid)
        self.dest_dir = [dest_dir]
        self.archive_name = [archive_uid]
        os.makedirs(dest_dir)
        for type in ['xml', 'img']:
            os.makedirs(os.path.join(self.dest_dir[0], type))
        for archive in self.input_archive[archive_uid]:
            archive_name = os.path.basename(archive)
            if archive.lower() == '.7z':
                utils.sevenzextract(archive, dest_dir)
            else:
                utils.zipextract(archive, dest_dir)
            self.logger.info('%s > %s' % (archive_name, dest_dir))

    def get_xmls_files_from_list(self, file_walker=None):
        if len(self.input_archive) == 0:
            return [], {}
        archive_uid = os.path.basename(self.input_archive)
        archive_uid, ext = os.path.splitext(archive_uid)
        dest_dir = os.path.join(self.output_dir, archive_uid)
        self.dest_dir = [dest_dir]
        self.archive_name = [archive_uid]
        os.makedirs(dest_dir)
        utils.zipextract(self.input_archive, dest_dir)
        self.logger.info('%s > %s' % (os.path.basename(self.input_archive),
                                      dest_dir))
        xml_files = []
        img_map = {}
        if file_walker:
            for r, d, files in os.walk(dest_dir):
                file_walker(r, d, files, xml_files, img_map)
        return xml_files, img_map

    def get_xmls_files_with_iterator(self, file_walker=None):
        if len(self.input_archive) == 0:
            return [], {}
        archive_uid = next(iter(self.input_archive))
        dest_dir = os.path.join(self.output_dir, archive_uid)
        self.dest_dir = [dest_dir]
        self.archive_name = [archive_uid]
        os.makedirs(dest_dir)
        self.xml_dir = os.path.join(self.dest_dir[0], 'xml')
        os.makedirs(self.xml_dir)
        for archive in self.input_archive[archive_uid]:
            utils.zipextract(archive, dest_dir)
            self.logger.info('%s > %s' % (os.path.basename(archive), dest_dir))
        xml_files = []
        img_map = {}
        if file_walker:
            for r, d, files in os.walk(dest_dir):
                file_walker(r, d, files, xml_files, img_map)
        return xml_files, img_map

    def get_xmls_files_with_path(self, file_walker=None, extra_path=None):
        if len(self.input_archive) == 0:
            return [], {}
        archive_uid = next(iter(self.input_archive))
        archive_path = self.input_archive[archive_uid]
        archive_name, archive_ext = os.path.splitext(
            os.path.basename(archive_path))
        self.archive_name = [archive_name]

        # extract in a directory having the same name as the archive
        dest_dir = os.path.join(
            self.output_dir,
            archive_uid
        )
        self.dest_dir = [dest_dir]
        os.makedirs(dest_dir)
        if extra_path:
            dest_extact = os.path.join(dest_dir, extra_path)
            os.makedirs(dest_extact)
        else:
            dest_extact = dest_dir
        self.logger.info('%s\n%s\n' % (
            archive_path, re.sub(r'.', '-', archive_path)))
        self.logger.info('extracting into %s\n' % (dest_dir))

        try:
            if archive_ext.lower() == '.rar':
                utils.rarextract(archive_path, dest_extact)
            elif archive_ext.lower() == '.zip':
                utils.zipextract(archive_path, dest_extact)
        except Exception as e:
            return [], {}

        xml_files = []
        img_map = {}
        if file_walker:
            for r, d, files in os.walk(dest_extact):
                file_walker(r, d, files, xml_files, img_map)

        return xml_files, img_map

    def get_xmls_files_with_xml_and_img_path(self, xml_walker=None,
                                             img_walker=None,
                                             preprocess_hook=None,
                                             with_uid=False):
        if len(self.input_archive) == 0:
            self.dest_dir = [self.output_dir]
            return [], {}
        archive_uid = next(iter(self.input_archive))
        self.archive_name = [archive_uid]
        if with_uid:
            self.archive_name = [os.path.splitext(os.path.basename(
                self.input_archive[archive_uid]))[0]]

        # extract in a directory having the same name as the archive
        dest_dir = os.path.join(
            self.output_dir,
            archive_uid
        )
        self.dest_dir = [dest_dir]
        self.subfolders = {
            'xml':  os.path.join(dest_dir, 'xml'),
            'img':  os.path.join(dest_dir, 'img')
        }

        os.makedirs(dest_dir)
        for type, subfolder in self.subfolders.items():
            os.makedirs(subfolder)
        self.subfolders['dest'] = dest_dir
        if preprocess_hook:
            preprocess_hook(archive_uid)
        if not isinstance(self.input_archive[archive_uid], list):
            self.input_archive[archive_uid] = [self.input_archive[archive_uid]]
        for archive in self.input_archive[archive_uid]:
            tmp = self._get_sub_folder(archive)
            if tmp is None:
                continue
            sub_folder = self.subfolders[tmp]
            if archive.lower().endswith('.rar'):
                utils.rarextract(archive, sub_folder)
            elif archive.lower().endswith('.zip'):
                utils.zipextract(archive, sub_folder)
            self.logger.info('%s > %s' % (archive, sub_folder))

        xml_files = []
        img_map = {}

        if xml_walker:
            # get trademarks file
            for r, d, files in os.walk(self.subfolders['xml']):
                xml_walker(r, d, files, xml_files, img_map)
        if img_walker:
            # get images file
            for r, d, files in os.walk(self.subfolders['img']):
                img_walker(r, d, files, xml_files, img_map)
        return xml_files, img_map

    def process(self):
        xml_data = self.get_raw_data()
        xml_count, img_count = self.process_xml_data(xml_data)
        self.archive_time = []
        is_from_api = self.meta['pipeline']['input'].get('from_api', None) is not None
        for archive_name in self.archive_name:
            if is_from_api:
                archive_date = datetime.now().strftime('%Y-%m-%d')
                self.archive_time.append(archive_date)
            else:
                archive_manager = ArchiveDateManagement(
                    self.collection, archive_name)
                self.archive_time.append(archive_manager.archive_date)
        self.prepare_extract_output(xml_count, img_count)


