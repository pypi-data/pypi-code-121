from functools import partial
from multiprocessing import Pool
from pathlib import Path

from six.moves.urllib.parse import urlparse

from rebotics_sdk.advanced import remote_loaders
from rebotics_sdk.constants import RCDB


class FileUploadError(Exception):
    def __init__(self, msg, response):
        super(FileUploadError, self).__init__(msg)
        self.response = response


class RCDBImportFlow(object):
    def __init__(self, rcdb_interface, retailer, retailer_model, extension):
        """
        Process wrapper with automatic API hooks

        :param ReboticsClassificationDatabase rcdb_interface:
        :param str retailer:
        :param str retailer_model:
        :param str extension:
        """
        self.rcdb = rcdb_interface
        self.import_request = self.rcdb.create(retailer, retailer_model, extension)
        self.rcdb_id = self.import_request['id']

    def __enter__(self):
        self.rcdb.update(self.rcdb_id, status=RCDB.EXPORT_IN_PROGRESS)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type or exc_val:
            self.rcdb.update(self.rcdb_id, status=RCDB.EXPORT_ERROR)
        else:
            self.rcdb.update(self.rcdb_id, status=RCDB.EXPORT_DONE)

    def upload_file(self, packed, progress_bar=False):
        destination = self.import_request['destination']
        response = remote_loaders.upload(destination, packed, progress_bar=progress_bar)
        if response.status_code > 300:
            raise FileUploadError(
                'Failed to upload destination. Response: {}. {}'.format(response.status_code, response.content),
                response)


class ReboticsClassificationDatabase(object):
    def __init__(self, *args, **kwargs):
        self.provider = kwargs.get('provider', None)

    def create(self, retailer, model, backup_type='feature_vectors', extension='rcdb'):
        return self.provider.rcdb_create({
            'retailer': retailer,
            'facenet_model': model,
            'extension': extension,
            'backup_type': backup_type,
        })

    def update(self, id_, status=RCDB.EXPORT_DONE, entries_count=0):
        assert status in (c[0] for c in RCDB.EXPORT_STATUS_CHOICES)
        return self.provider.rcdb_update(id_, {
            'status': status,
            'entries_count': entries_count
        })

    def get(self, id_):
        return self.provider.rcdb_get(id_)

    def import_flow(self, retailer, retailer_model, extension):
        return RCDBImportFlow(
            self, retailer, retailer_model, extension
        )


class FeatureVectorFlow(object):
    def __init__(self, provider, session):
        self.provider = provider
        self.session = session

    def get(self):
        return self.session.get()

    def export(self, triggered_by='sdk', source_model='', result_model='previews_backup', batch_size=50000):
        d = dict(
            triggered_by=triggered_by,
            source_model=source_model,
            result_model=result_model,
            batch_size=batch_size
        )
        return self.session.post(json=d)


def download_virtual_entry(entry, base_folder):
    """

    :param rebotics_sdk.advanced.packers.VirtualClassificationEntry entry:
    :param base_folder:
    :return:
    """
    up = urlparse(entry.image_url)
    remote_loaders.download(
        entry.image_url,
        destination=base_folder / "{}{}".format(entry.index, Path(up.path).suffix)
    )


def unload_packer_file(packer, target):
    with open(target / 'labels.txt', 'w') as labels, open(target / 'features.txt', 'w') as features:
        for entry in packer.unpack():
            labels.write("{}\n".format(entry.label))
            features.write("{}\n".format(entry.feature))
            yield entry


def download_vrcdb_file(packer, target, concurrency=4):
    target = Path(target)
    target.mkdir(parents=True, exist_ok=True)
    images_folder = target / "images"
    images_folder.mkdir(parents=True, exist_ok=True)

    with Pool(concurrency) as pool:
        result = pool.imap_unordered(
            partial(download_virtual_entry, base_folder=images_folder),
            unload_packer_file(packer, target)
        )
    return result
