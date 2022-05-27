from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User


class StaticBackend:
	"""
	Authenticate against the setting STATIC_AUTH_CREDENTIALS, which is a dict
	of username -> password pairs. Passwords are stored in plaintext
	(so, it's explicitly insecure).
	"""
	def authenticate(self, request, username=None, password=None):
		if username in settings.STATIC_AUTH_CREDENTIALS:
			if settings.STATIC_AUTH_CREDENTIALS[username] == password:
				return self._get_or_create(username)
		return None

	def _get_or_create(self, username):
		try:
			user = User.objects.get(username=username)
		except User.DoesNotExist:
			# Create a new user. There's no need to set a password
			# because only the password from settings.py is checked.
			user = User(username=username)
			# user.is_staff = True
			# user.is_superuser = True
			user.save()
		return user

	def get_user(self, user_id):
		try:
			return User.objects.get(pk=user_id)
		except User.DoesNotExist:
			return None


# https://docs.djangoproject.com/en/2.1/topics/auth/customizing/#writing-an-authentication-backend
class SettingsBackend:
	"""
	Authenticate against the settings ADMIN_LOGIN and ADMIN_PASSWORD.

	Use the login name and a hash of the password. For example:

	ADMIN_LOGIN = 'admin'
	ADMIN_PASSWORD = 'pbkdf2_sha256$30000$Vo0VlMnkR4Bk$qEvtdyZRWTcOsCnI/oQ7fVOu1XAURIZYoOZ3iq8Dr4M='
	"""

	def authenticate(self, request, username=None, password=None):
		login_valid = (settings.ADMIN_LOGIN == username)
		pwd_valid = check_password(password, settings.ADMIN_PASSWORD)
		if login_valid and pwd_valid:
			try:
				user = User.objects.get(username=username)
			except User.DoesNotExist:
				# Create a new user. There's no need to set a password
				# because only the password from settings.py is checked.
				user = User(username=username)
				user.is_staff = True
				user.is_superuser = True
				user.save()
			return user
		return None

	def get_user(self, user_id):
		try:
			return User.objects.get(pk=user_id)
		except User.DoesNotExist:
			return None
