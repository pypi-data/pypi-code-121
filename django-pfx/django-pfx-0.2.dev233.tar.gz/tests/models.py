from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.core.mail import send_mail
from django.db import models
from django.utils.functional import cached_property

from pfx.pfxcore.decorator import rest_property
from pfx.pfxcore.fields import MediaField, MinutesDurationField
from pfx.pfxcore.models import (
    CacheableMixin,
    CacheDependsMixin,
    PFXModelMixin,
    UniqueConstraint,
)
from pfx.pfxcore.models.pfx_models import JSONReprMixin
from pfx.pfxcore.models.user_filtered_queryset_mixin import (
    UserFilteredQuerySetMixin,
)


class UserManager(BaseUserManager):
    def create_user(
            self, username, email, password, first_name, last_name,
            is_superuser=False):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
            is_superuser=is_superuser
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
            self, username, email, password, first_name, last_name):
        return self.create_user(
            username, email, password, first_name, last_name,
            is_superuser=True)


class User(CacheableMixin, JSONReprMixin, AbstractBaseUser):
    username = models.CharField(
        'username',
        max_length=150,
        unique=True,
        error_messages={
            'unique': "A user with that username already exists.",
        },
    )
    first_name = models.CharField('first name', max_length=150, blank=True)
    last_name = models.CharField('last name', max_length=150, blank=True)
    email = models.EmailField('email address', blank=True)
    is_active = models.BooleanField(
        'active',
        default=True,
    )
    is_superuser = models.BooleanField(
        'is_superuser',
        default=False,
    )

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = UserManager()

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)


class BadUserAuthorQuerySet(UserFilteredQuerySetMixin, models.QuerySet):
    pass


class UserAuthorQuerySet(UserFilteredQuerySetMixin, models.QuerySet):
    def user(self, user):
        if not user.is_superuser:
            return self.exclude(last_name="Tolkien")
        return self


class Author(CacheableMixin, JSONReprMixin, models.Model):
    CACHED_PROPERTIES = ['books_count']

    first_name = models.CharField("First Name", max_length=30)
    last_name = models.CharField("Last Name", max_length=30)
    slug = models.SlugField("Slug", unique=True)
    gender = models.CharField("Gender", max_length=10, choices=[
        ('male', "Male"), ('female', "Female")], default='male')
    science_fiction = models.BooleanField("Science Fiction", default=False)
    created_at = models.DateField("Created at", auto_now_add=True)
    create_comment = models.CharField(
        "Create comment", max_length=255, null=True, blank=True)
    update_comment = models.CharField(
        "Update comment", max_length=255, null=True, blank=True)

    objects = models.QuerySet.as_manager()
    bad_user_objects = BadUserAuthorQuerySet.as_manager()
    user_objects = UserAuthorQuerySet.as_manager()

    class Meta:
        verbose_name = "Author"
        verbose_name_plural = "Authors"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @rest_property("Name Length", "IntegerField")
    def name_length(self):
        return len(str(self))

    @cached_property
    def books_count(self):
        return self.books.count()

    @property
    def books_count_prop(self):
        return self.books.count()


class BookType(CacheDependsMixin, PFXModelMixin, models.Model):
    CACHE_DEPENDS_FIELDS = ['books.author']

    name = models.CharField("Name", max_length=30)
    slug = models.SlugField("Slug")

    class Meta:
        verbose_name = "Book Type"
        verbose_name_plural = "Book Types"

    def __str__(self):
        return f"{self.name}"


class Book(CacheDependsMixin, PFXModelMixin, models.Model):
    CACHE_DEPENDS_FIELDS = ['author']

    name = models.CharField("Name", max_length=100)
    author = models.ForeignKey(
        'tests.Author', on_delete=models.RESTRICT,
        related_name='books', verbose_name="Author")
    type = models.ForeignKey(
        'tests.BookType', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='books', verbose_name="Book Type")
    pub_date = models.DateField("Pub Date")
    created_at = models.DateField("Created at", auto_now_add=True)
    pages = models.IntegerField("Pages", null=True, blank=True)
    rating = models.FloatField("Rating", null=True, blank=True)
    reference = models.CharField(
        "Reference", max_length=30, null=True, blank=True)
    cover = MediaField("Cover", auto_delete=True)
    read_time = MinutesDurationField("Read Time", null=True, blank=True)

    class Meta:
        verbose_name = "Book"
        verbose_name_plural = "Books"
        constraints = [
            UniqueConstraint(
                fields=['author', 'name'],
                name='book_unique_author_and_name',
                message="%(name)s already exists for %(author)s")]

    def __str__(self):
        return f"{self.name}"
