"""Miscellaneous functions for SatNOGS DB"""
import binascii
import json
import logging
import math
from datetime import datetime, timedelta
from decimal import Decimal

from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from django.db.models import Count, Max, OuterRef, Q, Subquery
from django.db.models.functions import Substr
from django.utils.timezone import make_aware, now
from influxdb import InfluxDBClient
from satnogsdecoders import __version__ as decoders_version
from satnogsdecoders import decoder

from db.base.models import DemodData, LatestTleSet, Mode, Satellite, Tle, Transmitter

LOGGER = logging.getLogger('db')


def remove_latest_tle_set(satellite_pk):
    """Remove LatestTleSet entry for specific Satellite"""
    LatestTleSet.objects.filter(satellite__pk=satellite_pk).delete()


def update_latest_tle_sets(satellite_pks=None):
    """Update LatestTleSet entries for all or specific Satellites"""
    # Select satellite models
    if satellite_pks:
        satellites = Satellite.objects.filter(
            pk__in=satellite_pks,
            associated_satellite__isnull=True,
            satellite_entry__approved=True
        ).exclude(satellite_entry__status__in=['re-entered', 'future'])
    else:
        satellites = Satellite.objects.filter(
            associated_satellite__isnull=True, satellite_entry__approved=True
        ).exclude(satellite_entry__status__in=['re-entered', 'future'])

    # Create dictionary with Satellite ids as keys and Tle ids as values
    latest_triplets = LatestTleSet.objects.filter(
        satellite__in=satellites
    ).values_list('satellite', 'latest', 'latest_distributable')
    latest_dictionary = {
        latest_triplet[0]: (latest_triplet[1], latest_triplet[2])
        for latest_triplet in latest_triplets
    }

    # For each satellite update LatestTleSet
    for satellite in satellites:

        # Keep the Tle ids of the LatestTleSet to check Tle entries inserted after them
        # If there isn't one (new satellite or remove Tle entry) then check all of them
        tle_id, tle_id_dist = (0, 0)
        if satellite.id in latest_dictionary:
            tle_ids = latest_dictionary[satellite.id]
            tle_id = tle_ids[0] if tle_ids[0] else 0
            tle_id_dist = tle_ids[1] if tle_ids[1] else 0

        # Query for the latest Tle set for this satellite
        sub_subquery = Tle.objects.filter(
            pk__gte=tle_id, satellite=satellite
        ).exclude(tle_source__in=settings.TLE_SOURCES_IGNORE_FROM_LATEST).filter(
            satellite=OuterRef('satellite'), tle_source=OuterRef('tle_source')
        ).order_by('-updated')
        subquery = Tle.objects.filter(
            pk__gte=tle_id, satellite=satellite
        ).exclude(tle_source__in=settings.TLE_SOURCES_IGNORE_FROM_LATEST
                  ).filter(pk=Subquery(sub_subquery.values('pk')[:1])
                           ).filter(satellite=OuterRef('satellite')
                                    ).annotate(epoch=Max(Substr('tle1', 19, 14))
                                               ).order_by('-epoch')
        new_latest = Tle.objects.filter(
            pk__gte=tle_id, satellite=satellite
        ).exclude(tle_source__in=settings.TLE_SOURCES_IGNORE_FROM_LATEST
                  ).filter(pk=Subquery(subquery.values('pk')[:1]))

        # Query for the latest Tle set that is distributable for this satellite
        sub_subquery = Tle.objects.filter(
            pk__gte=tle_id_dist,
            satellite=satellite,
            tle_source__in=settings.TLE_SOURCES_REDISTRIBUTABLE
        ).exclude(tle_source__in=settings.TLE_SOURCES_IGNORE_FROM_LATEST).filter(
            satellite=OuterRef('satellite'), tle_source=OuterRef('tle_source')
        ).order_by('-updated')
        subquery = Tle.objects.filter(
            pk__gte=tle_id_dist,
            satellite=satellite,
            tle_source__in=settings.TLE_SOURCES_REDISTRIBUTABLE
        ).exclude(tle_source__in=settings.TLE_SOURCES_IGNORE_FROM_LATEST
                  ).filter(pk=Subquery(sub_subquery.values('pk')[:1])
                           ).filter(satellite=OuterRef('satellite')
                                    ).annotate(epoch=Max(Substr('tle1', 19, 14))
                                               ).order_by('-epoch')
        new_latest_dist = Tle.objects.filter(
            pk__gte=tle_id_dist,
            satellite=satellite,
            tle_source__in=settings.TLE_SOURCES_REDISTRIBUTABLE
        ).exclude(tle_source__in=settings.TLE_SOURCES_IGNORE_FROM_LATEST
                  ).filter(pk=Subquery(subquery.values('pk')[:1]))

        # Add the latest Tle set if there is a LatestTleSet entry, if not create one
        if new_latest:
            LatestTleSet.objects.update_or_create(
                satellite=satellite, defaults={
                    'latest': new_latest[0],
                    'last_modified': now()
                }
            )
        # Add the latest distributable Tle set if there is a LatestTleSet entry, if not create one
        if new_latest_dist:
            LatestTleSet.objects.update_or_create(
                satellite=satellite,
                defaults={
                    'latest_distributable': new_latest_dist[0],
                    'last_modified': now()
                }
            )

    # Remove any LatestTleSet that hasn't any Tle entry (satellite without Tle entries)
    LatestTleSet.objects.filter(latest__isnull=True, latest_distributable__isnull=True).delete()


def get_tle_sources():
    """Check for and return TLE custom sources"""
    sources = {}
    if settings.TLE_SOURCES_JSON:
        try:
            sources_json = json.loads(settings.TLE_SOURCES_JSON)
            sources['sources'] = list(sources_json.items())
        except json.JSONDecodeError as error:
            print('TLE Sources JSON ignored as it is invalid: {}'.format(error))
    if settings.SPACE_TRACK_USERNAME and settings.SPACE_TRACK_PASSWORD:
        sources['spacetrack_config'] = {
            'identity': settings.SPACE_TRACK_USERNAME,
            'password': settings.SPACE_TRACK_PASSWORD
        }
    return sources


def calculate_statistics():
    """Calculates statistics about the data we have in DB

    :returns: a dictionary of statistics
    """
    # satellite statistics
    satellites = Satellite.objects.filter(
        associated_satellite__isnull=True, satellite_entry__approved=True
    )
    total_satellites = satellites.count()

    # data statistics
    total_data = DemodData.objects.all().count()

    # transmitter statistics
    transmitters, total_transmitters, alive_transmitters_percentage = \
        calculate_transmitters_stats()

    # mode statistics
    mode_data_sorted, mode_label_sorted = \
        calculate_mode_stats(transmitters)

    # band statistics
    band_label_sorted, band_data_sorted = \
        calculate_band_stats(transmitters)

    statistics = {
        'total_satellites': total_satellites,
        'total_data': total_data,
        'transmitters': total_transmitters,
        'transmitters_alive': alive_transmitters_percentage,
        'mode_label': mode_label_sorted,
        'mode_data': mode_data_sorted,
        'band_label': band_label_sorted,
        'band_data': band_data_sorted
    }
    return statistics


def calculate_transmitters_stats():
    """Helper function to provite transmitters and statistics about
    transmitters in db (such as total and percentage of alive)"""
    transmitters = Transmitter.objects.filter(
        satellite__associated_satellite__isnull=True, satellite__satellite_entry__approved=True
    )
    total_transmitters = transmitters.count()
    alive_transmitters = transmitters.filter(status='active').count()
    if alive_transmitters > 0 and total_transmitters > 0:
        try:
            alive_transmitters_percentage = '{0}%'.format(
                round((float(alive_transmitters) / float(total_transmitters)) * 100, 2)
            )
        except ZeroDivisionError as error:
            LOGGER.error(error, exc_info=True)
            alive_transmitters_percentage = '0%'
    else:
        alive_transmitters_percentage = '0%'

    return transmitters, total_transmitters, alive_transmitters_percentage


def calculate_mode_stats(transmitters):
    """Helper function to provide data and labels for modes associated with
    transmitters provided"""
    modes = Mode.objects.all()
    mode_label = []
    mode_data = []

    for mode in modes:
        filtered_transmitters = transmitters.filter(
            downlink_mode=mode
        ).count() + transmitters.filter(uplink_mode=mode).count()
        mode_label.append(mode.name)
        mode_data.append(filtered_transmitters)

    # needed to pass testing in a fresh environment with no modes in db
    if not mode_label:
        mode_label = ['FM']
    if not mode_data:
        mode_data = ['FM']

    mode_data_sorted, mode_label_sorted = \
        list(zip(*sorted(zip(mode_data, mode_label), reverse=True)))

    return mode_data_sorted, mode_label_sorted


def calculate_band_stats(transmitters):
    """Helper function to provide data and labels for bands associated with
    transmitters provided"""
    band_label = []
    band_data = []

    bands = [
        # <30.000.000 - HF
        {
            'lower_limit': 0,
            'upper_limit': 30000000,
            'label': 'HF'
        },
        # 30.000.000 ~ 300.000.000 - VHF
        {
            'lower_limit': 30000000,
            'upper_limit': 300000000,
            'label': 'VHF'
        },
        # 300.000.000 ~ 1.000.000.000 - UHF
        {
            'lower_limit': 300000000,
            'upper_limit': 1000000000,
            'label': 'UHF',
        },
        # 1G ~ 2G - L
        {
            'lower_limit': 1000000000,
            'upper_limit': 2000000000,
            'label': 'L',
        },
        # 2G ~ 4G - S
        {
            'lower_limit': 2000000000,
            'upper_limit': 4000000000,
            'label': 'S',
        },
        # 4G ~ 8G - C
        {
            'lower_limit': 4000000000,
            'upper_limit': 8000000000,
            'label': 'C',
        },
        # 8G ~ 12G - X
        {
            'lower_limit': 8000000000,
            'upper_limit': 12000000000,
            'label': 'X',
        },
        # 12G ~ 18G - Ku
        {
            'lower_limit': 12000000000,
            'upper_limit': 18000000000,
            'label': 'Ku',
        },
        # 18G ~ 27G - K
        {
            'lower_limit': 18000000000,
            'upper_limit': 27000000000,
            'label': 'K',
        },
        # 27G ~ 40G - Ka
        {
            'lower_limit': 27000000000,
            'upper_limit': 40000000000,
            'label': 'Ka',
        },
    ]

    for band in bands:
        filtered = transmitters.filter(
            downlink_low__gte=band['lower_limit'], downlink_low__lt=band['upper_limit']
        ).count()
        band_label.append(band['label'])
        band_data.append(filtered)

    band_data_sorted, band_label_sorted = \
        list(zip(*sorted(zip(band_data, band_label), reverse=True)))

    return band_label_sorted, band_data_sorted


def create_point(fields, satellite, telemetry, demoddata, version):
    """Create a decoded data point in JSON format that is influxdb compatible

    :returns: a JSON formatted time series data point
    """
    point = [
        {
            'time': demoddata.timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'measurement': satellite.satellite_entry.norad_cat_id,
            'tags': {
                'satellite': satellite.satellite_entry.name,
                'decoder': telemetry.decoder,
                'station': demoddata.station,
                'observer': demoddata.observer,
                'source': demoddata.app_source,
                'version': version
            },
            'fields': fields
        }
    ]

    return point


def write_influx(json_obj):
    """Take a json object and send to influxdb."""
    client = InfluxDBClient(
        settings.INFLUX_HOST,
        settings.INFLUX_PORT,
        settings.INFLUX_USER,
        settings.INFLUX_PASS,
        settings.INFLUX_DB,
        ssl=settings.INFLUX_SSL,
        verify_ssl=settings.INFLUX_VERIFY_SSL
    )
    client.write_points(json_obj)


def decode_demoddata(demoddata, satellite, tlmdecoder):
    """Decode a DemodData object and push it either in InfluxDB instance or in local DB"""
    try:
        decoder_class = getattr(decoder, tlmdecoder.decoder.capitalize())
    except AttributeError:
        return
    try:
        with open(demoddata.payload_frame.path) as frame_file:
            # we get data frames in hex but kaitai requires binary
            hexdata = frame_file.read()
            bindata = binascii.unhexlify(hexdata)

        try:
            frame = decoder_class.from_bytes(bindata)
            json_obj = create_point(
                decoder.get_fields(frame), satellite, tlmdecoder, demoddata, decoders_version
            )

            # if we are set to use InfluxDB, send the decoded data
            # there, otherwise we store it in the local DB.
            if settings.USE_INFLUX:
                write_influx(json_obj)
                DemodData.objects.filter(pk=demoddata.id).update(
                    is_decoded=True, payload_decoded='influxdb'
                )
            else:
                DemodData.objects.filter(pk=demoddata.id).update(
                    is_decoded=True, payload_decoded=json_obj
                )
        except BaseException:  # pylint: disable=W0703
            DemodData.objects.filter(pk=demoddata.id).update(is_decoded=False, payload_decoded='')
    except (IOError, binascii.Error) as error:
        LOGGER.error(error, exc_info=True)


def decode_data(sat_id, demoddata_id=None, redecode=False):
    """Decode data for a satellite, with an option to limit the scope.

    :param sat_id: the Satellite Identifier of the satellite to decode data for
    :param demoddata_id: if demoddata_id exists, try to decode this demoddata object
    :param redecode: redecode demoddata or only recent
    """
    satellite = Satellite.objects.get(satellite_identifier__sat_id=sat_id)

    # If satellite is merged use telemetries from the associated satellite
    if satellite.associated_satellite:
        satellite = satellite.associated_satellite
    telemetry_decoders = satellite.telemetries.all()

    if telemetry_decoders:
        data = DemodData.objects.select_for_update()
        if demoddata_id:
            if redecode:
                data = data.filter(pk=demoddata_id)
            else:
                data = data.filter(pk=demoddata_id, is_decoded=False)
        else:
            # Get a list of all associated satellites for decoding all related data
            satellites_list = list(satellite.associated_with.all().values_list('pk', flat=True))
            satellites_list.append(satellite.pk)
            if redecode:
                data = data.filter(satellite__in=satellites_list)
            else:
                time_period = make_aware(datetime.utcnow() - timedelta(hours=48))
                data = data.filter(
                    satellite__in=satellites_list, timestamp__gte=time_period, is_decoded=False
                )

        with transaction.atomic():
            # iterate over DemodData objects
            for obj in data:
                # iterate over Telemetry decoders
                for tlmdecoder in telemetry_decoders:
                    decode_demoddata(demoddata=obj, satellite=satellite, tlmdecoder=tlmdecoder)


# Caches stats about satellites and data
def cache_statistics():
    """Populate a django cache with statistics from data in DB

    .. seealso:: calculate_statistics
    """
    statistics = calculate_statistics()
    cache.set('stats_transmitters', statistics, 60 * 60 * 25)

    ids = []
    sat_stats = {}

    satellites = Satellite.objects.filter(satellite_entry__approved=True).values(
        'satellite_entry__name', 'satellite_entry__norad_cat_id', 'id', 'associated_satellite',
        'satellite_identifier__sat_id'
    ).annotate(
        count=Count('telemetry_data'),
        decoded=Count('telemetry_data', filter=Q(telemetry_data__is_decoded=True)),
        latest_payload=Max('telemetry_data__timestamp')
    )

    # Aggregate stats for satellites and their associated ones
    for sat in satellites:
        # if satellite is merged then add statistics to its association
        if sat['associated_satellite']:
            if sat['associated_satellite'] in sat_stats:
                sat_stats[sat['associated_satellite']]['count'] += sat['count']
                sat_stats[sat['associated_satellite']]['decoded'] += sat['decoded']
                if sat['latest_payload']:
                    sat_stats[sat['associated_satellite']]['latest_payload'] = max(
                        [
                            sat_stats[sat['associated_satellite']]['latest_payload'],
                            sat['latest_payload']
                        ],
                        default=sat['latest_payload']
                    )
            else:
                sat_id = sat['associated_satellite']
                del sat['associated_satellite']
                sat_stats[sat_id] = sat
        else:
            ids.append(sat['id'])
            # if non-merged satellite is already in sat_stats then overwrite
            # the name and the NORAD ID as the current ones are from one of its
            # associated satellites that have been merged with it.
            if sat['id'] in sat_stats:
                sat_stats[sat['id']]['satellite_entry__name'] = sat['satellite_entry__name']
                sat_stats[sat['id']
                          ]['satellite_entry__norad_cat_id'] = sat['satellite_entry__norad_cat_id']
                sat_stats[sat['id']
                          ]['satellite_identifier__sat_id'] = sat['satellite_identifier__sat_id']
                sat_stats[sat['id']]['count'] += sat['count']
                sat_stats[sat['id']]['decoded'] += sat['decoded']
                if sat_stats[sat['id']]['latest_payload']:
                    if sat['latest_payload']:
                        sat_stats[sat['id']]['latest_payload'] = max(
                            sat_stats[sat['id']]['latest_payload'], sat['latest_payload']
                        )
                else:
                    sat_stats[sat['id']]['latest_payload'] = sat['latest_payload']
            else:
                del sat['associated_satellite']
                sat_stats[sat['id']] = sat

    for sat_pk in sat_stats:
        cache.set(sat_pk, sat_stats[sat_pk], 60 * 60 * 25)
    cache.set('satellites_ids', ids, 60 * 60 * 25)

    observers = DemodData.objects.values('observer').annotate(
        count=Count('observer'), latest_payload=Max('timestamp')
    ).order_by('-count')
    cache.set('stats_observers', observers, 60 * 60 * 25)


def remove_exponent(converted_number):
    """Remove exponent."""
    return converted_number.quantize(
        Decimal(1)
    ) if converted_number == converted_number.to_integral() else converted_number.normalize()


def millify(number, precision=0):
    """Humanize number."""
    millnames = ['', 'k', 'M', 'B', 'T', 'P', 'E', 'Z', 'Y']
    number = float(number)
    millidx = max(
        0,
        min(
            len(millnames) - 1, int(math.floor(0 if number == 0 else math.log10(abs(number)) / 3))
        )
    )
    result = '{:.{precision}f}'.format(number / 10**(3 * millidx), precision=precision)
    result = remove_exponent(Decimal(result))
    return '{0}{dx}'.format(result, dx=millnames[millidx])


def read_influx(norad):
    """Queries influxdb for the last 30d of data points (counted) in 1d resolution.

    :param norad: the NORAD ID of the satellite to query influxdb for
    :returns: a raw json of the measurement, timestamps, and point counts
    """
    client = InfluxDBClient(
        settings.INFLUX_HOST,
        settings.INFLUX_PORT,
        settings.INFLUX_USER,
        settings.INFLUX_PASS,
        settings.INFLUX_DB,
        ssl=settings.INFLUX_SSL,
        verify_ssl=settings.INFLUX_VERIFY_SSL
    )

    # check against injection
    if isinstance(norad, int):
        # epoch:s to set the return timestamp in unixtime for easier conversion
        params = {'epoch': 's'}
        results = client.query(
            'SELECT count(*) FROM "' + str(norad)
            + '" WHERE time > now() - 30d GROUP BY time(1d) fill(null)',
            params=params
        )
        return results.raw
    # no-else-return
    return ''
