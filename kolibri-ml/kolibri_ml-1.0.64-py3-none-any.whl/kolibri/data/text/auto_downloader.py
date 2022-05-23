import os
import errno
import logging
import tarfile
import pickle
import requests
import re
from tqdm import tqdm
from kolibri.settings import DATA_PATH, GITHUB_TOKEN, GITHUB_REPO_NAME
from copy import copy
from pathlib import Path

from kdmt.wget import Wget
LOGGER = logging.getLogger(__name__)
from kolibri.data import resources


class DownloaderBase(object):
    def __init__(self,  download_dir=DATA_PATH):
        self._error = None
        self.download_dir=download_dir
        try:
            self.local_db = dict(pickle.load(open(os.path.join(DATA_PATH, ".index"), "rb")))
        except IOError as e:
            print("index not found. Creating new index")
            self.local_db = {}

    def download(self, file_path, external_url):


        self.pkg=os.path.splitext(os.path.basename(file_path))[0]
        file_path_key=Path(file_path).as_posix()

        if file_path_key in resources.Resources_sha.keys():
            self.url =resources.Resources_sha[file_path_key]['url']

        elif file_path_key+'.tar.gz' in resources.Resources_sha.keys():
            file_path_key+='.tar.gz'
            file_path += '.tar.gz'
            self.url = resources.Resources_sha[file_path_key]['url']
        else:
            download_file_path=os.path.join(self.download_dir, file_path)
            if external_url is not None and not os.path.exists(download_file_path):
                LOGGER.info("Trying external URL")
                wg = Wget()
                wg.download(external_url, filename=download_file_path)
            elif external_url is None:
                LOGGER.error("Couldn't find file {}".format(file_path_key))


        if not os.path.exists(self.download_dir):
            print('creating download dir')
            os.mkdir(self.download_dir)
        server_file_entry=resources.Resources_sha.get(file_path_key, None)
        local_file_entry=self.local_db.get(file_path_key, None)
        if server_file_entry is not None:
            server_file_checksum=server_file_entry['sha']
            local_file_checksum=-1
            if local_file_entry is not None:
                local_file_checksum=local_file_entry['sha']
            if server_file_checksum != local_file_checksum or not os.path.exists(os.path.join(self.download_dir, file_path)):
                self._download_data(file_path)
                LOGGER.info('data already set up')
                self.local_db[file_path_key]=copy(resources.Resources_sha[file_path_key])
                pickle.dump(list(self.local_db.items()), open(os.path.join(DATA_PATH, ".index"), "wb"))


    @staticmethod
    def get_filename_from_cd(cd):
        """
        Get filename from content-disposition
        """
        if not cd:
            return None
        fname = re.findall('filename="(.+)"', cd)
        if len(fname) == 0:
            return None
        return fname[0]

    def _download_data(self, file_path):
        LOGGER.info('downloading data for {}...'.format(self.pkg))
        r = requests.get(self.url, stream=True)
        total_length = r.headers.get('content-length', 0)
        pbar = tqdm(
                unit='B', unit_scale=True,
                total=int(total_length))
        if total_length is None:
            LOGGER.error("Couldn't fetch model data.")
            raise Exception("Couldn't fetch model data.")
        else:
            filename = Path(file_path).name
            path = os.path.join(self.download_dir, file_path)
            if not os.path.exists(os.path.dirname(path)):
                try:
                    os.makedirs(os.path.dirname(path))
                except OSError as exc:  # Guard against race condition
                    if exc.errno != errno.EEXIST:
                        raise
            with open(path, 'wb') as f:
                for data in r.iter_content(chunk_size=1024):
                    f.write(data)
                    pbar.update(len(data))
            if filename.endswith('.tar.gz') or filename.endswith('.tgz'):
                tar = tarfile.open(path, "r:gz")
                for tarinfo in tar:
                    tar.extract(tarinfo, os.path.dirname(path))
                tar.close()
                # clean raw tar gz
                # if os.path.exists(path):
                #     os.remove(path)
            LOGGER.info('download complete')

class Downloader(DownloaderBase):
    def __init__(self, file_path, download_dir=DATA_PATH):
        super().__init__(download_dir)

        self.download(file_path)

