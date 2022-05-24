
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


def setup_settings(settings, **kwargs):

    settings['STYLESHEETS'] += [
        'jquery.rateit/rateit.css'
    ]

    settings['JAVASCRIPT'] += [
        'reviews/reviews.js',
        'jquery.rateit/jquery.rateit.js',
        'jquery.form.js'
    ]

    settings['INSTALLED_APPS'] += [
        app for app in [
            'reviews',
            'captcha'
        ] if app not in settings['INSTALLED_APPS']
    ]


class ReviewsConfig(AppConfig):
    name = 'reviews'
    verbose_name = _("Reviews")


default_app_config = 'reviews.ReviewsConfig'
