"""SatNOGS DB API django rest framework Views"""
from django.conf import settings
from django.core.files.base import ContentFile
from django.db.models import F
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema, \
    extend_schema_view
from rest_framework import mixins, status, viewsets
from rest_framework.parsers import FileUploadParser, FormParser, MultiPartParser
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

from db.api import filters, pagination, serializers
from db.api.parsers import JSONLDParser
from db.api.perms import IsAuthenticatedOrOptions, SafeMethodsWithPermission
from db.api.renderers import BrowserableJSONLDRenderer, JSONLDRenderer
from db.base.helpers import gridsquare
from db.base.models import SATELLITE_STATUS, SERVICE_TYPE, TRANSMITTER_STATUS, TRANSMITTER_TYPE, \
    Artifact, DemodData, LatestTleSet, Mode, Satellite, SatelliteEntry, SatelliteIdentifier, \
    Transmitter
from db.base.tasks import decode_current_frame, publish_current_frame, update_satellite_name

ISS_EXAMPLE = OpenApiExample('25544 (ISS)', value=25544)


@extend_schema_view(
    retrieve=extend_schema(
        description='Retrieve a single RF Mode from SatNOGS DB based on its ID',
    ),
    list=extend_schema(description='Retrieve a complete list of RF Modes from SatNOGS DB', )
)
class ModeViewSet(viewsets.ReadOnlyModelViewSet):  # pylint: disable=R0901
    """
    Read-only view into the transmitter modulation modes (RF Modes) currently tracked
    in the SatNOGS DB database

    For more details on individual RF mode types please [see our wiki][moderef].

    [moderef]: https://wiki.satnogs.org/Category:RF_Modes
    """
    renderer_classes = [
        JSONRenderer, BrowsableAPIRenderer, JSONLDRenderer, BrowserableJSONLDRenderer
    ]
    queryset = Mode.objects.all()
    serializer_class = serializers.ModeSerializer


@extend_schema_view(
    list=extend_schema(
        description='Retrieve a full or filtered list of satellites in SatNOGS DB',
        parameters=[
            # drf-spectacular does not currently recognize the in_orbit filter as a
            # bool, forcing it here. See drf-spectacular#234
            OpenApiParameter(
                name='in_orbit',
                description='Filter by satellites currently in orbit (True) or those that have \
                            decayed (False)',
                required=False,
                type=bool
            ),
            OpenApiParameter(
                name='status',
                description='Filter by satellite status: ' + ' '.join(SATELLITE_STATUS),
                required=False,
                type=OpenApiTypes.STR
            ),
            OpenApiParameter(
                name='norad_cat_id',
                description='Select a satellite by its NORAD-assigned identifier',
                examples=[ISS_EXAMPLE],
            ),
        ],
    ),
    retrieve=extend_schema(
        description='Retrieve details on a single satellite in SatNOGS DB',
        parameters=[
            OpenApiParameter(
                'satellite_identifier__sat_id',
                OpenApiTypes.STR,
                OpenApiParameter.PATH,
                description='Select a satellite by its Satellite Identifier',
            ),
        ],
    ),
)
class SatelliteViewSet(  # pylint: disable=R0901
        mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin,
        viewsets.GenericViewSet):
    """
    View into the Satellite entities in the SatNOGS DB database
    """
    renderer_classes = [
        JSONRenderer, BrowsableAPIRenderer, JSONLDRenderer, BrowserableJSONLDRenderer
    ]
    parser_classes = [JSONLDParser]
    queryset = Satellite.objects.filter(
        associated_satellite__isnull=True, satellite_entry__approved=True
    ).prefetch_related('associated_with', 'telemetries')
    serializer_class = serializers.SatelliteSerializer
    filterset_class = filters.SatelliteViewFilter
    lookup_field = 'satellite_identifier__sat_id'

    def get_object(self):
        queryset = self.get_queryset()
        # Apply any filter backends
        queryset = self.filter_queryset(queryset)

        # In case user uses NORAD ID for getting satellite
        if 'satellite_entry__norad_cat_id' in self.kwargs:
            norad_cat_id = self.kwargs['satellite_entry__norad_cat_id']
            return get_object_or_404(queryset, satellite_entry__norad_cat_id=norad_cat_id)

        # Getting satellite by using Satellite Identifier
        sat_id = self.kwargs['satellite_identifier__sat_id']
        try:
            return queryset.get(satellite_identifier__sat_id=sat_id)
        except Satellite.DoesNotExist:
            return get_object_or_404(
                queryset, associated_with__satellite_identifier__sat_id=sat_id
            )

    def create(self, request, *args, **kwargs):  # noqa: C901; pylint: disable=R0911,R0912,R0915
        """
        Creates a satellite suggestion.
        """
        satellites_data = []
        for satellite_entry in request.data['@graph']:
            if 'satellite' not in satellite_entry:
                data = 'Satellite Entry without "satellite" key'
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            if not satellite_entry['satellite']:
                data = 'One or more of the required fields are missing.\n Required fields: \
                        name, status, citation'

                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            satellite = satellite_entry['satellite']
            create_satellite_identifier = False

            satellite_data = {}
            if "@id" not in satellite:
                data = 'Missing "@id" for one or more entries'
                return Response(data, status=status.HTTP_400_BAD_REQUEST)

            if 'sat_id' in satellite:
                if isinstance(satellite['sat_id'], list):
                    data = 'Multiple values for "http://schema.org/identifier" or multiple \
                            entries with the same "@id" and different \
                            "http://schema.org/identifier" values'

                    return Response(data, status=status.HTTP_400_BAD_REQUEST)
                sat_id = satellite['sat_id']
                try:
                    satellite_object = Satellite.objects.get(satellite_identifier__sat_id=sat_id)
                    satellite_data['satellite_identifier'
                                   ] = satellite_object.satellite_entry.satellite_identifier.pk
                    satellite_data['norad_follow_id'
                                   ] = satellite_object.satellite_entry.norad_follow_id
                    satellite_data['description'] = satellite_object.satellite_entry.description
                    satellite_data['dashboard_url'
                                   ] = satellite_object.satellite_entry.dashboard_url
                    satellite_data['image'] = satellite_object.satellite_entry.image
                    satellite_data['decayed'] = satellite_object.satellite_entry.decayed
                    satellite_data['countries'] = satellite_object.satellite_entry.countries
                    satellite_data['website'] = satellite_object.satellite_entry.website
                    satellite_data['launched'] = satellite_object.satellite_entry.launched
                    satellite_data['deployed'] = satellite_object.satellite_entry.deployed
                    satellite_data['operator'] = satellite_object.satellite_entry.operator
                except Satellite.DoesNotExist:
                    try:
                        satellite_identifier = SatelliteIdentifier.objects.get(sat_id=sat_id)
                        satellite_data['satellite_identifier'] = satellite_identifier.pk
                    except SatelliteIdentifier.DoesNotExist:
                        satellite_identifier = SatelliteIdentifier.objects.create(sat_id=sat_id)
                        satellite_data['satellite_identifier'] = satellite_identifier.pk

            else:
                create_satellite_identifier = True

            if isinstance(satellite['status'], list):
                data = 'Multiple values for "https://schema.space/metasat/status" or multiple \
                        entries with the same "@id" and different \
                        "https://schema.space/metasat/status" values'

                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            if isinstance(satellite['name'], list):
                data = 'Multiple values for "https://schema.space/metasat/name" or multiple \
                        entries with the same "@id" and different \
                        "https://schema.space/metasat/name" values'

                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            if isinstance(satellite['citation'], list):
                data = 'Multiple values for "https://schema.org/citation" or multiple \
                        entries with the same "@id" and different \
                        "https://schema.org/citation" values'

                return Response(data, status=status.HTTP_400_BAD_REQUEST)

            satellite_data['name'] = satellite['name']
            satellite_data['status'] = satellite['status']
            satellite_data['citation'] = satellite['citation']
            satellite_data['created_by'] = request.user.pk

            if 'norad_cat_id' in satellite:
                if isinstance(satellite['norad_cat_id'], list):
                    data = 'Multiple values for "https://schema.space/metasat/noradID" or \
                            multiple entries with the same "@id" and different \
                            "https://schema.space/metasat/noradId" values'

                    return Response(data, status=status.HTTP_400_BAD_REQUEST)
                satellite_data['norad_cat_id'] = satellite['norad_cat_id']

            if 'names' in satellite:
                if isinstance(satellite['norad_cat_id'], list):
                    satellite_data['names'] = '\r\n'.join(satellite['names'])
                else:
                    satellite_data['names'] = satellite['names']

            if create_satellite_identifier:
                satellite_identifier = SatelliteIdentifier.objects.create()
                satellite_data['satellite_identifier'] = satellite_identifier.pk

            satellites_data.append(satellite_data)

        serializer = serializers.SatelliteEntrySerializer(
            data=satellites_data, many=True, allow_empty=True
        )
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_201_CREATED)


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name='satellite__norad_cat_id',
                description='NORAD ID of a satellite to filter telemetry data for',
                examples=[ISS_EXAMPLE],
            ),
            OpenApiParameter(
                name='status',
                description='Filter by transmitter status: ' + ' '.join(TRANSMITTER_STATUS),
                required=False,
                type=OpenApiTypes.STR,
                examples=[OpenApiExample('active', value='\'active\'')]
            ),
            OpenApiParameter(
                name='service',
                description='Filter by transmitter service: ' + ' '.join(SERVICE_TYPE),
                required=False,
                type=OpenApiTypes.STR,
                examples=[OpenApiExample('Amateur', value='\'Amateur\'')]
            ),
            OpenApiParameter(
                name='type',
                description='Filter by transmitter type: ' + ' '.join(TRANSMITTER_TYPE),
                required=False,
                type=OpenApiTypes.STR,
                examples=[OpenApiExample('Transmitter', value='\'Transmitter\'')]
            ),
        ],
    ),
)
class TransmitterViewSet(  # pylint: disable=R0901
        mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin,
        viewsets.GenericViewSet):
    """
    View into the Transmitter entities in the SatNOGS DB database.
    Transmitters are inclusive of Transceivers and Transponders
    """
    renderer_classes = [
        JSONRenderer, BrowsableAPIRenderer, JSONLDRenderer, BrowserableJSONLDRenderer
    ]
    parser_classes = [JSONLDParser]
    queryset = Transmitter.objects.filter(
        satellite__satellite_entry__approved=True, satellite__associated_satellite__isnull=True
    ).exclude(status='invalid')
    serializer_class = serializers.TransmitterSerializer
    filterset_class = filters.TransmitterViewFilter
    lookup_field = 'uuid'

    def create(self, request, *args, **kwargs):  # noqa: C901; pylint: disable=R0911,R0912,R0915
        """
        Creates a transmitter suggestion.
        """
        transmitters_data = []
        for transmitter_entry in request.data['@graph']:
            if 'transmitter' not in transmitter_entry:
                data = 'Transmitter Entry without "transmitter" key'
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            if not transmitter_entry['transmitter']:
                data = 'One or more of the required fields are missing.\n Required fields: \
                        description, status, citation, service, satellite'

                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            transmitter = transmitter_entry['transmitter']

            transmitter_data = {}
            if "@id" not in transmitter:
                data = 'Missing "@id" for one or more entries'
                return Response(data, status=status.HTTP_400_BAD_REQUEST)

            if 'uuid' in transmitter:
                if isinstance(transmitter['uuid'], list):
                    data = 'Multiple values for "http://schema.org/identifier" or multiple \
                            entries with the same "@id" and different \
                            "http://schema.org/identifier" values'

                    return Response(data, status=status.HTTP_400_BAD_REQUEST)
                transmitter_uuid = transmitter['uuid']
                if Transmitter.objects.filter(uuid=transmitter_uuid).exists():
                    transmitter_data['uuid'] = transmitter_uuid

            transmitter_data['description'] = transmitter['description']
            transmitter_data['status'] = transmitter['status']
            transmitter_data['citation'] = transmitter['citation']
            transmitter_data['service'] = transmitter['service']
            transmitter_data['coordination'] = ''
            transmitter_data['coordination_url'] = ''
            transmitter_data['created_by'] = request.user.pk

            try:
                if transmitter['satellite']:
                    if isinstance(transmitter['satellite'], list):
                        data = 'Multiple values for "https://schema.space/metasat/satellite" \
                                or multiple entries with the same "@id" and different \
                                "https://schema.space/metasat/satellite" values'

                        return Response(data, status=status.HTTP_400_BAD_REQUEST)
                    transmitter_data['satellite'] = Satellite.objects.get(
                        satellite_entry__norad_cat_id=transmitter['satellite']['norad_cat_id']
                    ).pk
                else:
                    data = 'Missing NORAD ID value for Satellite'
                    return Response(data, status=status.HTTP_400_BAD_REQUEST)
            except Satellite.DoesNotExist:
                data = 'Unknown NORAD ID: {}'.format(transmitter['satellite']['norad_cat_id'])
                return Response(data, status=status.HTTP_400_BAD_REQUEST)

            if 'baud' in transmitter:
                transmitter_data['baud'] = transmitter['baud']

            if 'invert' in transmitter:
                transmitter_data['invert'] = transmitter['invert']

            if 'uplink' not in transmitter and 'downlink' not in transmitter:
                data = 'Missing "https://schema.space/metasat/uplink" or \
                            "https://schema.space/metasat/downlink"'

                return Response(data, status=status.HTTP_400_BAD_REQUEST)

            if 'uplink' in transmitter:
                if isinstance(transmitter['uplink'], list):
                    data = 'Multiple values for "https://schema.space/metasat/uplink" or multiple \
                            entries with the same "@id" and different \
                            "https://schema.space/metasat/uplink" values'

                    return Response(data, status=status.HTTP_400_BAD_REQUEST)
                if 'frequency' not in transmitter['uplink']:
                    data = 'Missing "https://schema.space/metasat/frequency" from \
                            "https://schema.space/metasat/uplink" value'

                    return Response(data, status=status.HTTP_400_BAD_REQUEST)
                if isinstance(transmitter['uplink']['frequency'], int):
                    transmitter_data['type'] = 'Transceiver'
                    transmitter_data['uplink_low'] = transmitter['uplink']['frequency']
                else:
                    transmitter_data['type'] = 'Transponder'
                    if 'minimum' not in transmitter['uplink'][
                            'frequency'] or 'maximum' not in transmitter['uplink']['frequency']:
                        data = 'Missing "https://schema.org/minimum" or \
                                "https://schema.org/maximum" from \
                                "https://schema.space/metasat/frequency" value of \
                                "https://schema.space/metasat/uplink"'

                        return Response(data, status=status.HTTP_400_BAD_REQUEST)
                    transmitter_data['uplink_low'] = transmitter['uplink']['frequency']['minimum']
                    transmitter_data['uplink_high'] = transmitter['uplink']['frequency']['maximum']
                if 'mode' in transmitter['uplink']:
                    try:
                        transmitter_data['uplink_mode'] = Mode.objects.get(
                            name=transmitter['uplink']['mode']
                        ).pk
                    except Mode.DoesNotExist:
                        data = 'Unknown Mode: {}'.format(transmitter['uplink']['mode'])
                        return Response(data, status=status.HTTP_400_BAD_REQUEST)
                if 'drift' in transmitter['uplink']:
                    transmitter_data['uplink_drift'] = transmitter['uplink']['drift']
            else:
                transmitter_data['type'] = 'Transmitter'

            if 'downlink' in transmitter:
                if isinstance(transmitter['downlink'], list):
                    data = 'Multiple values for "https://schema.space/metasat/downlink" or \
                            multiple entries with the same "@id" and different \
                            "https://schema.space/metasat/downlink" values'

                    return Response(data, status=status.HTTP_400_BAD_REQUEST)
                if 'frequency' not in transmitter['downlink']:
                    data = 'Missing "https://schema.space/metasat/frequency" from \
                            "https://schema.space/metasat/downlink" value'

                    return Response(data, status=status.HTTP_400_BAD_REQUEST)
                if isinstance(transmitter['downlink']['frequency'],
                              int) and not transmitter_data['type'] == 'Transponder':
                    transmitter_data['downlink_low'] = transmitter['downlink']['frequency']
                elif transmitter_data['type'] == 'Transponder':
                    if 'minimum' not in transmitter['downlink'][
                            'frequency'] or 'maximum' not in transmitter['downlink']['frequency']:
                        data = 'Missing "https://schema.org/minimum" or \
                                "https://schema.org/maximum" from \
                                "https://schema.space/metasat/frequency" value of \
                                "https://schema.space/metasat/downlink"'

                        return Response(data, status=status.HTTP_400_BAD_REQUEST)
                    transmitter_data['downlink_low'] = transmitter['downlink']['frequency'][
                        'minimum']
                    transmitter_data['downlink_high'] = transmitter['downlink']['frequency'][
                        'maximum']
                else:
                    data = 'Expected integer for "https://schema.space/metasat/frequency" value \
                            of "https://schema.space/metasat/downlink"'

                    return Response(data, status=status.HTTP_400_BAD_REQUEST)
                if 'mode' in transmitter['downlink']:
                    try:
                        transmitter_data['downlink_mode'] = Mode.objects.get(
                            name=transmitter['downlink']['mode']
                        ).pk
                    except Mode.DoesNotExist:
                        data = 'Unknown Mode: {}'.format(transmitter['downlink']['mode'])
                        return Response(data, status=status.HTTP_400_BAD_REQUEST)
                if 'drift' in transmitter['downlink']:
                    transmitter_data['downlink_drift'] = transmitter['downlink']['drift']
            transmitters_data.append(transmitter_data)

        serializer = serializers.TransmitterEntrySerializer(
            data=transmitters_data, many=True, allow_empty=True
        )
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_201_CREATED)


class LatestTleSetViewSet(viewsets.ReadOnlyModelViewSet):  # pylint: disable=R0901
    """
    Read-only view into the most recent two-line elements (TLE) in the SatNOGS DB
    database
    """
    renderer_classes = [JSONRenderer, BrowsableAPIRenderer]
    queryset = LatestTleSet.objects.all().select_related('satellite').exclude(
        latest_distributable__isnull=True
    ).annotate(
        tle0=F('latest_distributable__tle0'),
        tle1=F('latest_distributable__tle1'),
        tle2=F('latest_distributable__tle2'),
        tle_source=F('latest_distributable__tle_source'),
        updated=F('latest_distributable__updated')
    )
    serializer_class = serializers.LatestTleSetSerializer
    filterset_class = filters.LatestTleSetViewFilter

    def get_queryset(self):
        """
        Returns latest TLE queryset depending on user permissions
        """
        if self.request.user.has_perm('base.access_all_tles'):
            return LatestTleSet.objects.all().select_related('satellite').exclude(
                latest__isnull=True
            ).annotate(
                tle0=F('latest__tle0'),
                tle1=F('latest__tle1'),
                tle2=F('latest__tle2'),
                tle_source=F('latest__tle_source'),
                updated=F('latest__updated')
            )
        return self.queryset


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name='app_source',
                description='The submission source for the telemetry frames: manual (a manual \
                             upload/entry), network (SatNOGS Network observations), or sids \
                             (legacy API submission)',
            ),
            OpenApiParameter(
                name='observer',
                description='(string) name of the observer (submitter) to retrieve telemetry data \
                            from'
            ),
            OpenApiParameter(
                name='satellite',
                description='NORAD ID of a satellite to filter telemetry data for',
                examples=[ISS_EXAMPLE],
            ),
            OpenApiParameter(name='transmitter', description='Not currently in use'),
        ],
    ),
)
class TelemetryViewSet(  # pylint: disable=R0901,R0912,R0915
        mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin,
        viewsets.GenericViewSet):
    """
    View into the Telemetry objects in the SatNOGS DB database. Currently,
    this table is inclusive of all data collected from satellite downlink
    observations
    """
    renderer_classes = [
        JSONRenderer, BrowsableAPIRenderer, JSONLDRenderer, BrowserableJSONLDRenderer
    ]
    queryset = DemodData.objects.all().select_related('satellite', 'transmitter')
    serializer_class = serializers.TelemetrySerializer
    filterset_class = filters.TelemetryViewFilter
    permission_classes = [SafeMethodsWithPermission]
    parser_classes = (FormParser, MultiPartParser, FileUploadParser)
    pagination_class = pagination.LinkedHeaderPageNumberPagination

    @extend_schema(
        responses={'201': None},  # None
    )
    def create(self, request, *args, **kwargs):
        """
        Creates a frame of telemetry data from a satellite observation.
        """
        # pylint: disable=R0914
        data = {}

        norad_id = request.data.get('noradID')

        try:
            if norad_id:
                satellite = Satellite.objects.get(satellite_entry__norad_cat_id=norad_id)
            else:
                raise ValueError
        except Satellite.DoesNotExist:
            satellite_identifier = SatelliteIdentifier.objects.create()
            satellite_entry = SatelliteEntry.objects.create(
                norad_cat_id=norad_id,
                name='New Satellite',
                satellite_identifier=satellite_identifier,
                created=now()
            )
            satellite = Satellite.objects.create(
                satellite_identifier=satellite_identifier, satellite_entry=satellite_entry
            )
            update_satellite_name.delay(int(norad_id))
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        data['satellite'] = satellite.id
        data['station'] = request.data.get('source')
        data['timestamp'] = request.data.get('timestamp')
        if request.data.get('version'):
            data['version'] = request.data.get('version')
        observation_id = ''
        if request.data.get('observation_id'):
            observation_id = request.data.get('observation_id')
            data['observation_id'] = observation_id
        station_id = ''
        if request.data.get('station_id'):
            station_id = request.data.get('station_id')
            data['station_id'] = station_id

        # Convert coordinates to omit N-S and W-E designators
        lat = request.data.get('latitude')
        lng = request.data.get('longitude')
        try:
            if any(x.isalpha() for x in lat):
                data['lat'] = (-float(lat[:-1]) if ('S' in lat) else float(lat[:-1]))
            else:
                data['lat'] = float(lat)
            if any(x.isalpha() for x in lng):
                data['lng'] = (-float(lng[:-1]) if ('W' in lng) else float(lng[:-1]))
            else:
                data['lng'] = float(lng)
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # Network or SiDS submission?
        if request.data.get('satnogs_network'):
            data['app_source'] = 'network'
        else:
            data['app_source'] = 'sids'

        # Create file out of frame string
        frame = ContentFile(request.data.get('frame'), name='sids')
        data['payload_frame'] = frame
        # Create observer
        qth = gridsquare(data['lat'], data['lng'])
        observer = '{0}-{1}'.format(data['station'], qth)
        data['observer'] = observer

        serializer = serializers.SidsSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # Run task to decode the current frame
        decode_current_frame.delay(satellite.satellite_identifier.sat_id, serializer.instance.pk)

        # Run task to publish the current frame via ZeroMQ
        if settings.ZEROMQ_ENABLE:
            publish_current_frame.delay(
                request.data.get('timestamp'), request.data.get('frame'), observer, {
                    'norad_id': norad_id,
                    'observation_id': observation_id,
                    'station_id': station_id
                }
            )

        return Response(status=status.HTTP_201_CREATED)


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'network_obs_id',
                OpenApiTypes.INT64,
                required=False,
                description='Given a SatNOGS Network observation ID, this will return any \
                             artifacts files associated with the observation.'
            ),
        ],
    ),
    retrieve=extend_schema(
        parameters=[
            OpenApiParameter(
                'id',
                OpenApiTypes.URI,
                OpenApiParameter.PATH,
                description='The ID for the requested artifact entry in DB'
            ),
        ],
    ),
)
class ArtifactViewSet(  # pylint: disable=R0901
        mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin,
        viewsets.GenericViewSet):
    """
    Artifacts are file-formatted objects collected from a satellite observation.
    """
    queryset = Artifact.objects.all()
    filterset_class = filters.ArtifactViewFilter
    permission_classes = [IsAuthenticatedOrOptions]
    parser_classes = (FormParser, MultiPartParser)
    pagination_class = pagination.LinkedHeaderPageNumberPagination

    def get_serializer_class(self):
        """Returns the right serializer depending on http method that is used"""
        if self.action == 'create':
            return serializers.NewArtifactSerializer
        return serializers.ArtifactSerializer

    def create(self, request, *args, **kwargs):
        """
        Creates observation artifact from an [HDF5 formatted file][hdf5ref]
        * Requires session or key authentication to create an artifact

        [hdf5ref]: https://en.wikipedia.org/wiki/Hierarchical_Data_Format
        """
        serializer = self.get_serializer(data=request.data)
        try:
            if serializer.is_valid():
                data = serializer.save()
                http_response = {}
                http_response['id'] = data.id
                response = Response(http_response, status=status.HTTP_200_OK)
            else:
                data = serializer.errors
                response = Response(data, status=status.HTTP_400_BAD_REQUEST)
        except (ValidationError, ValueError, OSError) as error:
            response = Response(str(error), status=status.HTTP_400_BAD_REQUEST)
        return response
