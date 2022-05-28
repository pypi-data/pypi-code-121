"""
    django command to install triggers
"""
from django.core.management.base import BaseCommand

from django_auditmatic.install.audit import install_audit


class Command(BaseCommand):
    """
    install_audit command
    """

    help = "Installs audit table and triggers for the configured models."

    def add_arguments(self, parser):
        # parser.add_argument('models', nargs='+', type=str)
        pass

    def handle(self, *args, **options):
        install_audit()
