from django.dispatch import (
    receiver,
)
from django.utils import (
    timezone,
)

from m3_gar.importer.signals import (
    post_download,
    post_fetch_version,
    post_import,
    post_import_table,
    post_load,
    post_unpack,
    post_update,
    pre_download,
    pre_fetch_version,
    pre_import,
    pre_import_table,
    pre_load,
    pre_unpack,
    pre_update,
)


class Timer:
    start = None
    end = None

    fetch_versions = None
    download = None
    unpack = None
    load = None

    @classmethod
    def full_reset(cls):
        cls.start = None
        cls.end = None
        cls.reset_counters()

    @classmethod
    def reset_counters(cls):
        cls.download = None
        cls.unpack = None
        cls.load = None

    @classmethod
    def init(cls):
        cls.full_reset()
        cls.start = timezone.now()


@receiver(pre_fetch_version)
def pre_fetch_version_callback(sender, **kwargs):
    pass


@receiver(post_fetch_version)
def post_fetch_version_callback(sender, **kwargs):
    time = timezone.now()
    print(f'Version info updated at {time}. Estimated time: {time - Timer.start}')


@receiver(pre_load)
def pre_load_callback(sender, src, **kwargs):
    pass


@receiver(post_load)
def post_load_callback(sender, wrapper, **kwargs):
    Timer.load = timezone.now()


@receiver(pre_download)
def pre_download_callback(sender, url, **kwargs):
    Timer.download = timezone.now()


@receiver(post_download)
def post_download_callback(sender, url, path, **kwargs):
    Timer.download = timezone.now() - Timer.download


@receiver(pre_unpack)
def pre_unpack_callback(sender, archive, **kwargs):
    Timer.unpack = timezone.now()


@receiver(post_unpack)
def post_unpack_callback(sender, archive, dst, **kwargs):
    Timer.unpack = timezone.now() - Timer.unpack


@receiver(pre_import_table)
def pre_import_table_callback(sender, table, **kwargs):
    pass


@receiver(post_import_table)
def post_import_table_callback(sender, table, **kwargs):
    pass


@receiver(pre_import)
def pre_import_callback(sender, version, **kwargs):
    print(f'Loading data v.{version.ver} started at {timezone.now()}')


@receiver(post_import)
def post_import_callback(sender, version, **kwargs):
    time = timezone.now()
    print(f'Data v.{version} loaded at {time}')
    print(
        f'Estimated time: {time - Timer.start}. '
        f'Download: {Timer.download or 0}. '
        f'Unpack: {Timer.unpack or 0}. '
        f'Import: {time - Timer.load}'
    )
    Timer.reset_counters()


@receiver(pre_update)
def pre_update_callback(sender, before, after, **kwargs):
    print(f'Updating from v.{before.ver} to v.{after.ver} started at {timezone.now()}')


@receiver(post_update)
def post_update_callback(sender, before, after, **kwargs):
    time = timezone.now()
    print(f'Data v.{before.ver} is updated to v.{after.ver} at {time}')
    print(
        f'Download: {Timer.unpack or 0}. '
        f'Unpack: {time - Timer.load}. '
        f'Import: {time - Timer.start}. '
        f'Total time: {Timer.download or 0}.'
    )
    Timer.reset_counters()
