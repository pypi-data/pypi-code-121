
from django.apps import apps
from django.conf import settings
from django.contrib import messages
from django.template.loader import render_to_string
from django.contrib.sites.models import Site
from django.core.mail import mail_managers
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _


def get_new_order_context(order):
    return {
        'order': order,
        'title': '{} #{}'.format(_('New order'), order.id),
        'site': Site.objects.get_current(),
        'is_clothes_app_enabled': apps.is_installed('clothes')
    }


def send_new_order_sms(context):
    try:
        from turbosms.lib import send_sms_from_template
        send_sms_from_template('orders/new_order_sms_for_manager.txt', context)
    except ImportError:
        pass
    except Exception as e:
        if settings.DEBUG:
            raise Exception('SMS sending error: {}'.format(e))


def send_new_order_email(context, subject=None):

    if subject is None:
        subject = context.get('title', '')

    html = render_to_string('orders/new_order_email_for_manager.html', context)

    mail_managers(subject=subject, message='', html_message=html)


def push_new_order_message_to_session(request, context):

    message = render_to_string('orders/new_order_message.html', context)

    messages.success(request, mark_safe(message))


def send_new_order_notifications(request, order):

    context = get_new_order_context(order)

    send_new_order_email(context)
    send_new_order_sms(context)

    if not order.is_liqpay_payment():
        push_new_order_message_to_session(request, context)
