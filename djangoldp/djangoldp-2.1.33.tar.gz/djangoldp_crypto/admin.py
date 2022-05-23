from django.contrib import admin

from djangoldp_crypto.models import RSAKey


@admin.register(RSAKey)
class RSAKeyAdmin(admin.ModelAdmin):

    readonly_fields = ['kid', 'pub_key']

    def save_model(self, request, obj, form, change):
        obj.priv_key.replace('\r', '')
        super().save_model(request, obj, form, change)
