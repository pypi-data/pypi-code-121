import factory  # type: ignore
from django.contrib.auth import get_user_model
from factory.django import DjangoModelFactory  # type: ignore


class UserFactory(DjangoModelFactory):
    class Meta:
        model = get_user_model()

    username = factory.Sequence(lambda n: "user{}".format(n))
    is_active = True
    is_staff = True
