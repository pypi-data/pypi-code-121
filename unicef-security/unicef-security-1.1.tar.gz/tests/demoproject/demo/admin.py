from django.contrib import admin

from unicef_security.admin import UserAdminPlus

from .models import User


@admin.register(User)
class UserPlus(UserAdminPlus):
    pass
