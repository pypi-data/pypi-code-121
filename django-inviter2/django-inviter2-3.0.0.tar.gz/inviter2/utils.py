from __future__ import unicode_literals

from shortuuid import uuid

from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.http import int_to_base36

from .models import OptOut
from .settings import NAMESPACE, TOKEN_GENERATOR, FROM_EMAIL
from .views import import_attribute


User = get_user_model()
token_generator = import_attribute(TOKEN_GENERATOR)


def create_inactive_user(**initials):
    """Create user with ``is_active`` se to ``False`` and a random password."""
    initials.update(is_active=False)
    user = User.objects.create(**initials)
    user.set_unusable_password()
    user.save()
    return user


def send_invite(invitee, inviter, url=None, opt_out_url=None, **kwargs):
    """
    Send the default invitation email.

    Assembled from ``inviter2/email/subject.txt`` and
    ``inviter2/email/body.txt``

    Both templates will receive all the ``kwargs``.

    :param invitee: The invited user
    :param inviter: The inviting user
    :param url: The invite URL
    :param subject_template: The template to render for the subject
    :param body_template: The template to render for the body
    :param opt_out_url: A URL where users can permanently opt out of
                        invitations
    """
    ctx = {'invitee': invitee, 'inviter': inviter}
    ctx.update(kwargs)
    ctx.update(url=url)
    ctx.update(opt_out_url=opt_out_url)

    subject_template = kwargs.pop('subject_template',
                                  'inviter2/email/subject.txt')
    body_template = kwargs.pop('body_template', 'inviter2/email/body.txt')

    subject = render_to_string(subject_template, ctx)
    body = render_to_string(body_template, ctx)

    # Newlines in subject lines are not allowed
    subject = ' '.join(subject.split('\n'))

    send_mail(subject, body, FROM_EMAIL, [invitee.email])


def invite(email, inviter, user=None, sendfn=send_invite, resend=True,
           **kwargs):
    """
    Invite a given email address.

    Returns a ``(User, sent)`` tuple similar to the Django
    :meth:`django.db.models.Manager.get_or_create` method.

    If a user is passed in, reinvite the user.  For projects that support
    multiple users with the same email address, it is necessary to pass in the
    user to avoid throwing a MultipleObjectsReturned error.

    If a user with ``email`` address does not exist:

    * Creates a user object
    * Set ``user.email = email``
    * Set ``user.is_active = False``
    * Set a random password
    * Send the invitation email
    * Return ``(user, True)``

    If a user with ``email`` address exists and ``user.is_active == False``:

    * Re-send the invitation
    * Return ``(user, True)``

    If a user with ``email`` address exists:

    * Don't send  the invitation
    * Return ``(user, False)``

    If the email address is blocked:

    * Don't send the invitation
    * Return ``(None, False)``

    To customize sending, pass in a new ``sendfn`` function as documented by
    :attr:`inviter2.utils.send_invite`:

    ::

        sendfn = lambda invitee, inviter, **kwargs: 1
        invite("foo@bar.com", request.user, sendfn = sendfn)


    :param email: The email address
    :param inviter: The user inviting the email address
    :param pk: The pk of an existing user to be reinvited.
    :param sendfn: An email sending function. Defaults to
                   :attr:`inviter2.utils.send_invite`
    :param resend: Resend email to users that are not registered yet
    """
    if OptOut.objects.is_blocked(email):
        return None, False
    try:
        if not user:
            user = User.objects.get(email=email)
        if user.is_active:
            return user, False
        if not resend:
            return user, False
    except User.DoesNotExist:
        username_field = getattr(User, 'USERNAME_FIELD', 'username')
        if username_field == 'username':
            user = create_inactive_user(email=email, username=uuid())
        else:
            user = create_inactive_user(email=email)

    url_parts = int_to_base36(user.id), token_generator.make_token(user)
    url = reverse('{}:register'.format(NAMESPACE), args=url_parts)

    opt_out_url = reverse('{}:opt-out'.format(NAMESPACE), args=url_parts)
    kwargs.update(opt_out_url=opt_out_url)

    sendfn(user, inviter, url=url, **kwargs)
    return user, True
