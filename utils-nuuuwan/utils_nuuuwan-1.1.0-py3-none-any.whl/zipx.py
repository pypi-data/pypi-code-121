import logging
import os

log = logging.getLogger('utils.zipx')


def download_zip(download_url, zip_file):
    os.system('wget %s -O %s ' % (download_url, zip_file))
    log.info(
        'Downloaded zip from %s to %s',
        download_url,
        zip_file,
    )


def unzip(zip_file, unzip_dir):
    os.system(
        'unzip -d %s -o %s'
        % (
            unzip_dir,
            zip_file,
        )
    )
    log.info('Unzipped %s to %s', zip_file, unzip_dir)
