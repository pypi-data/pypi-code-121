"""
    django command to install audit permissions
"""
from django.core.management.base import BaseCommand

from django_auditmatic.install.audit_permission import install_audit_permission


class Command(BaseCommand):
    """
    install_audit command
    """

    help = "Installs audit table and triggers for the configured models."

    def add_arguments(self, parser):
        # parser.add_argument('models', nargs='+', type=str)
        pass

    def handle(self, *args, **options):
        install_audit_permission()
