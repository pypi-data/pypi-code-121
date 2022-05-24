import datetime

from m3_gar.importer.client import (
    client,
)
from m3_gar.importer.signals import (
    post_fetch_version,
    pre_fetch_version,
)
from m3_gar.models import (
    Version,
)


def get_or_create_version(version_id):
    dumpdate = datetime.datetime.strptime(str(version_id), "%Y%m%d").date()
    version = Version.objects.filter(
        ver=version_id,
    ).first()

    if version:
        ver = version

        if version.dumpdate < dumpdate:
            version.dumpdate = dumpdate
            version.save()
            created = True
        else:
            created = False
    else:
        ver = Version.objects.create(
            ver=version_id,
            dumpdate=dumpdate,
        )
        created = True

    return ver, created


def parse_item_as_dict(item, update_all=False):
    """
    Разбор данных о версии как словаря
    """
    ver, created = get_or_create_version(item['VersionId'])

    if created or update_all:
        setattr(ver, 'complete_xml_url', item.get('GarXMLFullURL', ''))
        setattr(ver, 'delta_xml_url', item.get('GarXMLDeltaURL', ''))

        ver.save()


def fetch_version_info(update_all=False):

    pre_fetch_version.send(object.__class__)

    versions = client.get_all_download_file_info()
    for item in versions:
        parse_item_as_dict(item=item, update_all=update_all)

    post_fetch_version.send(object.__class__)
