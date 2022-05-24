import dataclasses
import functools
import io
import json
import logging
import os
import pathlib
import re
import typing
import uuid
import zipfile
from collections import namedtuple, defaultdict
from datetime import datetime
from hashlib import md5
from io import BytesIO, StringIO
from multiprocessing.pool import ThreadPool

import tqdm

import rebotics_sdk
from rebotics_sdk.advanced import remote_loaders

logger = logging.getLogger(__name__)

ClassificationEntry = namedtuple('ClassificationEntry', ['label', 'feature', 'image', 'filename', 'index'])
ImageEntry = namedtuple('ImageEntry', ['filename', 'filepath', 'order'])


class VirtualClassificationEntry(object):
    def __init__(self, label, feature, image_url, index=None):
        self.label = label
        self.feature = feature
        self.image_url = image_url
        self.index = index

    def to_dict(self):
        return {
            'label': self.label,
            'feature': self.feature,
            'image_url': self.image_url,
            'index': self.index
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            label=d['label'],
            feature=d['feature'],
            image_url=d['image_url'],
            index=d['index']
        )


NUMERIC_VALUE = re.compile(r'\d+')


class ClassificationDatabaseException(Exception):
    pass


class DuplicateFeatureVectorsException(ClassificationDatabaseException):
    def __init__(self, msg, duplicates):
        super(DuplicateFeatureVectorsException, self).__init__(msg)
        self.duplicates = duplicates


def extract_numeric(filename):
    found = NUMERIC_VALUE.findall(filename)
    if len(found) == 0:
        raise ClassificationDatabaseException('Images name should contain numeric value that represents the order. '
                                              'Instead of {} name was used'.format(filename))
    return int(found[0])


class BaseClassificationDatabasePacker(object):
    version = 0
    extension = 'zip'

    def __init__(self, source=None, destination=None, progress_bar=False, check_duplicates=False,
                 *args, **kwargs):
        if source is not None and destination is not None:
            raise ValueError("You can't sent source and destination at a same time.")

        self.source = source

        self.meta_data = {
            'packed': datetime.now().strftime('%c'),
            'sdk_version': rebotics_sdk.__version__,
            'packer_version': self.version
        }
        self.zip_io = None

        if self.source is not None:
            self.read_meta()

        self.check_duplicates = check_duplicates
        self.images = []

        if hasattr(destination, 'write') or hasattr(destination, 'read'):
            self.destination = destination  # file like object
        elif destination is None:
            self.destination = BytesIO()
        elif isinstance(destination, str) or isinstance(destination, pathlib.PurePath):
            # in python 2 it doesn't accept pathlib PurePath, but only os.path or str
            self.destination = str(destination)
            if not self.destination.endswith(self.extension):
                self.destination = "{}.{}".format(self.destination, self.extension)

        self.progress_bar = progress_bar

    def read_lines(self, lines):
        return [x for x in lines.split('\n') if x]

    def zipfile(self, file, **kwargs):
        # if python version is
        params = dict(
            compression=zipfile.ZIP_DEFLATED,
            allowZip64=True,
        )
        #
        # if (sys.version_info.major, sys.version_info.minor) >= (3, 7):
        #     # using the most aggressive compression
        #     params['compresslevel'] = 9  # default is 6

        params.update(kwargs)

        for compression_option in [zipfile.ZIP_DEFLATED, zipfile.ZIP_STORED]:
            try:
                params['compression'] = compression_option
                return zipfile.ZipFile(file, **params)
            except RuntimeError:
                pass

    def __enter__(self):
        if self.zip_io is not None:
            return self

        # check for file to be not closed

        if self.source is not None:
            self.zip_io = self.zipfile(self.source, mode='r')
        elif self.destination is not None:
            self.zip_io = self.zipfile(self.destination, mode='w')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.zip_io.close()
        self.zip_io = None

    def pack(self, *args, **kwargs):
        raise NotImplementedError()

    def unpack(self):
        raise NotImplementedError()

    def read_meta(self):
        with self as packer:
            self.meta_data = json.load(packer.zip_io.open('meta.json'))


class ZipDatabasePacker(BaseClassificationDatabasePacker):
    """
    Unified file format for packing classification database into single folder
    File format is the zip based archive with following :

    labels.txt
    features.txt
    meta.json
    """
    version = 0
    extension = 'zip'

    def pack(self, labels, features, *args, **kwargs):
        labels_io = StringIO("\n".join(labels))
        features_io = StringIO("\n".join(features))
        self.meta_data['count'] = len(labels)

        with self.zipfile(self.destination, mode='w') as zip_io:
            zip_io.writestr('labels.txt', labels_io.getvalue())
            zip_io.writestr('features.txt', features_io.getvalue())
            zip_io.writestr('meta.json', json.dumps(self.meta_data))
        return self.destination

    def unpack(self):
        if self.source is None:
            raise ClassificationDatabaseException("Can not unpack with empty source file")

        with self.zipfile(self.source, mode='r') as zip_io:
            try:
                self.meta_data = json.load(zip_io.open('meta.json'))
            except KeyError:
                # meta.json is not presented, working in the compatibility mode
                pass

            labels = self.read_lines(zip_io.read('labels.txt').decode('utf-8'))
            features = self.read_lines(zip_io.read('features.txt').decode('utf-8'))

            for index, (label, feature) in enumerate(zip(labels, features)):
                yield ClassificationEntry(
                    label, feature, None, None, index
                )


class ClassificationDatabasePacker(BaseClassificationDatabasePacker):
    """
    Unified file format for packing classification database into single folder
    File format is the zip based archive with following :

    labels.txt
    features.txt
    meta.json
    images/  - folder with images, this folder can be empty
    """

    version = 1
    extension = 'rcdb'
    images_extensions = {'jpeg', 'png', 'jpg'}

    def extract_meta_data(self, labels_path, features_path, images_folder):
        known_order = set()
        for f in pathlib.Path(images_folder).iterdir():
            if f.is_file():
                extension = f.suffix
                if extension in self.images_extensions:
                    raise ClassificationDatabaseException("Extension is not supported by packer: {}".format(f.name))
                numeric_order = extract_numeric(f.name)
                if numeric_order in known_order:
                    raise ClassificationDatabaseException("Numeric order collision. {}".format(f.name))

                known_order.add(numeric_order)
                self.images.append(ImageEntry(f.name, str(f), numeric_order))

        # repack based on the filename and it's numeric value
        self.images.sort(key=lambda i: i.order)  # sort by numeric value of the filename

        with open(labels_path, 'r') as labels_io, open(features_path, 'r') as features_io:
            labels = self.read_lines(labels_io.read())
            features = self.read_lines(features_io.read())

        labels_count = len(labels)
        features_count = len(features)
        files_count = len(self.images)

        if labels_count != features_count:
            raise ClassificationDatabaseException('Inconsistent count of labels and features. {}/{}'.format(
                labels_count, features_count
            ))

        if labels_count != files_count:
            raise ClassificationDatabaseException(
                'Inconsistent count of labels and features and files. {}/{}/{}'.format(
                    labels_count, features_count, files_count
                ))

        self.meta_data.update({
            'count': features_count,
            'images': [str(img.filename) for img in self.images]
        })

        if not self.check_duplicates:
            return

        # checking for the uniqueness of the FV
        features_map = defaultdict(list)
        for i, fv in tqdm.tqdm(enumerate(features), total=features_count, disable=not self.progress_bar, leave=False):
            md_ = md5(fv.encode('utf-8'))
            features_map[md_.hexdigest()].append(i)
        duplicates = []
        for same_fv_ids in features_map.values():
            if len(same_fv_ids) > 1:
                duplicates.append([
                    ClassificationEntry(
                        labels[id_],
                        features[id_],
                        None,
                        self.images[id_].filename,
                        id_
                    ) for id_ in same_fv_ids
                ])

        if duplicates:
            raise DuplicateFeatureVectorsException(
                "Detected {} duplicate groups.".format(len(duplicates)),
                duplicates=duplicates
            )

    def pack(self, labels, features, images, *args, **kwargs):
        self.extract_meta_data(labels, features, images)

        with self.zipfile(self.destination, mode='w') as zip_io:
            zip_io.write(labels, 'labels.txt')
            zip_io.write(features, 'features.txt')
            zip_io.writestr('meta.json', json.dumps(self.meta_data))

            for img in tqdm.tqdm(
                self.images,
                leave=False,
                disable=not self.progress_bar
            ):
                zip_io.write(img.filepath, str(pathlib.Path('images') / img.filename))

        return self.destination

    def unpack(self):
        """

        :return: generator of label, feature, image_io
        :rtype:self.meta_data
        """
        if self.source is None:
            raise ClassificationDatabaseException("Can not unpack with empty source file")

        with self.zipfile(self.source, mode='r') as zip_io:
            labels = self.read_lines(zip_io.read('labels.txt').decode('utf-8'))
            features = self.read_lines(zip_io.read('features.txt').decode('utf-8'))

            for index, (label, feature, image_name) in enumerate(zip(
                labels,
                features,
                self.meta_data['images']
            )):
                image = zip_io.read('images/{}'.format(image_name))
                yield ClassificationEntry(
                    label, feature, image, image_name, index
                )


@dataclasses.dataclass
class DataEntry:
    label: str
    feature: typing.List[float]
    uuid: uuid.UUID
    image_url: str
    image: typing.Optional[typing.BinaryIO] = None


def _task_unpack_classification_entry(entry: DataEntry, download_image=False):
    if not download_image:
        return entry

    data = dataclasses.asdict(entry)
    data['image'] = buffer = remote_loaders.download(entry.image_url)
    buffer.seek(0)
    return DataEntry(**data)


class VirtualClassificationDatabasePacker(BaseClassificationDatabasePacker):
    version = 2
    extension = 'rcdb'

    def __init__(self, *args, **kwargs):
        self.with_images = kwargs.get('with_images', False)
        self.concurrency = kwargs.get('concurrency', None)
        if self.concurrency is None or self.concurrency < 1:
            self.concurrency = os.cpu_count()
        super(VirtualClassificationDatabasePacker, self).__init__(*args, **kwargs)

    def pack(self, labels, features, uuids, images, *args, **kwargs):
        with self.zipfile(self.destination, mode='w') as zip_io:
            # writing those as a file
            zip_io.write(labels, 'labels.txt')
            zip_io.write(features, 'features.txt')
            zip_io.write(uuids, 'uuids.txt')
            zip_io.write(images, 'images.txt')

            zip_io.writestr('meta.json', json.dumps(self.meta_data))
        return self.destination

    def unpack(self):
        if self.with_images:
            task = functools.partial(_task_unpack_classification_entry, download_image=True)
        else:
            task = _task_unpack_classification_entry

        with ThreadPool(self.concurrency) as pool:
            for batch in self._data_entry_generator():
                yield from pool.map(task, batch)

    def _data_entry_generator(self):
        batch = []  # initial batch
        with self.zipfile(self.source, mode='r') as zip_io:
            labels_io = io.TextIOWrapper(zip_io.open("labels.txt"), encoding='utf-8')
            features_io = io.TextIOWrapper(zip_io.open("features.txt"), encoding='utf-8')
            uuids_io = io.TextIOWrapper(zip_io.open("uuids.txt"), encoding='utf-8')
            images_io = io.TextIOWrapper(zip_io.open("images.txt"), encoding='utf-8')

            while True:
                label = labels_io.readline().strip()
                feature = features_io.readline().strip()
                uuid_ = uuids_io.readline().strip()
                image_url = images_io.readline().strip()

                if label == '' or feature == '':
                    break

                batch.append(DataEntry(
                    label,
                    feature,
                    uuid_,
                    image_url
                ))
                # if len(batch) >= self.concurrency:
                if len(batch) >= self.concurrency:
                    yield batch
                    batch = []

            if batch:
                yield batch
