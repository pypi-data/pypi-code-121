from django.contrib import admin

from . import models, helper

@admin.register(models.Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('name', 'source_url', 'is_active',  'create_time')
    search_fields = ("name", 'source_url')
    date_hierarchy = 'create_time'


