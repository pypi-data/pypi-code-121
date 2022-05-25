from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.datetime_safe import date

from djangoldp.models import Model
from djangoldp.permissions import LDPPermissions, SuperUserPermission


class User(AbstractUser, Model):

    class Meta(AbstractUser.Meta, Model.Meta):
        serializer_fields = ['@id', 'username', 'first_name', 'last_name', 'email', 'userprofile',
                             'conversation_set', 'circle_set', 'projects']
        anonymous_perms = ['view', 'add']
        authenticated_perms = ['inherit', 'change']
        owner_perms = ['inherit']
        rdf_type = 'foaf:user'


class Skill(Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    obligatoire = models.CharField(max_length=255)
    slug = models.SlugField(blank=True, null=True, unique=True)
    date = models.DateTimeField(auto_now_add=True, blank=True)

    def recent_jobs(self):
        return self.joboffer_set.filter(date__gte=date.today())

    class Meta(Model.Meta):
        anonymous_perms = ['view']
        authenticated_perms = ['inherit', 'add', 'change']
        owner_perms = ['inherit', 'delete', 'control']
        serializer_fields = ["@id", "title", "recent_jobs", "slug", "obligatoire"]
        lookup_field = 'slug'
        rdf_type = 'hd:skill'


class JobOffer(Model):
    title = models.CharField(max_length=255, null=True)
    skills = models.ManyToManyField(Skill, blank=True)
    slug = models.SlugField(blank=True, null=True, unique=True)
    date = models.DateTimeField(auto_now_add=True, blank=True)

    def recent_skills(self):
        return self.skills.filter(date__gte=date.today())

    def some_skill(self):
        return self.skills.all().first()

    class Meta(Model.Meta):
        anonymous_perms = ['view']
        authenticated_perms = ['inherit', 'change', 'add']
        owner_perms = ['inherit', 'delete', 'control']
        serializer_fields = ["@id", "title", "skills", "recent_skills", "resources", "slug", "some_skill", "urlid"]
        container_path = "job-offers/"
        lookup_field = 'slug'
        rdf_type = 'hd:joboffer'


class Conversation(models.Model):
    description = models.CharField(max_length=255, blank=True, null=True)
    author_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    peer_user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, related_name="peers_conv",
                                  on_delete=models.DO_NOTHING)
    observers = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='observed_conversations')

    class Meta(Model.Meta):
        anonymous_perms = ['view']
        authenticated_perms = ['inherit', 'add']
        owner_perms = ['inherit', 'change', 'delete', 'control']
        owner_field = 'author_user'


class Resource(Model):
    joboffers = models.ManyToManyField(JobOffer, blank=True, related_name='resources')
    description = models.CharField(max_length=255)

    class Meta(Model.Meta):
        anonymous_perms = ['view', 'add', 'delete', 'change', 'control']
        authenticated_perms = ['inherit']
        owner_perms = ['inherit']
        serializer_fields = ["@id", "joboffers"]
        depth = 1
        rdf_type = 'hd:Resource'


# a resource in which only the owner has permissions (for testing owner permissions)
class OwnedResource(Model):
    description = models.CharField(max_length=255, blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, related_name="owned_resources",
                             on_delete=models.CASCADE)

    class Meta(Model.Meta):
        anonymous_perms = []
        authenticated_perms = []
        owner_perms = ['view', 'delete', 'add', 'change', 'control']
        owner_field = 'user'
        serializer_fields = ['@id', 'description', 'user']
        depth = 1


class OwnedResourceVariant(Model):
    description = models.CharField(max_length=255, blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, related_name="owned_variant_resources",
                             on_delete=models.CASCADE)

    class Meta(Model.Meta):
        anonymous_perms = []
        authenticated_perms = ['view', 'change']
        owner_perms = ['view', 'delete', 'add', 'change', 'control']
        owner_field = 'user'
        serializer_fields = ['@id', 'description', 'user']
        depth = 1


class UserProfile(Model):
    description = models.CharField(max_length=255, blank=True, null=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='userprofile', on_delete=models.CASCADE)
    slug = models.SlugField(blank=True, null=True, unique=True)

    class Meta(Model.Meta):
        anonymous_perms = ['view']
        authenticated_perms = ['inherit']
        owner_perms = ['inherit', 'change', 'control']
        owner_field = 'user'
        lookup_field = 'slug'
        serializer_fields = ['@id', 'description', 'settings', 'user', 'post_set']
        depth = 1


class NotificationSetting(Model):
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name="settings")
    receiveMail = models.BooleanField(default=True)

    class Meta(Model.Meta):
        anonymous_perms = ['view', 'change']
        authenticated_perms = ['inherit']
        owner_perms = ['inherit', 'change', 'control']


class Message(models.Model):
    text = models.CharField(max_length=255, blank=True, null=True)
    conversation = models.ForeignKey(Conversation, on_delete=models.DO_NOTHING)
    author_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)

    class Meta(Model.Meta):
        anonymous_perms = ['view']
        authenticated_perms = ['inherit', 'add']
        owner_perms = ['inherit', 'change', 'delete', 'control']


class Dummy(models.Model):
    some = models.CharField(max_length=255, blank=True, null=True)
    slug = models.SlugField(blank=True, null=True, unique=True)

    class Meta(Model.Meta):
        anonymous_perms = ['view']
        authenticated_perms = ['inherit', 'add']
        owner_perms = ['inherit', 'change', 'delete', 'control']


class LDPDummy(Model):
    some = models.CharField(max_length=255, blank=True, null=True)

    class Meta(Model.Meta):
        anonymous_perms = ['view']
        authenticated_perms = ['inherit', 'add']
        owner_perms = ['inherit', 'change', 'delete', 'control']


# model used in django-guardian permission tests (no anonymous etc permissions set)
class PermissionlessDummy(Model):
    some = models.CharField(max_length=255, blank=True, null=True)
    slug = models.SlugField(blank=True, null=True, unique=True)
    parent = models.ForeignKey(LDPDummy, on_delete=models.DO_NOTHING, related_name="anons", blank=True, null=True)

    class Meta(Model.Meta):
        anonymous_perms = []
        authenticated_perms = []
        owner_perms = []
        permissions = (
            ('custom_permission_permissionlessdummy', 'Custom Permission'),
        )


class Post(Model):
    content = models.CharField(max_length=255)
    author = models.ForeignKey(UserProfile, blank=True, null=True, on_delete=models.SET_NULL)
    peer_user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, related_name="peers_post",
                                  on_delete=models.SET_NULL)

    class Meta(Model.Meta):
        auto_author = 'author'
        auto_author_field = 'userprofile'
        anonymous_perms = ['view', 'add', 'delete', 'add', 'change', 'control']
        authenticated_perms = ['inherit']
        owner_perms = ['inherit']
        rdf_type = 'hd:post'


class Invoice(Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    date = models.DateField(blank=True, null=True)

    class Meta(Model.Meta):
        depth = 2
        anonymous_perms = ['view']
        authenticated_perms = ['inherit', 'add', 'change']
        owner_perms = ['inherit', 'delete', 'control']


class Circle(Model):
    name = models.CharField(max_length=255, blank=True)
    description = models.CharField(max_length=255, blank=True)
    team = models.ManyToManyField(settings.AUTH_USER_MODEL, through="CircleMember", blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="owned_circles", on_delete=models.DO_NOTHING, null=True, blank=True)

    class Meta(Model.Meta):
        anonymous_perms = ['view', 'add', 'delete', 'add', 'change', 'control']
        authenticated_perms = ["inherit"]
        serializer_fields = ['@id', 'name', 'description', 'members', 'team', 'owner', 'space']
        rdf_type = 'hd:circle'


class Space(Model):
    name = models.CharField(max_length=255, blank=True)
    circle = models.OneToOneField(to=Circle, null=True, blank=True, on_delete=models.CASCADE, related_name='space')

    class Meta(Model.Meta):
        pass


class Batch(Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='batches')
    title = models.CharField(max_length=255, blank=True, null=True)

    class Meta(Model.Meta):
        serializer_fields = ['@id', 'title', 'invoice', 'tasks']
        anonymous_perms = ['view', 'add']
        authenticated_perms = ['inherit', 'add']
        owner_perms = ['inherit', 'change', 'delete', 'control']
        depth = 1
        rdf_type = 'hd:batch'


class CircleMember(Model):
    circle = models.ForeignKey(Circle, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="circles")
    is_admin = models.BooleanField(default=False)

    class Meta(Model.Meta):
        container_path = "circle-members/"
        anonymous_perms = ['view', 'add', 'delete', 'add', 'change', 'control']
        authenticated_perms = ['inherit']
        unique_together = ['user', 'circle']
        rdf_type = 'hd:circlemember'


class Task(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=255)

    class Meta(Model.Meta):
        serializer_fields = ['@id', 'title', 'batch']
        anonymous_perms = ['view']
        authenticated_perms = ['inherit', 'add']
        owner_perms = ['inherit', 'change', 'delete', 'control']


class ModelTask(Model, Task):
    class Meta(Model.Meta):
        pass

STATUS_CHOICES = [
    ('Public', 'Public'),
    ('Private', 'Private'),
    ('Archived', 'Archived'),
]

class Project(Model):
    description = models.CharField(max_length=255, null=True, blank=False)
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default='Private', null=True, blank=True)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='projects')

    class Meta(Model.Meta):
        anonymous_perms = ['view', 'add', 'delete', 'add', 'change', 'control']
        authenticated_perms = ["inherit"]
        rdf_type = 'hd:project'


class DateModel(Model):
    excluded = models.CharField(max_length=255, null=True, default='test')
    value = models.DateField()

    class Meta(Model.Meta):
        rdf_type = "hd:date"
        serializer_fields_exclude = ['excluded']


class DateChild(Model):
    parent = models.ForeignKey(DateModel, on_delete=models.CASCADE, related_name='children')

    class Meta(Model.Meta):
        rdf_type = 'hd:datechild'


class MyAbstractModel(Model):
    defaultsomething = models.CharField(max_length=255, blank=True)

    class Meta(Model.Meta):
        permission_classes = [LDPPermissions]
        abstract = True
        rdf_type = "wow:defaultrdftype"


class NoSuperUsersAllowedModel(Model):
    class Meta(Model.Meta):
        anonymous_perms = []
        authenticated_perms = []
        owner_perms = []
        superuser_perms = []
        permission_classes = [LDPPermissions]


class ComplexPermissionClassesModel(Model):
    class Meta(Model.Meta):
        permission_classes = [LDPPermissions, SuperUserPermission]
        superuser_perms = []
