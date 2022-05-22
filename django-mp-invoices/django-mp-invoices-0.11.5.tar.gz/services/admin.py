
from django.contrib import admin

from services import models


@admin.register(models.Service)
class ServiceAdmin(admin.ModelAdmin):

    list_display = ['id', 'created', 'customer', 'item', 'price']


@admin.register(models.ServiceItem)
class ServiceItemAdmin(admin.ModelAdmin):

    search_fields = ['name', 'code']
    list_display = ['id', 'name', 'code', 'price']


@admin.register(models.ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):

    search_fields = ['name']
    list_display = ['id', 'name']


@admin.register(models.ServiceWorker)
class ServiceWorkerAdmin(admin.ModelAdmin):

    search_fields = ['name']
    list_display = ['id', 'name']
