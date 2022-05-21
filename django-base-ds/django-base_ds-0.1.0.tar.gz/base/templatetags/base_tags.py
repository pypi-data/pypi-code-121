import os
from django.template import Library

import logging
logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(levelname)s: [%(name)s] %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel(logging.ERROR)


register = Library()

# https://localcoder.org/django-inclusion-tag-with-configurable-template


@register.inclusion_tag("base/seo.html", takes_context=True)
def make_seo(context):
    return context


@register.inclusion_tag("base/vendor_css.html", takes_context=True)
def make_vendor_css(context):
    return {
        'vendor_css': make_up_vendor_css(context['theme']),
    }


@register.inclusion_tag("base/vendor_js.html", takes_context=True)
def make_vendor_js(context):
    return {
        'vendor_js': make_up_vendor_js(context['theme']),
    }


@register.inclusion_tag("base/analytics.html", takes_context=True)
def make_analytics(context):
    return {
        'analytics': context['analytics'],
    }


@register.inclusion_tag("base/fonts.html", takes_context=True)
def make_fonts(context, font_link: str):
    return {
        'font_link': font_link
    }


@register.inclusion_tag("base/favicons.html")
def make_favicons():
    return {}


def make_up_vendor_css(theme=None) -> list:
    animate = os.path.join('vendor', 'animate.css', 'animate.min.css')
    bootstrap = os.path.join('vendor', 'bootstrap', 'css', 'bootstrap.min.css')
    bi = os.path.join('vendor', 'bootstrap-icons', 'bootstrap-icons.css')
    bx = os.path.join('vendor', 'boxicons', 'css', 'boxicons.min.css')
    fontawesome = os.path.join('vendor', 'fontawesome-free', 'css', 'all.min.css')
    glightbox = os.path.join('vendor', 'glightbox', 'css', 'glightbox.min.css')
    remixicon = os.path.join('vendor', 'remixicon', 'remixicon.css')
    swiper = os.path.join('vendor', 'swiper', 'swiper-bundle.min.css')
    aos = os.path.join('vendor', 'aos', 'aos.css')

    if theme == 'niceadmin':
        quill_snow = os.path.join('vendor', 'quill', 'quill.snow.css')
        quill_bubble = os.path.join('vendor', 'quill', 'quill.bubble.css')
        simple_db = os.path.join('vendor', 'simple-datatables', 'style.css')
        return [bootstrap, bi, remixicon, bx, quill_snow, quill_bubble, simple_db]

    if theme == 'mentor_ds':
        return [animate, aos, bootstrap, bi, bx, remixicon, swiper]
    elif theme == 'medilab_ds':
        return [animate, bootstrap, bi, bx, fontawesome, glightbox, remixicon, swiper]
    elif theme == 'bethany_ds':
        return [aos, bootstrap, bi, bx, glightbox, remixicon, swiper]
    elif theme == 'medicio_ds':
        return [animate, aos, bootstrap, bi, bx, fontawesome, glightbox, swiper]
    else:
        return [aos, bootstrap, bi, bx, glightbox, remixicon, swiper, aos]


def make_up_vendor_js(theme=None) -> list:
    bootstrap_min = os.path.join('vendor', 'bootstrap', 'js', 'bootstrap.bundle.min.js')
    glightbox = os.path.join('vendor', 'glightbox', 'js', 'glightbox.min.js')
    phpemailform = os.path.join('vendor', 'php-email-form', 'validate.js')
    purecounter = os.path.join('vendor', 'purecounter', 'purecounter.js')
    swiper = os.path.join('vendor', 'swiper', 'swiper-bundle.min.js')
    aos = os.path.join('vendor', 'aos', 'aos.js')
    isotope = os.path.join('vendor', 'isotope-layout', 'isotope.pkgd.min.js')

    if theme == 'niceadmin':
        bootstrap = os.path.join('vendor', 'bootstrap', 'js', 'bootstrap.bundle.js')
        quill = os.path.join('vendor', 'quill', 'quill.min.js')
        tinymce = os.path.join('vendor', 'tinymce', 'tinymce.min.js')
        simple_db = os.path.join('vendor', 'simple-datatables', 'simple-datatables.js')
        chart = os.path.join('vendor', 'chart.js', 'chart.min.js')
        apexcharts = os.path.join('vendor', 'apexcharts', 'apexcharts.min.js')
        echarts = os.path.join('vendor', 'echarts', 'echarts.min.js')
        return [bootstrap, phpemailform, quill, tinymce, simple_db, chart, apexcharts, echarts ]

    if theme == 'mentor_ds':
        return [aos, bootstrap_min, phpemailform, swiper, purecounter]
    elif theme == 'medilab_ds':
        return [bootstrap_min, glightbox, isotope, phpemailform, swiper, purecounter]
    elif theme == 'bethany_ds':
        return [aos, bootstrap_min, glightbox, isotope, phpemailform, swiper, purecounter]
    elif theme == 'medicio_ds':
        return [aos, bootstrap_min, glightbox, phpemailform, purecounter, swiper]
    else:
        return [aos, bootstrap_min, glightbox, isotope, phpemailform, swiper, purecounter]