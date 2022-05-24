"""AuditAdmin admin file.

Contains all the supported admin models for the AuditModel.

classes:
    AuditNotesInline: EoxSupport AuditAdmin inline class.
    AuditAdmin: EoxSupport AuditModel admin class.
"""
from django.contrib import admin

from eox_audit_model.models import AuditModel, AuditNote


class AuditNotesInline(admin.StackedInline):
    """AuditNotesInline class.

    This class has the ability to edit models on the same page.
    https://docs.djangoproject.com/en/1.11/ref/contrib/admin/#inlinemodeladmin-objects

    This class only allows to view the current registers.

    Attributes:
        model: AuditNote model definition.
        extra: Default fields in admin panel.
    """

    model = AuditNote
    extra = 0
    readonly_fields = ['title', 'description']
    can_delete = False

    def has_add_permission(self, request, obj=None):  # pylint: disable=arguments-differ
        """Adding registers is not allow."""
        return False


class AddAuditNotesInline(admin.StackedInline):
    """AddAuditNotesInline class.

    The class AuditNotesInline only allow to see the current registers, this allows to
    add new notes in the admin panel in order that the staff members could leave some comments
    if that is necessary.

    Attributes:
        model: AuditNote model definition.
        extra: Default fields in admin panel.
    """

    model = AuditNote
    extra = 0

    def has_change_permission(self, request, obj=None):
        """Tecurrent register can not be changed."""
        return False


class AuditAdmin(admin.ModelAdmin):
    """AuditAdmin class.

    Attributes:
        list_display: Displayed fields.
        search_fields: This fields will be used to look for the registers.
        readonly_fields: The audit model must not be modified.
        fields: This allows to define the order in the admin panel.
        list_filter: Define the admin filters.
    """

    def timestamp_microseconds(self, obj):
        """Format date with microseconds"""
        return obj.audit_date_stamp.strftime("%Y-%m-%d %H:%M:%S.%f")

    timestamp_microseconds.short_description = 'Audit date stamp'
    timestamp_microseconds.admin_order_field = 'audit_date_stamp'

    inlines = (AuditNotesInline, AddAuditNotesInline)
    list_display = [
        'status',
        'method_name',
        'action',
        'performer',
        'site',
        'timestamp_microseconds'
    ]

    search_fields = [
        'status',
        'method_name',
        'action',
        'performer',
        'site__domain',
        'ip',
        'captured_logs',
    ]

    readonly_fields = [
        'action',
        'method_name',
        'status',
        'performer',
        'site',
        'captured_logs',
        'input_parameters',
        'output_parameters',
        'traceback_log',
        'timestamp_microseconds',
        'ip',
    ]

    fields = [
        'action',
        'method_name',
        'status',
        'performer',
        'site',
        'input_parameters',
        'output_parameters',
        'captured_logs',
        'traceback_log',
        'timestamp_microseconds',
        'ip',
    ]

    list_filter = ('status',)


admin.site.register(AuditModel, AuditAdmin)
