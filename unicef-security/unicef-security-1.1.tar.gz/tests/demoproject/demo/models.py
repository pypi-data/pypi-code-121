from unicef_security.models import AbstractUser


class User(AbstractUser):

    class Meta(AbstractUser.Meta):
        app_label = 'demo'
