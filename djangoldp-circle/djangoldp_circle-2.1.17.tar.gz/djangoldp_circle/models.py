import random
import string
import re
from urllib.parse import urlparse
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.utils.html import strip_tags
from django.db import models
from django.db.models.signals import pre_save, post_save, pre_delete, post_delete
from django.dispatch import receiver
from django.template import loader
from djangoldp.activities.services import ActivityQueueService
from djangoldp.models import Model
from django.utils.encoding import force_text
from djangoldp_circle.permissions import CirclePermissions, CircleMemberPermissions, CircleAccessRequestPermissions
from djangoldp_circle.views import CircleMembersViewset
import logging

logger = logging.getLogger('djangoldp')

MODEL_MODIFICATION_USER_FIELD = 'modification_user'
STATUS_CHOICES = [
    ('Public', 'Public'),
    ('Private', 'Private'),
    ('Archived', 'Archived'),
    ('Restricted', 'Restricted'),
]

# NOTE: the email templates are relying on the names "Accepted" and "Refused"
ACCESS_REQUEST_STATUS_STATES = [
    ('Pending', 'Pending'),
    ('Accepted', 'Accepted'),
    ('Refused', 'Refused'),
]

circle_fields = ["@id", "name", "subtitle", "description", "creationDate", "status", "owner", "jabberID", "jabberRoom", "members", "parentCircle", "children", "access_requests"]
if 'djangoldp_community' in settings.DJANGOLDP_PACKAGES:
    circle_fields += ['community']

if 'djangoldp_polls' in settings.DJANGOLDP_PACKAGES:
    circle_fields += ['polls']

if 'djangoldp_resource' in settings.DJANGOLDP_PACKAGES:
    circle_fields += ['resources']

if 'djangoldp_event' in settings.DJANGOLDP_PACKAGES:
    circle_fields += ['events']

if 'djangoldp_fcpe' in settings.DJANGOLDP_PACKAGES:
    circle_fields += ['space']


class Circle(Model):
    name = models.CharField(max_length=255, blank=True, null=True, default='')
    subtitle = models.CharField(max_length=255, blank=True, null=True, default='')
    description = models.TextField(blank=True, null=True, default='')
    creationDate = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Public')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="owned_circles", on_delete=models.SET_NULL,
                              null=True, blank=True)
    parentCircle = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name='children',
                                     help_text="A circle can optionally be nested within a parent")
    jabberID = models.CharField(max_length=255, blank=True, null=True, unique=True)
    jabberRoom = models.BooleanField(default=True)

    class Meta(Model.Meta):
        empty_containers = ["owner"]
        auto_author = 'owner'
#        depth = 1 # Disabled due to owner being serialized
        permission_classes = [CirclePermissions]
        anonymous_perms = []
        authenticated_perms = []
        owner_perms = []
        serializer_fields = circle_fields
        rdf_type = 'hd:circle'

    def __str__(self):
        try:
            return '{} ({})'.format(self.name, self.urlid)
        except:
            return self.urlid

    def get_admins(self):
        return self.members.filter(is_admin=True)


class CircleMember(Model):
    circle = models.ForeignKey(Circle, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="circles", null=True, blank=True)
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        try:
            return '{} -> {} ({})'.format(self.circle.urlid, self.user.urlid, self.urlid)
        except:
            return self.urlid

    class Meta(Model.Meta):
        container_path = "circle-members/"
        permission_classes = [CircleMemberPermissions]
        anonymous_perms = []
        authenticated_perms = ['view', 'add']
        owner_perms = ['inherit']
        unique_together = ['user', 'circle']
        rdf_type = 'hd:circlemember'
        view_set = CircleMembersViewset

    def save(self, *args, **kwargs):
        if self.user:
            if self.user.username == "hubl-workaround-493":
                self.user = None
        # cannot be duplicated CircleMembers
        if not self.pk and CircleMember.objects.filter(circle=self.circle, user=self.user).exists():
            return

        super(CircleMember, self).save(*args, **kwargs)


class CircleAccessRequest(Model):
    circle = models.ForeignKey(Circle, on_delete=models.CASCADE, related_name='access_requests')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="circle_access_requests")
    status = models.CharField(max_length=8, choices=ACCESS_REQUEST_STATUS_STATES, default='Pending')
    responded_to_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="circle_access_responses")

    # functions used in notification of access request to users
    #  https://git.startinblox.com/djangoldp-packages/djangoldp-notification
    def serialize_notification(self):
        '''serializes into a JSON-LD object for package djangoldp-notification'''
        result = {
            '@id': self.urlid,
            '@type': Model.get_meta(CircleAccessRequest, 'rdf_type'),
            'circle': {
                '@id': self.circle.urlid,
                '@type': Model.get_meta(Circle, 'rdf_type')
            },
            'user': {
                '@id': self.user.urlid,
                '@type': 'foaf:user'
            },
            'status': self.status
        }

        if self.responded_to_by is not None:
            result['responded_to_by'] = {
                '@id': self.responded_to_by.urlid,
                '@type': 'foaf:user'
            }
        
        return result

    class Meta(Model.Meta):
        permission_classes = [CircleAccessRequestPermissions]
        auto_author = 'user'
        anonymous_perms = []
        authenticated_perms = ['add']
        owner_perms = ['add']
        rdf_type = 'hd:circleaccessrequest'


@receiver(post_save, sender=CircleMember)
def fix_user_hubl_workaround_493(sender, instance, **kwargs):
    if not instance.user:
        try:
            request_user = getattr(instance, MODEL_MODIFICATION_USER_FIELD, None)
            if request_user is None:
                raise Exception('request user was unexpectedly None!')
            user = get_user_model().objects.get(pk=request_user.pk)
            instance.user = user
            instance.save()
        except Exception as e:
            logger.error('error in Circle.fix_user_hubl_workaround_493.. ' + str(e))
            if instance.pk is not None:
                instance.delete()

@receiver(pre_save, sender=Circle)
def set_jabberid(sender, instance, **kwargs):
    if getattr(settings, 'JABBER_DEFAULT_HOST', False) and not instance.jabberID:
        instance.jabberID = '{}@conference.{}'.format(
            ''.join(
                [
                    random.choice(string.ascii_letters + string.digits)
                    for n in range(12)
                ]
            ).lower(),
            settings.JABBER_DEFAULT_HOST
        )
        instance.jabberRoom = True

@receiver(post_save, sender=Circle)
def set_owner_as_member(instance, created, **kwargs):
    # add owner as an admin member
    if instance.owner is not None:
        try:
            owner_member = instance.members.get(user=instance.owner)
            if not owner_member.is_admin:
                owner_member.is_admin = True
                owner_member.save()
        except CircleMember.DoesNotExist:
            CircleMember.objects.create(user=instance.owner, circle=instance, is_admin=True)

@receiver(post_delete, sender=CircleMember)
def delete_circle_on_last_member_delete(sender, instance, **kwargs):
    # if this was the last member of the circle, the circle should be deleted too
    if instance.circle.pk is not None and instance.circle.members.count() == 0:
        instance.circle.delete()

@receiver(pre_delete, sender=CircleMember)
def manage_deleted_owner(sender, instance, **kwargs):
    # was the owner removed?
    if instance.user is not None and instance.user == instance.circle.owner:
        # if there are another admin: pick one, set them as owner
        alt = instance.circle.members.filter(is_admin=True).exclude(user=instance.user)[:1]
        if not alt.exists():
            # if there is another member: pick one, set them as owner
            alt = instance.circle.members.all().exclude(user=instance.user)[:1]
        if alt.exists():
            instance.circle.owner = alt[0].user
            instance.circle.save()

@receiver(post_save, sender=CircleAccessRequest)
def create_circle_member_accepted_request(sender, instance, **kwargs):
    if Model.is_external(instance):
        return

    if instance.status == 'Accepted' and not CircleMember.objects.filter(user=instance.user, circle=instance.circle).exists():
        cm = CircleMember(circle=instance.circle, user=instance.user, is_admin=False)
        cm.save()

if 'djangoldp_notification' in settings.DJANGOLDP_PACKAGES:
    from djangoldp_notification.models import Notification, get_default_email_sender_djangoldp_instance

    @receiver(post_save, sender=Notification)
    def send_email_on_notification(sender, instance, created, **kwargs):
        def to_text(html):
            return re.sub('[ \t]+', ' ', strip_tags(html)).replace('\n ', '\n').strip()

        if created \
                and instance.user.email \
                and instance.type == 'CircleAccessRequest':

            email_from = get_default_email_sender_djangoldp_instance()
            can_send_email = email_from and instance.user.settings.receiveMail

            if not can_send_email:
                return

            on = getattr(settings, 'INSTANCE_DEFAULT_CLIENT', False)
            ar = CircleAccessRequest.objects.get(urlid=instance.object)

            # when an access request is created, send a notification to Circle administrators
            if ar.status == 'Pending':
                html_message = render_to_string('accessrequests/access_requested.html', {
                    "instance": ar,
                    'on': on,
                })

                send_mail(
                    _("Someone requested access to your circle"),
                    to_text(html_message),
                    email_from,
                    [instance.user.email],
                    fail_silently = False,
                    html_message = html_message
                )

            # when an access request is resolved, add the user as a CircleMember if approved,
            # and send a notification to the user who made the request
            else:
                html_message = loader.render_to_string(
                    'accessrequests/access_resolved.html',
                    {
                        'on': on,
                        'instance': ar,
                        'accepted': ar.status == "Accepted"
                    }
                )

                email_title = (ar.status == "Accepted") if _("Your access request has been accepted") else  _("Your access request has been refused")
                send_mail(
                    email_title,
                    to_text(html_message),
                    email_from,
                    [instance.user.email],
                    fail_silently=(not settings.DEBUG),
                    html_message=html_message
                )

    @receiver(post_save, sender=CircleAccessRequest)
    def send_notification_for_access_request(sender, instance, created, **kwargs):
        # this signal is fired whenever a local CircleAccessRequest has been saved
        # when it is created, circle administratos will be informed of the request
        # when it has been responded to, the requesting user will be informed

        # only react to local access requests
        # at this point we know that the circle information will be local, but the users might be distant
        if Model.is_external(instance.urlid):
            return

        # build the notification data
        notification_obj = instance.serialize_notification()
        notification_type = "CircleAccessRequest"
        author = instance.user if created else instance.responded_to_by
        author = author.urlid if author is not None else str(_("Auteur inconnu"))
        summary = (instance.status == "Accepted") if _("Your access request has been accepted") else  _("Your access request has been refused")
        if created:
            summary = _('New Circle access request')
            
        notification = {
            "@context": settings.LDP_RDF_CONTEXT,
            "object": notification_obj,
            "author": author,
            "type": notification_type,
            "summary": force_text(summary)
        }

        def discover_circle_access_requests_inbox(target_urlid):
            parsed_url = urlparse(target_urlid)
            
            # TODO: proper inbox discovery
            distant_server_inbox = "{}://{}/circleaccessrequests/inbox/".format(parsed_url.scheme, parsed_url.netloc)
            return distant_server_inbox
        
        def send_notification_to_user(user):
            from djangoldp_notification.models import Notification

            if Model.is_external(user):
                inbox = discover_circle_access_requests_inbox(target.user.urlid)
                ActivityQueueService.send_activity(inbox, notification)
            else:
                Notification.objects.create(user=user, object=notification_obj['@id'], author=author, type=notification_type, summary=summary)

        # our intention is to notify the target user, which is either all admins of a circle (if the request is new)
        # or it is the user who made the request (if the request has been responded to)
        if created:
            for target in instance.circle.members.filter(is_admin=True):
                notification['target'] = target.user.urlid
                send_notification_to_user(target.user)
        elif instance.status != "Pending":
            send_notification_to_user(instance.user)
