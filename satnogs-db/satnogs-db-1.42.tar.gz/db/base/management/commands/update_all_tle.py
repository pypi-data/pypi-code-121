"""SatNOGS DB django management command to update TLE entries"""
from django.core.management.base import BaseCommand

from db.base.tasks import update_tle_sets


class Command(BaseCommand):
    """django management command to update TLE entries"""
    help = 'Update TLEs for existing Satellites'

    def handle(self, *args, **options):
        update_tle_sets()
