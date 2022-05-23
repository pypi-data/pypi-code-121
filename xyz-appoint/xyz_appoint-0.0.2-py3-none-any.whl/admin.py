# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals

from django.contrib import admin
from . import models


@admin.register(models.Policy)
class PolicyAdmin(admin.ModelAdmin):
    list_display = ('key', 'name', 'expire_time', 'create_time', 'modify_time')
    search_fields = ('key', 'name')
    list_filter = ('is_active', )

@admin.register(models.Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'policy', 'session_max_age', 'is_active', 'create_time', 'modify_time')
    list_filter = ('is_active', 'policy', )
    raw_id_fields = ('user',)
