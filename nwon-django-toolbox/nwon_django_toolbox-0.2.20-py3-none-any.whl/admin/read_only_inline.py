from django.contrib.admin import StackedInline, TabularInline
from polymorphic.admin import StackedPolymorphicInline


class ReadOnlyTabularInline(TabularInline):
    readonly_fields = []

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class ReadOnlyStackedInline(StackedInline):
    readonly_fields = []

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class ReadOnlyPolymorphicStackedInline(StackedPolymorphicInline):
    readonly_fields = []

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


__all__ = [
    "ReadOnlyTabularInline",
    "ReadOnlyStackedInline",
    "ReadOnlyPolymorphicStackedInline",
]
