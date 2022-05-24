"""Django signals for SatNOGS DB"""
import json
import logging

import h5py
from django.db.models.signals import post_save

from db.base.models import Artifact, Satellite
from db.base.utils import remove_latest_tle_set, update_latest_tle_sets

LOGGER = logging.getLogger('db')


def _remove_latest_tle_set(sender, instance, **kwargs):  # pylint: disable=W0613
    """Updates if needed LatestTle entries"""
    if instance.satellite_entry.status in [
            're-entered', 'future'
    ] or instance.associated_satellite or not instance.satellite_entry.approved:
        remove_latest_tle_set(satellite_pk=instance.pk)
    else:
        update_latest_tle_sets(satellite_pks=[instance.pk])


def _extract_network_obs_id(sender, instance, created, **kwargs):  # pylint: disable=W0613
    post_save.disconnect(_extract_network_obs_id, sender=Artifact)
    try:
        with h5py.File(instance.artifact_file, 'r') as h5_file:
            if h5_file.attrs["artifact_version"] == 1:
                # Artifacts version 1
                instance.network_obs_id = h5_file.attrs["observation_id"]
            else:
                # Artifacts version 2 or later
                metadata = json.loads(h5_file.attrs["metadata"])
                instance.network_obs_id = metadata["observation_id"]
    except OSError as error:
        LOGGER.warning(error)

    instance.save()
    post_save.connect(_extract_network_obs_id, sender=Artifact)


post_save.connect(_remove_latest_tle_set, sender=Satellite)

post_save.connect(_extract_network_obs_id, sender=Artifact)
