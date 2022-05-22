"""SatNOGS DB django context processors"""
from django.conf import settings
from django.template.loader import render_to_string
from satnogsdecoders import __version__ as satnogsdecoders_version

from db import __version__


def analytics(request):
    """Returns analytics code."""
    if settings.ENVIRONMENT == 'production':
        rendered_string = {'analytics_code': render_to_string('includes/analytics.html')}
    else:
        rendered_string = {'analytics_code': ''}
    return rendered_string


def stage_notice(request):
    """Displays stage notice."""
    if settings.ENVIRONMENT == 'stage':
        rendered_string = {'stage_notice': render_to_string('includes/stage_notice.html')}
    else:
        rendered_string = {'stage_notice': ''}
    return rendered_string


def auth_block(request):
    """Displays auth links local vs auth0."""
    if settings.AUTH0:
        rendered_string = {'auth_block': render_to_string('includes/auth_auth0.html')}
    else:
        rendered_string = {'auth_block': render_to_string('includes/auth_local.html')}
    return rendered_string


def logout_block(request):
    """Displays logout links local vs auth0."""
    if settings.AUTH0:
        rendered_string = {'logout_block': render_to_string('includes/logout_auth0.html')}
    else:
        rendered_string = {'logout_block': render_to_string('includes/logout_local.html')}
    return rendered_string


def login_button(request):
    """Displays login button local vs auth0."""
    if settings.AUTH0:
        rendered_string = {'login_button': render_to_string('includes/login_button_auth0.html')}
    else:
        rendered_string = {'login_button': render_to_string('includes/login_button_local.html')}
    return rendered_string


def version(request):
    """Displays the current satnogs-db version."""
    return {'version': 'Version: {}'.format(__version__)}


def decoders_version(request):
    """Displays the satnogsdecoders version."""
    return {'decoders_version': 'Decoders Version: {}'.format(satnogsdecoders_version)}
