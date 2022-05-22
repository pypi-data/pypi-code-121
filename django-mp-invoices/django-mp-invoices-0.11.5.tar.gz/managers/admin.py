
from django.contrib import admin
from managers.models import Manager


admin.site.register(Manager, list_display=['name'])
