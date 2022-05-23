from django.contrib import admin

from . import models

@admin.register(models.Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'creator', 'is_active', 'create_time')
    raw_id_fields = ('creator', )

@admin.register(models.Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'is_active', 'create_time')
    raw_id_fields = ('project', )

@admin.register(models.Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('name', 'group', 'number', 'is_active', 'begin_time', 'end_time', 'create_time')
    raw_id_fields = ('group', )


@admin.register(models.MemberShip)
class MemberShipAdmin(admin.ModelAdmin):
    list_display = ('user_name', 'group', 'is_active', 'create_time')
    raw_id_fields = ('group','user')
    search_fields = ('user_name', )
