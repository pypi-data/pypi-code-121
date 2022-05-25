
from django.contrib import admin

from product_barcode.models import BarCode


@admin.register(BarCode)
class BarCodeAdmin(admin.ModelAdmin):

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
