from email.policy import default
from tabnanny import verbose
import django_tables2 as tables

from netbox.tables import NetBoxTable, columns
from .models import AppSystem, AppSystemAssignment


class AppSystemTable(NetBoxTable):
    name = tables.Column(linkify=True)

    class Meta(NetBoxTable.Meta):
        model = AppSystem
        fields = ('pk', 'id', 'name', 'description', 'comments')
        default_columns = ('name', 'description')


class AppSystemAssignmentTable(NetBoxTable):
    content_type = columns.ContentTypeColumn(verbose_name='Object type')
    object = tables.Column(linkify=True, orderable=False)
    app_system = tables.Column(linkify=True)
    actions = columns.ActionsColumn(actions=('edit', 'delete'))

    class Meta(NetBoxTable.Meta):
        model = AppSystemAssignment
        fields = ('pk', 'content_type', 'object', 'app_system', 'actions')
        default_columns = ('pk', 'content_type', 'object', 'app_system')
