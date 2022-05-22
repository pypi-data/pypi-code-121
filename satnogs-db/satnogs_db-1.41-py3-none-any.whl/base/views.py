"""Base django views for SatNOGS DB"""
import logging
from datetime import timedelta

from bootstrap_modal_forms.generic import BSModalCreateView, BSModalFormView, BSModalUpdateView
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.db.models import Count, Max, Prefetch, Q
from django.http import HttpResponse, HttpResponseServerError, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.timezone import now
from django.views.decorators.http import require_POST

from db.base.forms import MergeSatellitesForm, SatelliteCreateForm, SatelliteUpdateForm, \
    TransmitterCreateForm, TransmitterUpdateForm
from db.base.helpers import get_api_token
from db.base.models import DemodData, Satellite, SatelliteEntry, SatelliteIdentifier, \
    SatelliteSuggestion, Transmitter, TransmitterEntry, TransmitterSuggestion
from db.base.tasks import background_cache_statistics, delay_task_with_lock, export_frames, \
    notify_suggestion
from db.base.utils import millify, read_influx

LOGGER = logging.getLogger('db')


def home(request):
    """View to render home page.

    :returns: base/home.html
    """
    prefetch_approved = Prefetch(
        'transmitter_entries', queryset=Transmitter.objects.all(), to_attr='approved_transmitters'
    )
    prefetch_suggested = Prefetch(
        'transmitter_entries',
        queryset=TransmitterSuggestion.objects.all(),
        to_attr='suggested_transmitters'
    )

    newest_sats = Satellite.objects.filter(
        associated_satellite__isnull=True
    ).order_by('-id')[:5].prefetch_related(prefetch_approved, prefetch_suggested)
    # Calculate latest contributors
    latest_data_satellites = []
    found = False
    date_from = now() - timedelta(days=1)
    data_list = DemodData.objects.filter(timestamp__gte=date_from
                                         ).order_by('-pk').select_related('satellite')
    paginator = Paginator(data_list, 50)
    page = paginator.page(1)
    while not found:
        for data in page.object_list:
            if data.satellite.id not in latest_data_satellites:
                latest_data_satellites.append(data.satellite.id)
            if len(latest_data_satellites) > 5:
                found = True
                break
        if page.has_next():
            page = paginator.page(page.next_page_number())
        else:
            break

    # Check if satellite is merged and if it is then show its associated entry.
    latest_data = Satellite.objects.filter(
        associated_satellite__isnull=True
    ).filter(Q(pk__in=latest_data_satellites) | Q(associated_with__pk__in=latest_data_satellites)
             ).prefetch_related(prefetch_approved, prefetch_suggested)

    # Calculate latest contributors
    date_from = now() - timedelta(days=1)
    latest_submitters = DemodData.objects.filter(timestamp__gte=date_from
                                                 ).values('station').annotate(c=Count('station')
                                                                              ).order_by('-c')

    return render(
        request, 'base/home.html', {
            'newest_sats': newest_sats,
            'latest_data': latest_data,
            'latest_submitters': latest_submitters
        }
    )


def transmitters_list(request):
    """View to render transmitters list page.

    :returns: base/transmitters.html
    """
    transmitters = Transmitter.objects.filter(
        satellite__associated_satellite__isnull=True, satellite__satellite_entry__approved=True
    ).exclude(
        status='invalid'
    ).select_related('satellite', 'satellite__satellite_entry', 'satellite__satellite_identifier')

    return render(request, 'base/transmitters.html', {'transmitters': transmitters})


def robots(request):
    """robots.txt handler

    :returns: robots.txt
    """
    data = render(request, 'robots.txt', {'environment': settings.ENVIRONMENT})
    response = HttpResponse(data, content_type='text/plain; charset=utf-8')
    return response


def satellites(request):
    """View to render satellites page.

    :returns: base/satellites.html
    """
    satellite_objects = Satellite.objects.filter(
        associated_satellite__isnull=True, satellite_entry__approved=True
    ).select_related('satellite_entry__operator').prefetch_related(
        Prefetch(
            'transmitter_entries',
            queryset=Transmitter.objects.all(),
            to_attr='approved_transmitters'
        )
    ).annotate(
        satellite_suggestions_count=Count(
            'satellite_identifier__satellite_entries',
            filter=Q(satellite_identifier__satellite_entries__reviewed__isnull=True)
        )
    )
    return render(request, 'base/satellites.html', {'satellites': satellite_objects})


def satellite(request, norad=None, sat_id=None):
    """View to render satellite page.

    :returns: base/satellite.html
    """
    if norad:
        satellite_obj = get_object_or_404(Satellite, satellite_entry__norad_cat_id=norad)
    else:
        satellite_obj = get_object_or_404(Satellite, satellite_identifier__sat_id=sat_id)

    if satellite_obj.associated_satellite:
        satellite_obj = satellite_obj.associated_satellite

    latest_tle = None
    latest_tle_set = None
    if hasattr(satellite_obj, 'latest_tle_set'):
        latest_tle_set = satellite_obj.latest_tle_set

    if latest_tle_set:
        if request.user.has_perm('base.access_all_tles'):
            latest_tle = latest_tle_set.latest
        else:
            latest_tle = latest_tle_set.latest_distributable

    transmitter_suggestions = TransmitterSuggestion.objects.filter(satellite=satellite_obj)
    for suggestion in transmitter_suggestions:
        try:
            original_transmitter = satellite_obj.transmitters.get(uuid=suggestion.uuid)
            suggestion.transmitter = original_transmitter
        except Transmitter.DoesNotExist:
            suggestion.transmitter = None

    satellite_suggestions = SatelliteSuggestion.objects.filter(
        satellite_identifier=satellite_obj.satellite_identifier
    )

    try:
        # pull the last 5 observers and their submission timestamps for this
        # satellite and for the satellite that are associated with it
        recent_observers = DemodData.objects.filter(
            Q(satellite=satellite_obj) | Q(satellite__associated_satellite=satellite_obj)
        ).values('observer').annotate(latest_payload=Max('timestamp')
                                      ).order_by('-latest_payload')[:5]
    except (ObjectDoesNotExist, IndexError):
        recent_observers = ''

    # decide whether a map (and map link) will be visible or not (ie: re-entered)
    showmap = False
    if satellite_obj.satellite_entry.status not in ['re-entered', 'future'] and latest_tle:
        showmap = True

    return render(
        request, 'base/satellite.html', {
            'satellite': satellite_obj,
            'latest_tle': latest_tle,
            'transmitter_suggestions': transmitter_suggestions,
            'satellite_suggestions': satellite_suggestions,
            'mapbox_token': settings.MAPBOX_TOKEN,
            'recent_observers': recent_observers,
            'badge_telemetry_count': millify(satellite_obj.telemetry_data_count),
            'showmap': showmap
        }
    )


@login_required
def request_export(request, sat_pk, period=None):
    """View to request frames export download.

    This triggers a request to collect and zip up the requested data for
    download, which the user is notified of via email when the celery task is
    completed.
    :returns: the originating satellite page
    """
    satellite_obj = get_object_or_404(Satellite, id=sat_pk)
    if satellite_obj.associated_satellite:
        satellite_obj = satellite_obj.associated_satellite

    export_frames.delay(satellite_obj.satellite_identifier.sat_id, request.user.id, period)
    messages.success(
        request, ('Your download request was received. '
                  'You will get an email when it\'s ready')
    )
    return redirect(
        reverse('satellite', kwargs={'sat_id': satellite_obj.satellite_identifier.sat_id})
    )


@login_required
@require_POST
def satellite_suggestion_handler(request):
    """Returns the Satellite page after approving or rejecting a suggestion if
    user has approve permission.

    :returns: Satellite page
    """
    satellite_entry = get_object_or_404(SatelliteSuggestion, pk=request.POST['pk'])
    satellite_obj = get_object_or_404(
        Satellite, satellite_identifier=satellite_entry.satellite_identifier
    )
    if request.user.has_perm('base.approve_satellitesuggestion'):
        if 'approve' in request.POST:
            satellite_entry.approved = True
            messages.success(request, ('Satellite approved.'))
        elif 'reject' in request.POST:
            satellite_entry.approved = False
            messages.success(request, ('Satellite rejected.'))
        satellite_entry.reviewed = now()
        satellite_entry.reviewer = request.user
        satellite_entry.save(update_fields=['approved', 'reviewed', 'reviewer'])

        if satellite_entry.approved:
            satellite_obj.satellite_entry = satellite_entry
            satellite_obj.save(update_fields=['satellite_entry'])
    redirect_page = redirect(
        reverse('satellite', kwargs={'sat_id': satellite_obj.satellite_identifier.sat_id})
    )
    return redirect_page


@login_required
@require_POST
def transmitter_suggestion_handler(request):
    """Returns the Satellite page after approving or rejecting a suggestion if
    user has approve permission.

    :returns: Satellite page
    """
    transmitter = get_object_or_404(TransmitterSuggestion, pk=request.POST['pk'])
    if request.user.has_perm('base.approve_transmittersuggestion'):
        if 'approve' in request.POST:
            transmitter.approved = True
            messages.success(request, ('Transmitter approved.'))
        elif 'reject' in request.POST:
            transmitter.approved = False
            messages.success(request, ('Transmitter rejected.'))
        transmitter.reviewed = now()
        transmitter.reviewer = request.user
        transmitter.save(update_fields=['approved', 'reviewed', 'reviewer'])

    redirect_page = redirect(
        reverse('satellite', kwargs={'sat_id': transmitter.satellite.satellite_identifier.sat_id})
    )
    return redirect_page


def about(request):
    """View to render about page.

    :returns: base/about.html
    """
    return render(request, 'base/about.html')


def satnogs_help(request):
    """View to render help modal. Have to avoid builtin 'help' name

    :returns: base/modals/help.html
    """
    return render(request, 'base/modals/satnogs_help.html')


def search(request):
    """View to render search page.

    :returns: base/search.html
    """
    query_string = ''
    results = Satellite.objects.none()
    if ('q' in request.GET) and request.GET['q'].strip():
        query_string = request.GET['q']

    if query_string:
        results = Satellite.objects.filter(
            associated_satellite__isnull=True, satellite_entry__approved=True
        ).filter(
            Q(satellite_entry__name__icontains=query_string)
            | Q(satellite_entry__names__icontains=query_string)
            | Q(satellite_entry__norad_cat_id__icontains=query_string)
            | Q(satellite_identifier__sat_id__icontains=query_string)
            | Q(associated_with__satellite_identifier__sat_id__icontains=query_string)
        ).order_by('satellite_entry__name').prefetch_related(
            Prefetch(
                'transmitter_entries',
                queryset=Transmitter.objects.all(),
                to_attr='approved_transmitters'
            )
        )

    if results.count() == 1:
        return redirect(
            reverse('satellite', kwargs={'sat_id': results[0].satellite_identifier.sat_id})
        )

    return render(request, 'base/search.html', {'results': results, 'q': query_string})


def stats(request):
    """View to render stats page.

    :returns: base/stats.html or base/calc-stats.html
    """
    cached_satellites = []
    ids = cache.get('satellites_ids')
    observers = cache.get('stats_observers')
    if not ids or not observers:
        delay_task_with_lock(background_cache_statistics, 1, 3600)
        return render(request, 'base/calc-stats.html')

    for sid in ids:
        stat = cache.get(sid)
        cached_satellites.append(stat)

    return render(
        request, 'base/stats.html', {
            'satellites': cached_satellites,
            'observers': observers
        }
    )


def statistics(request):
    """Return transmitter cached statistics if the cache exist

    :returns: JsonResponse of statistics
    """
    cached_stats = cache.get('stats_transmitters')
    if not cached_stats:
        cached_stats = []
    return JsonResponse(cached_stats, safe=False)


@login_required
def users_edit(request):
    """View to render user settings page.

    :returns: base/users_edit.html
    """
    token = get_api_token(request.user)
    return render(request, 'base/modals/users_edit.html', {'token': token})


def recent_decoded_cnt(request, norad):
    """Returns a query of InfluxDB for a count of points across a given measurement
    (norad) over the last 30 days, with a timestamp in unixtime.

    :returns: JSON of point counts as JsonResponse
    """
    if settings.USE_INFLUX:
        results = read_influx(norad)
        return JsonResponse(results, safe=False)

    return HttpResponseServerError()


class TransmitterCreateView(LoginRequiredMixin, BSModalCreateView):
    """A django-bootstrap-modal-forms view for creating transmitter suggestions"""
    template_name = 'base/modals/transmitter_create.html'
    model = TransmitterEntry
    form_class = TransmitterCreateForm
    success_message = 'Your transmitter suggestion was stored successfully and will be \
                       reviewed by a moderator. Thanks for contibuting!'

    satellite = Satellite()
    user = get_user_model()

    def dispatch(self, request, *args, **kwargs):
        """
        Overridden so we can make sure the `Satellite` instance exists first
        """
        self.satellite = get_object_or_404(Satellite, pk=kwargs['satellite_pk'])
        self.user = request.user
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """
        Overridden to add the `Satellite` relation to the `Transmitter` instance.
        """
        transmitter = form.instance
        transmitter.satellite = self.satellite
        transmitter.created = now()
        transmitter.created_by = self.user
        # Prevents sending notification twice as form_valid is triggered for validation and saving
        # Check if request is an AJAX one
        if not self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            notify_suggestion.delay(
                transmitter.satellite.satellite_entry.id, self.user.id, 'transmitter'
            )
        return super().form_valid(form)

    def get_success_url(self):
        return self.request.META.get('HTTP_REFERER')


class TransmitterUpdateView(LoginRequiredMixin, BSModalUpdateView):
    """A django-bootstrap-modal-forms view for updating transmitter entries"""
    template_name = 'base/modals/transmitter_update.html'
    model = TransmitterEntry
    form_class = TransmitterUpdateForm
    success_message = 'Your transmitter suggestion was stored successfully and will be \
                       reviewed by a moderator. Thanks for contributing!'

    user = get_user_model()

    def dispatch(self, request, *args, **kwargs):
        self.user = request.user
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        transmitter = form.instance
        # Add update as a new TransmitterEntry object and change fields in order to be a suggestion
        transmitter.pk = None
        transmitter.reviewed = None
        transmitter.reviewer = None
        transmitter.approved = False
        transmitter.created = now()
        transmitter.created_by = self.user
        # Prevents sending notification twice as form_valid is triggered for validation and saving
        # Check if request is an AJAX one
        if not self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            notify_suggestion.delay(
                transmitter.satellite.satellite_entry.id, self.user.id, 'transmitter'
            )
        return super().form_valid(form)

    def get_success_url(self):
        return self.request.META.get('HTTP_REFERER')


class MergeSatellitesView(LoginRequiredMixin, BSModalFormView):
    """Merges satellites if user has merge permission.
    """
    template_name = 'base/modals/satellites_merge.html'
    form_class = MergeSatellitesForm

    user = get_user_model()

    def dispatch(self, request, *args, **kwargs):
        self.user = request.user
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)

        if self.user.has_perm('base.merge_satellites'):
            # Check if request is an AJAX one
            if not self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
                primary_satellite = form.cleaned_data['primary_satellite']
                associated_satellite = form.cleaned_data['associated_satellite']
                associated_satellite.associated_satellite = primary_satellite
                associated_satellite.save(update_fields=['associated_satellite'])
                messages.success(self.request, ('Satellites have been merged!'))
        else:
            messages.error(self.request, ('No permission to merge satellites!'))
            response = redirect(reverse('satellites'))

        return response

    def get_success_url(self):
        return self.request.META.get('HTTP_REFERER')


class SatelliteCreateView(LoginRequiredMixin, BSModalCreateView):
    """A django-bootstrap-modal-forms view for creating satellite suggestions"""
    template_name = 'base/modals/satellite_create.html'
    model = SatelliteEntry
    form_class = SatelliteCreateForm
    success_message = 'Your satellite suggestion was stored successfully and will be \
                       reviewed by a moderator. Thanks for contributing!'

    user = get_user_model()

    def dispatch(self, request, *args, **kwargs):
        self.user = request.user
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        satellite_entry = form.instance
        satellite_obj = None
        # Create Satellite Identifier only when POST request is for saving and
        # NORAD ID is not used by other Satellite.
        # Check if request is an AJAX one
        if not self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                # If the form doesn't contain NORAD ID, create a new satellite
                if satellite_entry.norad_cat_id:
                    satellite_obj = Satellite.objects.get(
                        satellite_entry__norad_cat_id=satellite_entry.norad_cat_id
                    )
                    satellite_entry.satellite_identifier = satellite_obj.satellite_identifier
                else:
                    satellite_entry.satellite_identifier = SatelliteIdentifier.objects.create()
            except Satellite.DoesNotExist:
                satellite_entry.satellite_identifier = SatelliteIdentifier.objects.create()

        satellite_entry.created = now()
        satellite_entry.created_by = self.user

        # form_valid triggers also save() allowing us to use satellite_entry
        # for creating Satellite object, see comment bellow.
        response = super().form_valid(form)

        # Prevents sending notification twice as form_valid is triggered for
        # validation and saving. Also create and Satellite object only when POST
        # request is for saving and NORAD ID is not used by other Satellite.
        # Check if request is an AJAX one
        if not self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            if not satellite_obj:
                satellite_obj = Satellite.objects.create(
                    satellite_identifier=satellite_entry.satellite_identifier,
                    satellite_entry=satellite_entry
                )
            notify_suggestion.delay(satellite_obj.satellite_entry.pk, self.user.id, 'satellite')

        return response

    def get_success_url(self):
        return self.request.META.get('HTTP_REFERER')


class SatelliteUpdateView(LoginRequiredMixin, BSModalUpdateView):
    """A django-bootstrap-modal-forms view for updating satellite entries"""
    template_name = 'base/modals/satellite_update.html'
    model = SatelliteEntry
    form_class = SatelliteUpdateForm
    success_message = 'Your satellite suggestion was stored successfully and will be \
                       reviewed by a moderator. Thanks for contributing!'

    user = get_user_model()

    def dispatch(self, request, *args, **kwargs):
        self.user = request.user
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        satellite_entry = form.instance
        initial_satellite_entry_pk = satellite_entry.pk
        # Add update as a new SatelliteEntry object and change fields in order to be a suggestion
        satellite_entry.pk = None
        satellite_entry.reviewed = None
        satellite_entry.reviewer = None
        satellite_entry.approved = False
        satellite_entry.created = now()
        satellite_entry.created_by = self.user
        # Prevents sending notification twice as form_valid is triggered for validation and saving
        # Check if request is an AJAX one
        if not self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            notify_suggestion.delay(initial_satellite_entry_pk, self.user.id, 'satellite')
        return super().form_valid(form)

    def get_success_url(self):
        return self.request.META.get('HTTP_REFERER')
