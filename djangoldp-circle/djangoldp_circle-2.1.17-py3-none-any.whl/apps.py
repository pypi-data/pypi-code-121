from django.apps import AppConfig
from django.db.models.signals import post_save
from django.dispatch import receiver

from djangoldp_circle.models import Circle


class DjangoldpCircleConfig(AppConfig):
    name = 'djangoldp_circle'

