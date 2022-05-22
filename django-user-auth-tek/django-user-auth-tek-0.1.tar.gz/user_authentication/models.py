import uuid
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from phonenumber_field.modelfields import PhoneNumberField
from django.core.validators import RegexValidator
import os
os.getcwd()
from apps.base_model import BaseModel

# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        """
        Create and return a `User` with an email, username and password.
        """
        if not email:
            raise ValueError("Users Must Have an email address")

        user = self.model(
            email=self.normalize_email(email),
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        Create and return a `User` with superuser (admin) permissions.
        """
        if password is None:
            raise TypeError("Superusers must have a password.")

        user = self.create_user(email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user


class User(AbstractBaseUser):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(
        verbose_name="email address", max_length=255, unique=True
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    isVerified = models.BooleanField(blank=False, default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    # Tells Django that the UserManager class defined above should manage
    # objects of this type.
    objects = UserManager()

    def __str__(self):
        return self.email

    class Meta:
        """
        to set table name in database
        """

        db_table = "login"


class UserProfile(BaseModel):
    """
    to store all other attributes associated to user
    """


    phoneNumberRegex = RegexValidator(regex = r"^\+?1?\d{8,15}$")

    def content_file_name(instance, filename):
        return '/'.join(['profiles', "{0}-{1}".format(str(instance.user.id), filename)])

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    full_name = models.CharField(max_length=50, unique=False)
    phone_number = PhoneNumberField(validators=[phoneNumberRegex], max_length = 16, unique = True, null = True, blank = True)
    dob = models.DateField(null=True)
    zipcode = models.CharField(max_length=10, null=True)
    bio = models.TextField(null=True)
    url = models.CharField(max_length=255, null=True)
    scan_id = models.UUIDField(unique= True, default=uuid.uuid4, editable=False)
    id_num = models.CharField(unique= True, max_length=100, null=True)
    profile_image = models.FileField(upload_to=content_file_name, null=True, blank=True)

    class Meta:
        """
        to set table name in database
        """

        db_table = "profile"

