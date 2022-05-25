from __future__ import unicode_literals

import json
import sys

from django import forms
from django.utils.translation import gettext_lazy as _

from .conf import settings


class GeopositionWidget(forms.MultiWidget):
    template_name = 'geoposition/widgets/geoposition.html'

    backends = {
        'google': {
            'js': (
                '//maps.google.com/maps/api/js?key=%s' % settings.GOOGLE_MAPS_API_KEY,
                'geoposition/google.js',
            ),
            'css': (),
        },
        'leaflet': {
            'js': (
                '//unpkg.com/leaflet@1.2.0/dist/leaflet.js',
                '//unpkg.com/leaflet-control-geocoder@1.5.6/dist/Control.Geocoder.js',
                'geoposition/leaflet.js',
            ),
            'css': (
                '//unpkg.com/leaflet@1.2.0/dist/leaflet.css',
                '//unpkg.com/leaflet-control-geocoder@1.5.6/dist/Control.Geocoder.css',
            ),
        }
    }

    def __init__(self, attrs=None):
        self.Media.js = self.backends[settings.BACKEND]['js']
        self.Media.css['all'] = self.backends[settings.BACKEND]['css'] + self.Media.css['all']
        widgets = (
            forms.TextInput(),
            forms.TextInput(),
        )
        super(GeopositionWidget, self).__init__(widgets, attrs)

    def get_config(self):
        return {
            'map_widget_height': settings.MAP_WIDGET_HEIGHT or 500,
            'map_options': json.dumps(settings.MAP_OPTIONS),
            'marker_options': json.dumps(settings.MARKER_OPTIONS),
        }

    def get_context(self, name, value, attrs):
        context = super(GeopositionWidget, self).get_context(name, value, attrs)
        if not isinstance(value, list):
            value = self.decompress(value)
        if 'widget' not in context:
            context['widget'] = {}
        context['widget'].update({
            'latitude': {
                'html': value[0],
                'label': _("latitude"),
            },
            'longitude': {
                'html': value[1],
                'label': _("longitude"),
            },
            'config': {
                'map_widget_height': settings.MAP_WIDGET_HEIGHT or 500,
                'map_options': json.dumps(settings.MAP_OPTIONS),
                'marker_options': json.dumps(settings.MARKER_OPTIONS),
            }
        })
        return context

    def decompress(self, value):
        if isinstance(value, str):
            return value.rsplit(',')
        if value:
            return [value.latitude, value.longitude]
        return [None, None]

    class Media:
        css = {
            'all': ('geoposition/geoposition.css',)
        }
