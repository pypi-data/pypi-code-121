"""SatNOGS DB test suites"""
# pylint: disable=R0903,W0612
# flake8: noqa: F841
from datetime import timedelta

import factory
import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User  # pylint: disable=E5142
from django.test import TestCase
from django.utils.timezone import now
from factory import fuzzy
from pytest_django.asserts import assertContains  # pylint: disable=E0611

from db.base.models import DATA_SOURCES, DemodData, Mode, Satellite, SatelliteEntry, \
    SatelliteIdentifier, Telemetry, Transmitter, TransmitterSuggestion

DATA_SOURCE_IDS = [c[0] for c in DATA_SOURCES]


class ModeFactory(factory.django.DjangoModelFactory):
    """Mode model factory."""
    name = fuzzy.FuzzyText(length=8)

    class Meta:
        model = Mode


class UserFactory(factory.django.DjangoModelFactory):
    """User model factory"""
    username = factory.Sequence(lambda n: "user_%d" % n)

    class Meta:
        model = get_user_model()


class SatelliteIdentifierFactory(factory.django.DjangoModelFactory):
    """SatteliteIdentifier model factory."""
    class Meta:
        model = SatelliteIdentifier


class SatelliteEntryFactory(factory.django.DjangoModelFactory):
    """SatteliteEntry model factory."""
    norad_cat_id = fuzzy.FuzzyInteger(200, 48000)
    satellite_identifier = factory.SubFactory(SatelliteIdentifierFactory)
    name = fuzzy.FuzzyText()
    reviewer = factory.SubFactory(UserFactory)
    reviewed = fuzzy.FuzzyDateTime(now() - timedelta(hours=10), now())
    approved = True
    created = fuzzy.FuzzyDateTime(now() - timedelta(days=30), now() - timedelta(hours=10))
    created_by = factory.SubFactory(UserFactory)
    citation = fuzzy.FuzzyText()

    class Meta:
        model = SatelliteEntry


class SatelliteFactory(factory.django.DjangoModelFactory):
    """Sattelite model factory."""
    satellite_identifier = factory.SubFactory(SatelliteIdentifierFactory)
    satellite_entry = factory.SubFactory(SatelliteEntryFactory)

    class Meta:
        model = Satellite


class TransmitterFactory(factory.django.DjangoModelFactory):
    """Transmitter model factory."""
    description = fuzzy.FuzzyText()
    status = fuzzy.FuzzyChoice(choices=['active', 'inactive', 'invalid'])
    type = fuzzy.FuzzyChoice(choices=['Transmitter', 'Transceiver', 'Transponder'])
    uplink_low = fuzzy.FuzzyInteger(200000000, 500000000, step=10000)
    uplink_high = fuzzy.FuzzyInteger(200000000, 500000000, step=10000)
    downlink_low = fuzzy.FuzzyInteger(200000000, 500000000, step=10000)
    downlink_high = fuzzy.FuzzyInteger(200000000, 500000000, step=10000)
    downlink_mode = factory.SubFactory(ModeFactory)
    uplink_mode = factory.SubFactory(ModeFactory)
    invert = fuzzy.FuzzyChoice(choices=[True, False])
    baud = fuzzy.FuzzyInteger(4000, 22000, step=1000)
    satellite = factory.SubFactory(SatelliteFactory)
    approved = True
    created = fuzzy.FuzzyDateTime(now() - timedelta(days=30), now() - timedelta(hours=10))
    reviewed = fuzzy.FuzzyDateTime(now() - timedelta(hours=10), now())
    citation = fuzzy.FuzzyText()
    created_by = factory.SubFactory(UserFactory)
    reviewer = factory.SubFactory(UserFactory)

    class Meta:
        model = Transmitter


class TransmitterSuggestionFactory(factory.django.DjangoModelFactory):
    """TransmitterSuggestion model factory."""
    description = fuzzy.FuzzyText()
    status = fuzzy.FuzzyChoice(choices=['active', 'inactive', 'invalid'])
    type = fuzzy.FuzzyChoice(choices=['Transmitter', 'Transceiver', 'Transponder'])
    uplink_low = fuzzy.FuzzyInteger(200000000, 500000000, step=10000)
    uplink_high = fuzzy.FuzzyInteger(200000000, 500000000, step=10000)
    downlink_low = fuzzy.FuzzyInteger(200000000, 500000000, step=10000)
    downlink_high = fuzzy.FuzzyInteger(200000000, 500000000, step=10000)
    downlink_mode = factory.SubFactory(ModeFactory)
    uplink_mode = factory.SubFactory(ModeFactory)
    invert = fuzzy.FuzzyChoice(choices=[True, False])
    baud = fuzzy.FuzzyInteger(4000, 22000, step=1000)
    satellite = factory.SubFactory(SatelliteFactory)
    approved = False
    created = fuzzy.FuzzyDateTime(now() - timedelta(days=30), now())
    citation = fuzzy.FuzzyText()
    created_by = factory.SubFactory(UserFactory)
    service = fuzzy.FuzzyChoice(
        choices=['Amateur', 'Broadcasting', 'Earth Exploration', 'Fixed', 'Inter-satellite']
    )
    coordination = fuzzy.FuzzyChoice(
        choices=['', 'IARU Requested', 'IARU Declined', 'IARU Coordinated', 'Uncoordinated']
    )

    class Meta:
        model = TransmitterSuggestion


class TelemetryFactory(factory.django.DjangoModelFactory):
    """Telemetry model factory."""
    satellite = factory.SubFactory(SatelliteFactory)
    name = fuzzy.FuzzyText()
    schema = '{}'
    decoder = 'qb50'

    class Meta:
        model = Telemetry


# @pytest.mark.django_db
class DemodDataFactory(factory.django.DjangoModelFactory):
    """DemodData model factory."""
    satellite = factory.SubFactory(SatelliteFactory)
    transmitter = factory.SubFactory(TransmitterFactory)
    app_source = fuzzy.FuzzyChoice(choices=DATA_SOURCE_IDS)
    data_id = fuzzy.FuzzyInteger(0, 200)
    payload_frame = factory.django.FileField(filename='data.raw')
    payload_decoded = '{}'
    payload_telemetry = factory.SubFactory(TelemetryFactory)
    station = fuzzy.FuzzyText()
    lat = fuzzy.FuzzyFloat(-20, 70)
    lng = fuzzy.FuzzyFloat(-180, 180)
    timestamp = fuzzy.FuzzyDateTime(now() - timedelta(days=10), now())

    class Meta:
        model = DemodData


@pytest.mark.django_db(transaction=True)
# class HomeViewTest(TestCase):
#     """
#     Simple test to make sure the home page is working
#     """
def test_home_page(client):
    """Tests the SatNOGS DB home page in an unpopulated state"""
    response = client.get('/')
    assertContains(response, 'no contributions')


@pytest.mark.django_db(transaction=True)
def test_satellite_norad_404(client):
    """Tests for satellite not found by norad ID"""
    response = client.get('/satellite/999999/')
    assert response.status_code == 404


@pytest.mark.django_db(transaction=True)
def test_satellite_id_404(client):
    """Tests for satellite not found by satellite ID"""
    response = client.get('/satellite/AAAA-AAAA-AAAA-AAAA-AAAA/')
    assert response.status_code == 404


@pytest.mark.django_db(transaction=True)
# class AboutViewTest(TestCase):
#     """
#     Test to make sure the about page is working
#     """
def test_about_page(client):
    """Tests for a known string in the SatNOGS DB about page template"""
    response = client.get('/about/')
    assertContains(response, 'SatNOGS DB is an effort to create an hollistic')


@pytest.mark.django_db(transaction=True)
@pytest.mark.usefixtures('celery_session_app')
@pytest.mark.usefixtures('celery_session_worker')
class PopulatedDBTest(TestCase):
    """
    Tests with sample data populated
    """
    def setUp(self):
        self.client.force_login(User.objects.get_or_create(username='testuser')[0])

        # start by creating a bunch of satellite entries
        satellites = []
        satellites = [SatelliteFactory() for i in range(10)]

        # now create transmitters and some DemodData in the past 24h for the satellites
        for sat in range(0, len(satellites) - 1):
            demod = []
            demod = [
                DemodDataFactory(
                    satellite=satellites[sat],
                    timestamp=fuzzy.FuzzyDateTime(now() - timedelta(days=1), now())
                ) for i in range(10)
            ]
            transmitters = []
            transmitters = [TransmitterFactory(satellite=satellites[sat]) for i in range(2)]

        bad_transmitter = TransmitterFactory(status='inactive')
        good_transmitter = TransmitterFactory(status='active')

        # make sure we have a recent demoddata to show
        recent_demod_data = DemodDataFactory(timestamp=now())

        # and the newest satellite with no data
        recent_satellite_entry = SatelliteEntryFactory(created=now())
        recent_satellite = SatelliteFactory(satellite_entry=recent_satellite_entry)

    def test_home_page(self):
        """Tests for known strings in the populated SatNOGS DB home page"""
        response = self.client.get('/')
        assertContains(response, 'Latest data timestamp')
        assertContains(response, 'Data - Last 24h')
        assertContains(response, 'No Data')

    def test_satellites_page(self):
        """Tests for known strings in the populated satellites page"""
        check_sat = Satellite.objects.first()
        response = self.client.get('/satellites/')
        assertContains(response, check_sat.satellite_identifier)

    def test_satellite_by_id(self):
        """Tests for a good satellite entry by satellite ID"""
        check_sat = Satellite.objects.first()
        # go ahead and test transmitter suggestions here too
        TransmitterSuggestionFactory(satellite=check_sat)
        response = self.client.get('/satellite/%s/' % check_sat.satellite_identifier)
        assertContains(response, check_sat.satellite_entry.name)

    def test_satellite_by_norad(self):
        """Tests for a good satellite entry by NORAD ID"""
        check_sat = Satellite.objects.first()
        response = self.client.get('/satellite/%s/' % check_sat.satellite_entry.norad_cat_id)
        assertContains(response, check_sat.satellite_entry.name)

    def test_transmitter_page(self):
        """Tests for known strings in the populated transmitters page"""
        response = self.client.get('/transmitters/')
        assertContains(response, '<td>active</td>')
        assertContains(response, '<td>inactive</td>')

    def test_search_redirect(self):
        """Tests satellite search redirect"""
        check_sat = Satellite.objects.first()
        response = self.client.get('/search/?q=%s' % check_sat.satellite_entry.name)
        assert response.status_code == 302

    def test_multiple_search_results(self):
        """Tests satellite search with multiple results"""
        check_sat = Satellite.objects.first()
        # assume our population has created enough data for multiple hits of 1
        response = self.client.get('/search/?q=1')
        assertContains(response, 'multiple results')

    def test_bad_search(self):
        """Tests satellite search ending in 404"""
        check_sat = Satellite.objects.first()
        response = self.client.get('/search/?q=XXXXXXXXXX')
        assertContains(response, 'No results found')

    def test_stats(self):
        """Tests stats page against count of satellites"""
        # At some point we should force a celery run and test against the total sat cnt
        # refresh statistics first
        refresh = self.client.get('/statistics/')
        response = self.client.get('/stats/')
        assertContains(response, 'calculation')


def test_robots(client):
    """Tests for a known string in the SatNOGS DB about page template"""
    response = client.get('/robots.txt')
    assertContains(response, 'Disallow')


def test_help(client):
    """Tests for a known string in the help modal"""
    response = client.get('/help/')
    assertContains(response, 'You can ask questions')
