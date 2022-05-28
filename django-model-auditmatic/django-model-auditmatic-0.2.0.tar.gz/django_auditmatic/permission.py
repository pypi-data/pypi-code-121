"""
    audit permission
"""
from typing import Optional

from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import Model


class PermissionSettings:
    """
    permission settings data object
    """

    def __init__(self):
        auditmatic_settings = settings.AUDITMATIC
        self.codename = "can_audit"
        self.name = "Can audit"
        permission = auditmatic_settings.get("permission")
        if not permission:
            return

        if permission_codename := permission.get("codename"):
            self.codename = permission_codename
        if permission_name := permission.get("name"):
            self.name = permission_name


permission_settings = PermissionSettings()


def get_audit_permission(model: Model) -> Optional[Permission]:
    """
        create an audit permission for the given model.
    :param model:
    :return:
    """
    content_type = ContentType.objects.get_for_model(model)
    print(content_type.id, content_type)
    lowered_model = model._meta.object_name.lower()
    try:
        return Permission.objects.get(
            codename=f"{permission_settings.codename}_{lowered_model}",
            name=f"{permission_settings.name} {lowered_model}",
            content_type=content_type,
        )
    except Permission.DoesNotExist as ex:
        print(ex)


def get_or_create_audit_permission(model: Model) -> Permission:
    """
        create an audit permission for the given model.
    :param model:
    :return:
    """
    content_type = ContentType.objects.get_for_model(model)
    lowered_model = model._meta.object_name.lower()
    obj, _ = Permission.objects.get_or_create(
        codename=f"{permission_settings.codename}_{lowered_model}",
        name=f"{permission_settings.name} {lowered_model}",
        content_type=content_type,
    )
    return obj
