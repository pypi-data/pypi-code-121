from django.contrib import admin
from . import models

@admin.register(models.IndyDashConfiguration)
class IndyDashConfigurationAdmin(admin.ModelAdmin):
    filter_horizontal = ['corporations']

