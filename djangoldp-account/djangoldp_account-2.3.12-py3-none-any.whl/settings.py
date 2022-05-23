import validators
from django.conf import settings
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt


def userinfo(claims, user):
    # Populate claims dict.
    claims['name'] = '{0} {1}'.format(user.first_name, user.last_name)
    claims['email'] = user.email
    claims['website'] = user.webid()
    claims['webid'] = user.webid()
    claims['preferred_username'] = user.username
    return claims


def sub_generator(user):
    return user.webid()
