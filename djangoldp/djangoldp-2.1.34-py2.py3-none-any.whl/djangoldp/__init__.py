from django.db.models import options

__version__ = '2.1.34'

options.DEFAULT_NAMES += (
    'lookup_field', 'rdf_type', 'rdf_context', 'auto_author', 'auto_author_field', 'owner_field', 'view_set',
    'container_path', 'permission_classes', 'serializer_fields', 'serializer_fields_exclude', 'empty_containers',
    'nested_fields', 'nested_fields_exclude', 'depth', 'anonymous_perms', 'authenticated_perms', 'owner_perms',
    'superuser_perms')
default_app_config = 'djangoldp.apps.DjangoldpConfig'
