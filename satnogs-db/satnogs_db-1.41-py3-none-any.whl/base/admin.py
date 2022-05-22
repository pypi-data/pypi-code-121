"""Defines functions and settings for the django admin interface"""
from socket import error as socket_error

from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import re_path, reverse
from django.utils.timezone import now

from db.base.models import Artifact, DemodData, ExportedFrameset, LatestTleSet, Mode, Operator, \
    Satellite, SatelliteEntry, SatelliteIdentifier, SatelliteSuggestion, Telemetry, Tle, \
    Transmitter, TransmitterEntry, TransmitterSuggestion
from db.base.tasks import check_celery, decode_all_data, update_tle_sets
from db.base.utils import update_latest_tle_sets


@admin.register(Mode)
class ModeAdmin(admin.ModelAdmin):
    """Defines Mode view in django admin UI"""
    list_display = ('name', )


@admin.register(Operator)
class OperatorAdmin(admin.ModelAdmin):
    """Defines Operator view in django admin UI"""
    list_display = ('name', 'names', 'website')
    search_fields = ('name', 'names')


@admin.register(SatelliteIdentifier)
class SatelliteIdentifierAdmin(admin.ModelAdmin):
    """Defines SatelliteIdentifier view in django admin UI"""
    list_display = ('id', 'sat_id', 'created')
    search_fields = ('sat_id', )

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


@admin.register(SatelliteEntry)
class SatelliteEntryAdmin(admin.ModelAdmin):
    """Defines Satellite Entry view in django admin UI"""
    list_display = (
        'id', 'satellite_identifier', 'name', 'norad_cat_id', 'status', 'decayed',
        'norad_follow_id', 'citation', 'approved', 'created', 'created_by', 'reviewed', 'reviewer'
    )
    search_fields = ('name', 'norad_cat_id', 'norad_follow_id', 'satellite_identifier__sat_id')
    list_filter = ('status', 'decayed', 'reviewed', 'approved', 'satellite_identifier__sat_id')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('satellite_identifier')

    # workaround for readonly CountryField, more at:
    # https://github.com/SmileyChris/django-countries/issues/298
    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if not self.has_change_permission(request):
            try:
                index = fields.index('countries')
                fields[index] = 'countries_str'
            except ValueError:
                pass
        return fields

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        if request.user.has_perm('base.delete_satelliteentry'):
            return True
        return False

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


@admin.register(SatelliteSuggestion)
class SatelliteSuggestionAdmin(admin.ModelAdmin):
    """Defines SatelliteSuggestion view in django admin UI"""
    list_display = (
        'id', 'satellite_identifier', 'name', 'norad_cat_id', 'citation', 'created', 'created_by'
    )
    search_fields = ('name', 'norad_cat_id', 'norad_follow_id', 'satellite_identifier__sat_id')
    list_filter = ('satellite_identifier', )
    actions = ['approve_suggestion', 'reject_suggestion']

    # workaround for readonly CountryField, more at:
    # https://github.com/SmileyChris/django-countries/issues/298
    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if not self.has_change_permission(request):
            try:
                index = fields.index('countries')
                fields[index] = 'countries_str'
            except ValueError:
                pass
        return fields

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def get_actions(self, request):
        """Returns the actions a user can take on a SatelliteSuggestion

        For example, delete, approve, or reject

        :returns: list of actions the user can take on SatelliteSuggestion
        """
        actions = super().get_actions(request)
        if not request.user.has_perm('base.delete_satellitesuggestion'):
            if 'delete_selected' in actions:
                del actions['delete_selected']
        return actions

    def approve_suggestion(self, request, queryset):
        """Returns the SatelliteSuggestion page after approving suggestions

        :param queryset: the SatelliteSuggestion entries to be approved
        :returns: SatelliteSuggestion admin page
        """
        queryset_size = len(queryset)
        for entry in queryset:
            satellite = Satellite.objects.get(satellite_identifier=entry.satellite_identifier)
            entry.approved = True
            entry.reviewed = now()
            entry.reviewer = request.user
            entry.save()
            satellite.satellite_entry = entry
            satellite.save()
        if queryset_size == 1:
            self.message_user(request, "Satellite suggestion was successfully approved")
        else:
            self.message_user(request, "Satellite suggestions were successfully approved")

    approve_suggestion.short_description = 'Approve selected satellite suggestions'

    def reject_suggestion(self, request, queryset):
        """Returns the SatelliteSuggestion page after rejecting suggestions

        :param queryset: the SatelliteSuggestion entries to be rejected
        :returns: SatelliteSuggestion admin page
        """
        queryset_size = len(queryset)
        for entry in queryset:
            entry.approved = False
            entry.reviewed = now()
            entry.reviewer = request.user
            entry.save()
        if queryset_size == 1:
            self.message_user(request, "Satellite suggestion was successfully rejected")
        else:
            self.message_user(request, "Satellite suggestions were successfully rejected")

    reject_suggestion.short_description = 'Reject selected satellite suggestions'


@admin.register(Satellite)
class SatelliteAdmin(admin.ModelAdmin):
    """Defines Satellite view in django admin UI"""
    list_display = (
        'id', 'sat_id', 'associated_satellite', 'last_modified', 'satellite_entry_pk',
        'norad_cat_id', 'name', 'norad_follow_id', 'status', 'decayed'
    )
    search_fields = (
        'satellite_identifier__sat_id', 'satellite_entry__name', 'satellite_entry__norad_cat_id',
        'satellite_entry__norad_follow_id'
    )
    list_filter = ('satellite_entry__status', 'satellite_entry__decayed', 'associated_satellite')

    def get_urls(self):
        """Returns django urls for the Satellite view

        check_celery -- url for the check_celery function
        decode_all_data -- url for the decode_all_data function

        :returns: Django urls for the Satellite admin view
        """
        urls = super().get_urls()
        my_urls = [
            re_path(r'^check_celery/$', self.check_celery, name='check_celery'),
            re_path(
                r'^decode_all_data/(?P<sat_id>[A-Z]{4,4}(?:-\d\d\d\d){4,4})/$',
                self.decode_all_data,
                name='decode_all_data'
            )
        ]
        return my_urls + urls

    def sat_id(self, obj):  # pylint: disable=R0201
        """Return the Satellite Identifier for that satellite"""
        return obj.satellite_identifier.sat_id

    def satellite_entry_pk(self, obj):  # pylint: disable=R0201
        """Return the pk of the Satellite Entry object for that satellite"""
        if obj.satellite_entry:
            return obj.satellite_entry.pk
        return None

    def norad_cat_id(self, obj):  # pylint: disable=R0201
        """Return the satellite NORAD ID"""
        if obj.satellite_entry:
            return obj.satellite_entry.norad_cat_id
        return None

    def norad_follow_id(self, obj):  # pylint: disable=R0201
        """Return the NORAD ID that satellite follows"""
        if obj.satellite_entry:
            return obj.satellite_entry.norad_follow_id
        return None

    def name(self, obj):  # pylint: disable=R0201
        """Return the satellite name"""
        if obj.satellite_entry:
            return obj.satellite_entry.name
        return None

    def status(self, obj):  # pylint: disable=R0201
        """Return the satellite status"""
        if obj.satellite_entry:
            return obj.satellite_entry.status
        return None

    def decayed(self, obj):  # pylint: disable=R0201
        """Return the dacayed date of the satellite"""
        if obj.satellite_entry:
            return obj.satellite_entry.decayed
        return None

    def check_celery(self, request):  # pylint: disable=R0201
        """Returns status of Celery workers

        Check the delay for celery workers, return an error if a connection
        can not be made or if the delay is too long. Otherwise return that
        Celery is OK.

        :returns: admin home page redirect with popup message
        """
        try:
            investigator = check_celery.delay()
        except socket_error as error:
            messages.error(request, 'Cannot connect to broker: %s' % error)
            return HttpResponseRedirect(reverse('admin:index'))

        try:
            investigator.get(timeout=5)
        except investigator.TimeoutError as error:
            messages.error(request, 'Worker timeout: %s' % error)
        else:
            messages.success(request, 'Celery is OK')

        return HttpResponseRedirect(reverse('admin:index'))

    def decode_all_data(self, request, sat_id):  # pylint: disable=R0201
        """Returns the admin home page, while triggering a Celery decode task

        Forces a decode of all data for a Satellite Identifier. This could be very resource
        intensive but necessary when catching a satellite up with a new decoder

        :param sat_id: the Satellite Identifier for the satellite to decode
        :returns: Admin home page
        """
        satellite = Satellite.objects.get(satellite_identifier__sat_id=sat_id)

        # Allow decoding data only for Satellites that are not merged and
        # suggest user trigger decoding for the associated_satellite which will
        # include all DemodData of the satellites that are associated with it
        if satellite.associated_satellite:
            messages.error(
                request,
                'Satellite has been merged, for decoding data trigger "Decode All Data" for "%s"'
                % satellite.associated_satellite
            )
            return redirect(reverse('admin:index'))
        decode_all_data.delay(sat_id)
        messages.success(request, 'Decode task was triggered successfully!')
        return redirect(reverse('admin:index'))

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


@admin.register(TransmitterEntry)
class TransmitterEntryAdmin(admin.ModelAdmin):
    """Defines TransmitterEntry view in django admin UI"""
    list_display = (
        'id', 'uuid', 'description', 'satellite', 'service', 'type', 'downlink_mode',
        'uplink_mode', 'baud', 'downlink_low', 'downlink_high', 'downlink_drift', 'uplink_low',
        'uplink_high', 'uplink_drift', 'citation', 'approved', 'status', 'created', 'created_by',
        'reviewed', 'reviewer'
    )
    search_fields = (
        'uuid', 'satellite__satellite_identifier__sat_id', 'satellite__satellite_entry__name',
        'satellite__satellite_entry__norad_cat_id'
    )
    list_filter = (
        'reviewed',
        'approved',
        'type',
        'status',
        'service',
        'downlink_mode',
        'uplink_mode',
        'baud',
    )

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        if request.user.has_perm('base.delete_transmitterentry'):
            return True
        return False

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


@admin.register(TransmitterSuggestion)
class TransmitterSuggestionAdmin(admin.ModelAdmin):
    """Defines TransmitterSuggestion view in django admin UI"""
    list_display = (
        'uuid', 'description', 'satellite', 'service', 'type', 'downlink_mode', 'uplink_mode',
        'baud', 'downlink_low', 'downlink_high', 'downlink_drift', 'uplink_low', 'uplink_high',
        'uplink_drift', 'citation', 'status', 'created', 'created_by'
    )
    search_fields = (
        'uuid', 'satellite__satellite_identifier__sat_id', 'satellite__satellite_entry__name',
        'satellite__satellite_entry__norad_cat_id'
    )
    list_filter = (
        'type',
        'downlink_mode',
        'uplink_mode',
        'baud',
        'service',
    )
    actions = ['approve_suggestion', 'reject_suggestion']

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def get_actions(self, request):
        """Returns the actions a user can take on a TransmitterSuggestion

        For example, delete, approve, or reject

        :returns: list of actions the user can take on TransmitterSuggestion
        """
        actions = super().get_actions(request)
        if not request.user.has_perm('base.delete_transmittersuggestion'):
            if 'delete_selected' in actions:
                del actions['delete_selected']
        return actions

    def approve_suggestion(self, request, queryset):
        """Returns the TransmitterSuggestion page after approving suggestions

        :param queryset: the TransmitterSuggestion entries to be approved
        :returns: TransmitterSuggestion admin page
        """
        queryset_size = len(queryset)
        for entry in queryset:
            entry.approved = True
            entry.reviewed = now()
            entry.reviewer = request.user
            entry.save()
        if queryset_size == 1:
            self.message_user(request, "Transmitter suggestion was successfully approved")
        else:
            self.message_user(request, "Transmitter suggestions were successfully approved")

    approve_suggestion.short_description = 'Approve selected transmitter suggestions'

    def reject_suggestion(self, request, queryset):
        """Returns the TransmitterSuggestion page after rejecting suggestions

        :param queryset: the TransmitterSuggestion entries to be rejected
        :returns: TransmitterSuggestion admin page
        """
        queryset_size = len(queryset)
        for entry in queryset:
            entry.approved = False
            entry.reviewed = now()
            entry.reviewer = request.user
            entry.save()
        if queryset_size == 1:
            self.message_user(request, "Transmitter suggestion was successfully rejected")
        else:
            self.message_user(request, "Transmitter suggestions were successfully rejected")

    reject_suggestion.short_description = 'Reject selected transmitter suggestions'


@admin.register(Transmitter)
class TransmitterAdmin(admin.ModelAdmin):
    """Defines Transmitter view in django admin UI"""
    list_display = (
        'id', 'uuid', 'description', 'satellite', 'service', 'type', 'downlink_mode',
        'uplink_mode', 'baud', 'downlink_low', 'downlink_high', 'downlink_drift', 'uplink_low',
        'uplink_high', 'uplink_drift', 'citation', 'status', 'created', 'created_by', 'reviewed',
        'reviewer'
    )
    search_fields = (
        'uuid', 'satellite__satellite_identifier__sat_id', 'satellite__satellite_entry__name',
        'satellite__satellite_entry__norad_cat_id'
    )
    list_filter = (
        'type',
        'status',
        'service',
        'downlink_mode',
        'uplink_mode',
        'baud',
    )

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


@admin.register(Tle)
class TleAdmin(admin.ModelAdmin):
    """Define TLE view in django admin UI"""
    list_display = ('satellite_name', 'tle0', 'tle1', 'updated', 'tle_source')
    list_filter = ('tle_source', 'satellite__satellite_entry__name')

    def satellite_name(self, obj):  # pylint: disable=no-self-use
        """Return the satellite name"""
        return obj.satellite.satellite_entry.name

    def get_urls(self):
        """Returns django urls for Tle view

        update_tle_sets -- url for the update_tle_sets function

        :returns: Django urls for the Tle admin view
        """
        urls = super().get_urls()
        my_urls = [
            re_path(r'^update_tle_sets/$', self.update_tle_sets, name='update_tle_sets'),
        ]
        return my_urls + urls

    def update_tle_sets(self, request):  # pylint: disable=R0201
        """Returns the admin home page, while triggering a Celery update tle sets task

        :returns: Admin home page
        """
        update_tle_sets.delay()
        messages.success(request, 'Update TLE sets task was triggered successfully!')
        return redirect(reverse('admin:index'))

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        update_latest_tle_sets(satellite_pks=[obj.satellite.pk])

    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        update_latest_tle_sets(satellite_pks=[obj.satellite.pk])

    def delete_queryset(self, request, queryset):
        satellites = [tle.satellite.pk for tle in queryset]
        super().delete_queryset(request, queryset)
        update_latest_tle_sets(satellite_pks=satellites)


@admin.register(LatestTleSet)
class LatestTleSetAdmin(admin.ModelAdmin):
    """Defines LatestTleSet view in django admin UI"""
    list_display = ('satellite', 'latest', 'latest_distributable', 'last_modified')
    search_fields = (
        'satellite__satellite_identifier__sat_id', 'satellite__satellite_entry__norad_cat_id',
        'satellite__satellite_entry__name'
    )


@admin.register(Telemetry)
class TelemetryAdmin(admin.ModelAdmin):
    """Defines Telemetry view in django admin UI"""
    list_display = ('name', 'decoder', 'satellite')
    search_fields = (
        'satellite__satellite_identifier__sat_id', 'satellite__satellite_entry__norad_cat_id',
        'satellite__satellite_entry__name'
    )


@admin.register(DemodData)
class DemodDataAdmin(admin.ModelAdmin):
    """Defines DemodData view in django admin UI"""
    list_display = ('id', 'satellite', 'app_source', 'observer', 'observation_id', 'station_id')
    search_fields = (
        'transmitter__uuid', 'satellite__satellite_identifier__sat_id',
        'satellite__satellite_entry__norad_cat_id', 'observer', 'observation_id', 'station_id'
    )
    list_filter = (
        'satellite',
        'app_source',
        'observer',
    )

    def satellite(self, obj):  # pylint: disable=R0201
        """Returns the Satellite object associated with this DemodData

        :param obj: DemodData object
        :returns: Satellite object
        """
        return obj.satellite


@admin.register(ExportedFrameset)
class ExportedFramesetAdmin(admin.ModelAdmin):
    """Defines ExportedFrameset view in django admin UI"""
    list_display = ('id', 'created', 'user', 'satellite', 'exported_file', 'start', 'end')
    search_fields = ('user', 'satellite__satellite_entry__norad_cat_id')
    list_filter = ('satellite', 'user')


@admin.register(Artifact)
class ArtifactAdmin(admin.ModelAdmin):
    """Defines Artifact view in django admin UI"""
    list_display = ('id', 'network_obs_id', 'artifact_file')
