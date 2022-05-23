"""SatNOGS DB django rest framework Filters class"""
import django_filters
from django_filters import Filter
from django_filters import rest_framework as filters
from django_filters.rest_framework import FilterSet

from db.base.models import SATELLITE_STATUS, Artifact, DemodData, LatestTleSet, Mode, Satellite, \
    Transmitter


class ListFilter(Filter):
    """Custom Filter to use list"""
    def filter(self, qs, value):
        """Returns a QuerySet using list of values as input"""
        if value:
            value_list = value.replace(' ', '').split(u',')
            kwargs = {'{0}__in'.format(self.field_name): value_list}
            return qs.filter(**kwargs)

        return qs


class TransmitterViewFilter(FilterSet):
    """SatNOGS DB Transmitter API View Filter"""
    alive = filters.BooleanFilter(field_name='status', label='Alive', method='filter_status')
    mode = django_filters.ModelChoiceFilter(
        field_name='downlink_mode', lookup_expr='exact', queryset=Mode.objects.all()
    )

    # see https://django-filter.readthedocs.io/en/master/ref/filters.html for
    # W0613
    def filter_status(self, queryset, name, value):  # pylint: disable=W0613,R0201
        """Returns Transmitters that are either functional or non-functional"""
        if value:
            transmitters = queryset.filter(status='active')
        else:
            transmitters = queryset.exclude(status='active')
        return transmitters

    satellite__norad_cat_id = filters.NumberFilter(
        field_name='satellite__satellite_entry__norad_cat_id', label='Satellite NORAD ID'
    )
    sat_id = django_filters.CharFilter(
        method='get_current_sat_transmitter_from_sat_id', label='Satellite ID'
    )

    # pylint: disable=W0613,R0201
    def get_current_sat_transmitter_from_sat_id(self, queryset, field_name, value):
        """Return the transmitter from the parent satellite in case a merged

        satellite id is searched
        """
        if value:
            id_list = value.replace(' ', '').split(u',')
            parent_id_list = []

            qs = Satellite.objects.select_related('associated_satellite').filter(
                satellite_entry__approved=True, satellite_identifier__sat_id__in=id_list
            )

            try:
                sats = qs.all()
                for sat in sats:
                    if sat.associated_satellite is None:
                        parent_id_list.append(sat.id)
                    else:
                        parent_id_list.append(sat.associated_satellite.id)
            except Satellite.DoesNotExist:
                return qs

            return Transmitter.objects.select_related('satellite__associated_satellite').filter(
                satellite__satellite_entry__approved=True, satellite__id__in=parent_id_list
            )

        return queryset

    class Meta:
        model = Transmitter
        fields = [
            'uuid', 'mode', 'uplink_mode', 'type', 'satellite__norad_cat_id', 'alive', 'status',
            'service'
        ]


class SatelliteViewFilter(FilterSet):
    """SatNOGS DB Satellite API View Filter

    filter on decayed field
    """
    in_orbit = filters.BooleanFilter(
        field_name='satellite_entry__decayed', label='In orbit', lookup_expr='isnull'
    )
    status = filters.ChoiceFilter(
        field_name='satellite_entry__status',
        label='Satellite Status',
        choices=list(zip(SATELLITE_STATUS, SATELLITE_STATUS))
    )
    norad_cat_id = filters.NumberFilter(
        field_name='satellite_entry__norad_cat_id', label='Satellite NORAD ID'
    )
    sat_id = django_filters.CharFilter(method='get_current_sat_from_sat_id', label='Satellite ID')

    # pylint: disable=W0613,R0201
    def get_current_sat_from_sat_id(self, queryset, field_name, value):
        """Return the parent Satellite in case a merged

        satellite id is searched
        """
        if value:
            qs = Satellite.objects.select_related('associated_satellite').filter(
                satellite_entry__approved=True, satellite_identifier__sat_id=value
            )
            try:
                sat = qs.get()
                if sat.associated_satellite is None:
                    return qs

                qs = Satellite.objects.filter(
                    satellite_entry__approved=True, id=sat.associated_satellite.id
                )
                return qs
            except Satellite.DoesNotExist:
                return qs

        return queryset

    class Meta:
        model = Satellite
        fields = ['norad_cat_id', 'status', 'in_orbit']


class TelemetryViewFilter(FilterSet):
    """SatNOGS DB Telemetry API View Filter"""
    satellite = django_filters.NumberFilter(
        field_name='satellite__satellite_entry__norad_cat_id',
        lookup_expr='exact',
        label='Satellite NORAD ID'
    )
    sat_id = ListFilter(field_name='satellite__satellite_identifier__sat_id', label='Satellite ID')
    start = django_filters.IsoDateTimeFilter(field_name='timestamp', lookup_expr='gte')
    end = django_filters.IsoDateTimeFilter(field_name='timestamp', lookup_expr='lte')

    class Meta:
        model = DemodData
        fields = ['satellite', 'app_source', 'observer', 'transmitter']


class LatestTleSetViewFilter(FilterSet):
    """SatNOGS DB LatestTleSet API View Filter"""
    norad_cat_id = django_filters.NumberFilter(
        field_name='satellite__satellite_entry__norad_cat_id',
        lookup_expr='exact',
        label='Satellite NORAD ID'
    )
    sat_id = ListFilter(field_name='satellite__satellite_identifier__sat_id', label='Satellite ID')

    class Meta:
        model = LatestTleSet
        fields = ['norad_cat_id']


class ArtifactViewFilter(FilterSet):
    """SatNOGS DB Artifact API View Filter"""
    class Meta:
        model = Artifact
        fields = [
            'network_obs_id',
        ]
