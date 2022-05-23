import re, unicodedata
import uuid

from urllib.parse import urlparse
from django.conf import settings
from django.core.mail import send_mail
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.template import loader
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.urls import reverse_lazy
from django.utils.deconstruct import deconstructible
from django.utils.translation import ugettext_lazy as _
from importlib import import_module
from djangoldp.models import Model
from djangoldp.permissions import LDPPermissions
from djangoldp_account.permissions import LDPUserPermissions


djangoldp_modules = list(settings.DJANGOLDP_PACKAGES)
user_fields = ['@id', 'first_name', 'groups', 'last_name', 'username', 'email', 'account', 'chatProfile', 'name']

if 'djangoldp_uploader' in settings.DJANGOLDP_PACKAGES:
    user_fields += ['uploadURL']

user_nested_fields = ['account', 'groups', 'chatProfile']
user_empty_containers = []
for dldp_module in djangoldp_modules:
    try:
        module_settings = import_module(dldp_module + '.settings')
        module_user_nested_fields = module_settings.USER_NESTED_FIELDS
        user_fields += module_user_nested_fields
        user_nested_fields += module_user_nested_fields
        user_empty_containers += module_settings.USER_EMPTY_CONTAINERS
    except:
        pass

s_fields = []
s_fields.extend(user_fields)
s_fields.extend(user_nested_fields)


@deconstructible
class UsernameValidator(RegexValidator):
    regex = r'^[\w.+-]+$'
    message = _(
        "Entre un nom d'utilisateur valide. Il ne peut contenir que des lettres, "
        'des chiffres, et les caractères ./+/-/_'
    )
    flags = re.UNICODE


class LDPUser(AbstractUser, Model):
    slug = models.SlugField(unique=True, blank=True, null=True)
    username_validator = UsernameValidator()
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Requiert 150 caractères ou moins. Seulement des lettres, chiffres et les caractères ./+/-/_'),
        validators=[username_validator],
        error_messages={
            'unique': _("Ce nom d'utilisateur est déjà pris."),
        },
    )
    email = models.EmailField(
        _('email address'),
        blank=False,
        null=False,
        unique=True,
        error_messages={
            'unique': _("Un utilisateur avec cette adresse mail existe déjà."),
        },
    )
    # updated automatically on login - the default uri to redirect to if none has been passed
    default_redirect_uri = models.CharField(max_length=5000, blank=True, null=True, help_text='A URL to redirect to (home page) when none other is provided in a request, e.g. on forgot password. This will be automatically updated on login')

    class Meta:
        depth = 1
        verbose_name = _('user')
        verbose_name_plural = _('users')
        rdf_type = 'foaf:user'
        lookup_field = 'slug'
        container_path = 'users'
        owner_field = 'urlid'
        permission_classes = getattr(settings, 'USER_PERMISSION_CLASSES', [LDPUserPermissions])
        nested_fields = user_nested_fields
        serializer_fields = s_fields
        empty_containers = user_empty_containers
        anonymous_perms = getattr(settings, 'USER_ANONYMOUS_PERMISSIONS', [])
        authenticated_perms = getattr(settings, 'USER_AUTHENTICATED_PERMISSIONS', ['inherit'])
        owner_perms = getattr(settings, 'USER_OWNER_PERMISSIONS', ['inherit'])

    def name(self):
        return self.get_full_name()
    
    def uploadURL(self):
        return {"@id": settings.BASE_URL + "/upload/"}

    def webid(self):
        # remote user
        if self.urlid is not None and urlparse(self.urlid).netloc != urlparse(settings.BASE_URL).netloc:
            webid = self.urlid
        else:
            webid = '{0}{1}'.format(settings.BASE_URL, reverse_lazy('ldpuser-detail', kwargs={'slug': self.slug}))
        return webid

    def save(self, *args, **kwargs):
        if self.username == "hubl-workaround-493":
            return
        
        '''
        This is a workaround for the LDPSerializer which enforce the user to post an username when creating a new one
        By setting the username to `generate-an-username` we ensure that the user will have an username in conformity
        with slugify & the federation requirement
        '''
        if self.username == "generate-an-username" and self.first_name + self.last_name != "":
            username = unicodedata.normalize('NFD', self.first_name + self.last_name).encode('ascii', 'ignore').decode().lower().strip('.')
            username = re.sub(r'[\s\!#\$%&\'\*\^`\|~:\[\]\(\)\{\}=@\\/]+', r'-', username).strip('-')
            self.username = username[:min(len(username), 50)]

        if self.password == "":
            self.set_password(uuid.uuid4().hex.upper()[0:8])

        # an unforgivable sin so that I could meet my deadline
        # see issue:
        if self.is_backlink:
            self.email = str(uuid.uuid4()) + "@startinblox.com"

        super(LDPUser, self).save(*args, **kwargs)

    def __str__(self):
        return self.urlid


class Account(Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    slug = models.SlugField(unique=True)
    picture = models.URLField(blank=True, null=True)
    issuer = models.URLField(blank=True, null=True)

    class Meta:
        auto_author = 'user'
        permissions = (
            ('control_account', 'Control'),
        )
        lookup_field = 'slug'
        owner_field = 'user'
        permission_classes = getattr(settings, 'USER_PERMISSION_CLASSES', [LDPUserPermissions])
        anonymous_perms = getattr(settings, 'USER_ANONYMOUS_PERMISSIONS', [])
        authenticated_perms = getattr(settings, 'USER_AUTHENTICATED_PERMISSIONS', ['inherit'])
        owner_perms = getattr(settings, 'USER_OWNER_PERMISSIONS', ['inherit'])

    def __str__(self):
        return '{} ({})'.format(self.user.get_full_name(), self.user.username)


class ChatProfile(Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="chatProfile")
    slug = models.SlugField(unique=True)
    jabberID = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        auto_author = 'user'
        permissions = (
            ('control_chatprofile', 'Control'),
        )
        lookup_field = 'slug'
        owner_field = 'user'
        permission_classes = getattr(settings, 'USER_PERMISSION_CLASSES', [LDPUserPermissions])
        anonymous_perms = getattr(settings, 'USER_ANONYMOUS_PERMISSIONS', [])
        authenticated_perms = getattr(settings, 'USER_AUTHENTICATED_PERMISSIONS', ['inherit'])
        owner_perms = getattr(settings, 'USER_OWNER_PERMISSIONS', ['inherit'])

    def __str__(self):
        return '{} (jabberID: {})'.format(self.user.get_full_name(), self.jabberID)


class OPClient(Model):
    issuer = models.URLField()
    client_id = models.CharField(max_length=255)
    client_secret = models.CharField(max_length=255)

    class Meta(Model.Meta):
        anonymous_perms = []
        authenticated_perms = []
        owner_perms = []

    def __str__(self):
        return '{} ({})'.format(self.issuer, self.client_id)


@receiver(pre_save, sender=settings.AUTH_USER_MODEL)
def pre_create_account(sender, instance, **kwargs):
    if getattr(instance, Model.slug_field(instance)) != instance.username:
        setattr(instance, Model.slug_field(instance), instance.username)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def send_email(sender, instance, created, **kwargs):
    if created and not Model.is_external(instance) and instance.email and getattr(settings, 'EMAIL_ON_ACCOUNT_CREATION', False):
        try:
            on_server = getattr(settings, 'INSTANCE_DEFAULT_CLIENT', getattr(settings, 'JABBER_DEFAULT_HOST', ''))
            html_message = loader.render_to_string(
                'password/email.html',
                {
                    'on': on_server,
                    'password_link': getattr(settings, 'SITE_URL', '') + "/auth/password_reset/",
                    'instance': instance
                }
            )

            send_mail(
                _('Création de compte sur ') + on_server,
                _('Compte créé sur ') + on_server,
                settings.EMAIL_HOST_USER or "noreply@" + settings.JABBER_DEFAULT_HOST,
                [instance.email],
                fail_silently=True,
                html_message=html_message
            )
        except: 
            pass

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_account(sender, instance, created, **kwargs):
    if not Model.is_external(instance):
        if created:
            Account.objects.create(user=instance, slug=instance.username)
            chat_profile = ChatProfile.objects.create(user=instance, slug=instance.username)
            if isinstance(getattr(settings, 'JABBER_DEFAULT_HOST', False), str):
                chat_profile.jabberID = '{}@{}'.format(instance.username, settings.JABBER_DEFAULT_HOST)
                chat_profile.save()
        else:
            try:
                instance.account.slug = instance.username
                instance.account.save()
                instance.chatProfile.slug = instance.username
                instance.chatProfile.save()
            except:
                pass
