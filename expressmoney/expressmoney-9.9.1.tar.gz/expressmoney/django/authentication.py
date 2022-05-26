from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.utils import timezone
from rest_framework.authentication import TokenAuthentication

User = get_user_model()


class BackendAuthentication(ModelBackend):
    """
    Checks and resets the password
    user.last_name - number of invalid attempts
    """

    @staticmethod
    def authenticate(request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(username=username)
            is_valid = True if settings.DEBUG else user.check_password(password)
            if is_valid:
                user.set_unusable_password()
                user.last_name = 0
                user.last_login = timezone.now()
                user.save()
                return user
            else:
                try:
                    user.last_name = int(user.last_name)
                except ValueError:
                    user.last_name = 0
                user.last_name = int(user.last_name) + 1
                if int(user.last_name) > 3:
                    user.set_unusable_password()
                    user.last_name = 0
                user.save()

        except User.DoesNotExist:
            return None

    @staticmethod
    def get_user(user_id, **kwargs):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


class ServiceAuthentication(TokenAuthentication):
    """
    The Google Gateway API removes the HTTP_AUTHORIZATION header, so we use HTTP_SERVICE_AUTHORIZATION.
    """

    def authenticate(self, request):
        request.META.update({'HTTP_AUTHORIZATION': request.META.get('HTTP_SERVICE_AUTHORIZATION', b'')})
        return super().authenticate(request)
