from django.contrib import admin

from .models import HubOauthToken, HubUser, UserCompany

# Register your models here.
@admin.register(UserCompany)
class UserCompanyAdmin(admin.ModelAdmin):
    model = UserCompany
    list_display = ['uuid', 'name']

@admin.register(HubUser)
class HubUserAdmin(admin.ModelAdmin):
    model = HubUser
    list_display = ['user', 'token']

@admin.register(HubOauthToken)
class HubOauthTokenAdmin(admin.ModelAdmin):
    model = HubOauthToken
    list_display = ['uuid', 'expires_in_dt']
