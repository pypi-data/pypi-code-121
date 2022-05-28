"""
given steps
"""
from django.conf import settings
from django.contrib.auth.models import Group, User

from behave import given, use_step_matcher  # pylint: disable=E0611

from django_auditmatic.permission import get_or_create_audit_permission

use_step_matcher("parse")


@given("the user exists")
def user_exists(context):
    obj = User.objects.create_user(
        email="user@example.com", username="user", password="hellow", is_active=True
    )
    context.user = obj
    try:
        any_group = Group.objects.get(name="Any")
    except Group.DoesNotExist:
        any_group = Group.objects.create(name="Any")
    any_group.user_set.add(obj)
    assert context.user is not None


@given("the user model is configured with allow: any")
def user_model_configured_with_allow_any(context):
    """
    :type context: behave.runner.Context
    """
    settings.AUDITMATIC = {
        "apps": {
            "auth": {
                "User": {"allow": any},
            }
        }
    }


@given("the user model is configured")
def user_model_is_configured(context):
    """
    :type context: behave.runner.Context
    """
    settings.AUDITMATIC = {"apps": {"auth": {"User"}}}
    print(settings.AUDITMATIC)


@given("the user has the audit permission")
def user_has_audit_permission(context):
    """
    :type context: behave.runner.Context
    """
    permission = get_or_create_audit_permission(User)
    context.user.user_permissions.add(permission)


@given("the user does not have the audit permission")
def user_does_not_have_audit_permission(context):
    """
    :type context: behave.runner.Context
    """
    assert not context.user.has_perm("auth.can_audit_user")


@given("the audit name is {audit_name}")
def set_audit_name(context, audit_name: str):
    """
    :type context: behave.runner.Context
    :type audit_name: str
    """
    context.audit_name = audit_name


@given("the table name is {table_name}")
def set_table_name(context, table_name: str):
    """
    :type context: behave.runner.Context
    :type table_name: str
    """
    context.table_name = table_name
