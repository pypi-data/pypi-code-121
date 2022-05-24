import os
import mimetypes
from requests.auth import HTTPBasicAuth
from pypers.utils import utils
from pypers.core.step import FunctionStep
from pypers.steps.base import merge_spec_dict

class ExtractBase(FunctionStep):
    base_spec = {
        "args": {
            "inputs": [
                {
                    "name": "archives",
                    "type": "list",
                    "descr": "the archives to extract grouped by extraction date",
                    "iterable": True
                }
            ],
            "outputs": [
                {
                    "name": "manifest",
                    "descr": "manifest file listing the content of archive"
                }
            ]
        }
    }

    def __init__(self, *args, **kwargs):
        merge_spec_dict(self.spec, self.base_spec)
        super(ExtractBase, self).__init__(*args, **kwargs)
        self.logger = self.log

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

    # initializes the outputs
    def preprocess(self):
        self.data_files = {}
        self.img_files = {}
        self.media_files = {}
        self.manifest = {
            'data_files': {},
            'img_files': {},
            'media_files': {}
        }
        # self.archives is a tuple of (date, file)

        if not len(self.archives):
            return

        extraction_date = self.archives[0]
        archive = self.archives[1]

        archive_name, _ = os.path.splitext(os.path.basename(archive))

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

        # unpack the archives and collect the files
        self.collect_files(self.unpack_archive(archive, self.extraction_dir))

    # unpack an archive in extraction_directory
    # that has the same name as archive
    def unpack_archive(self, archive, dest):
        _, ext = os.path.splitext(os.path.basename(archive))

        if ext.lower() == '.rar':
            utils.rarextract(archive, dest)
        elif ext.lower() == '.zip':
            utils.zipextract(archive, dest)
        elif ext.lower() == '.tar':
            utils.tarextract(archive, dest)

        return dest

    # walk the extraction of archive
    # identify and collect files
    def collect_files(self, dest):
        rdir = os.path.basename(dest)
        for r, d, files in os.walk(dest):
            for f in files:
                self.file_in_archive(f, r)

    # assuming data files are xml
    # assuming data files and image files have
    # names equivalent to appnum
    def file_in_archive(self, file, path):
        appnum, ext = os.path.splitext(os.path.basename(file))
        if ext.lower() == '.xml':
            self.add_xml_file(appnum, os.path.join(path, file))
        else:
            file_mime = mimetypes.guess_type(file)[0]
            if (file_mime or '').startswith('image/'):
                self.add_img_file(appnum, os.path.join(path, file))
            elif file_mime == 'application/zip':
                self.archive_in_archive(file, path)

    def archive_in_archive(self, archive, path):
        name, ext = os.path.splitext(archive)
        dest = os.path.join(path, name)

        fullpath = os.path.join(path, archive)

        self.collect_files(self.unpack_archive(fullpath, dest))

        # no need to keep inner archives after extraction
        os.remove(fullpath)

    def add_xml_file(self, appnum, fullpath):
        if os.environ.get('GBD_DEV_EXTRACT_LIMIT', None):
            if len(self.manifest['data_files'].keys()) >= int(
                    os.environ.get('GBD_DEV_EXTRACT_LIMIT')):
                return

        self.manifest['data_files'].setdefault(appnum, {})
        self.manifest['data_files'][appnum]['ori'] = os.path.relpath(
            fullpath, self.extraction_dir
        )

    def add_img_file(self, appnum, fullpath):
        if os.environ.get('GBD_DEV_EXTRACT_LIMIT', None):
            if len(self.manifest['img_files'].keys()) >= int(
                    os.environ.get('GBD_DEV_EXTRACT_LIMIT')):
                return

        path = os.path.relpath(fullpath, self.extraction_dir)

        self.manifest['img_files'].setdefault(appnum, [])
        self.manifest['img_files'][appnum].append(
            {'ori': path}
        )

    def add_img_url(self, appnum, url):
        self.manifest['img_files'].setdefault(appnum, [])
        self.manifest['img_files'][appnum].append(
            {'url': url}
        )


    def postprocess(self):
        self.manifest = [self.manifest]
