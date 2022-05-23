from django.conf import settings
from guardian.utils import get_anonymous_user


# convenience function returns True if user is anonymous
def is_anonymous_user(user):
    return user.is_anonymous or (getattr(settings, 'ANONYMOUS_USER_NAME', True) is not None and
                                 user == get_anonymous_user())


# convenience function returns True if user is authenticated
def is_authenticated_user(user):
    return user.is_authenticated and (getattr(settings, 'ANONYMOUS_USER_NAME', True) is None or
                                      user != get_anonymous_user())
